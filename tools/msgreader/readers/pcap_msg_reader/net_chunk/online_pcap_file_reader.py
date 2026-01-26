"""Чтение pcap-файла в режиме online."""

import asyncio
import datetime
import hashlib
import logging
import os
import shlex
from asyncio import CancelledError, Event, Future, Task, create_subprocess_exec
from asyncio.subprocess import PIPE, Process
from collections import deque
from ipaddress import IPv4Address
from pathlib import Path
from typing import Self

from enki.misc import devonly

from .net_chunk import (
    NetChunkData,
    PortValue,
)

logger = logging.getLogger(__name__)


class Pcap2StreamNotStartedError(Exception):
    """Ошибка, если чтец pcap-файла не запущен."""


class OnlinePcapFileReader:
    """Чтение pcap-файла в режиме online."""

    # Команда tshark читает данные из именованного канала
    _TSHARK_CMD_TEMLATE = (
        "tshark -r {fifo} -Y '(tcp or udp) and not "
        "(arp or ssdp or dns or ip.addr == 127.0.0.11 or mdns or icmpv6)' "
        "-T fields -e frame.time_epoch -e ip.src -e ip.dst -e tcp.srcport "
        "-e tcp.dstport -e udp.srcport -e udp.dstport -e data -E separator=| "
        "-E occurrence=f"
    )

    # Команда, всё время читает из pcap-файла данные (для отправки в
    # именованный канал)
    _TAIL_PCAP_CMD_TEMPLATE = 'tail -f -c +0 "{pcap_path}"'

    # Папка с именованными каналами
    _FIFO_DIR = Path("/tmp/enki/msgreader/fifos")  # noqa: S108

    def __init__(self, pcap_path: Path) -> None:
        """Конструктор.

        Args:
            pcap_path (Path): путь до pcap-файла с KBEngine-сообщениями

        """
        self._pcap_path = pcap_path

        # Именнованный канал, из которого будет читать TShark и в который будет
        # записывать tail
        self._pipe_path = (
            self._FIFO_DIR
            / f"{pcap_path.name}-{hashlib.md5(str(pcap_path.parent).encode()).hexdigest()}"  # noqa: S324
        )

        # Shell команды с подпроцессами TShark и tail
        self._tshark_cmd = shlex.split(
            self._TSHARK_CMD_TEMLATE.format(fifo=self._pipe_path)
        )
        self._tail_cmd = shlex.split(
            self._TAIL_PCAP_CMD_TEMPLATE.format(pcap_path=self._pcap_path)
        )
        self._tail_proc: Process | None = None
        self._tshark_proc: Process | None = None

        # Событие о получении новой строки из дочернего процесса с TShark
        self._new_line_event = Event()
        # Данные от TShark
        self._net_chunks_data: deque[NetChunkData] = deque()
        self._read_tshark_stdin_task: Task | None = None

        self._started = False

        self._is_finilized_future: Future[None] = Future()

    async def _run_tail_proc(self) -> None:
        """Запустить дочерний процесс с tail."""
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert self._pipe_path.exists()
        assert self._pipe_path.is_fifo()

        logger.debug("[%s] Create the 'tail' process", self)
        self._tail_proc = await create_subprocess_exec(
            *self._tail_cmd,
            stdout=self._pipe_path.open("bw"),
            preexec_fn=os.setpgrp,
        )
        logger.debug("[%s] The 'tail' process is created", self)

    def _create_fifo(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._FIFO_DIR.mkdir(parents=True, exist_ok=True)
        if self._pipe_path.exists():
            self._pipe_path.unlink()
        os.mkfifo(self._pipe_path)

    async def _run_thark_proc(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())

        logger.debug("[%s] Create the 'tshark' process", self)
        self._tshark_proc = await create_subprocess_exec(
            *self._tshark_cmd, stdout=PIPE, stderr=PIPE, preexec_fn=os.setpgrp
        )
        logger.debug("[%s] The 'tshark' process is created", self)

    async def _read_tshark_stdin(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        assert self._tshark_proc is not None
        assert self._tshark_proc.stdout is not None

        while self._tshark_proc.returncode is None:
            try:
                b_line = await self._tshark_proc.stdout.readline()
            except CancelledError:
                logger.debug(
                    "[%s] The task canceled. Stop reading from stdout", self
                )
                break

            if not b_line:
                logger.debug("[%s] No lines from stdout. Stop reading", self)
                break

            line = b_line.decode()

            try:
                (
                    dt_epoch_str,
                    src_ip,
                    dst_ip,
                    tcp_src_port,
                    tcp_dst_port,
                    udp_src_port,
                    udp_dst_port,
                    hex_data,
                ) = line.split("|")
            except ValueError as err:
                logger.error(
                    "[%s] The line has invalid format (err = %s)", self, err
                )
                break

            # У мне не получилось отфильтровать пустые пакеты по frame.len > 0
            # или tcp.len > 0. Всё равно пакет ловится и в нём данные '\n'.
            if not hex_data.strip():
                continue

            if not src_ip or not dst_ip:
                logger.warning(
                    "[%s] The chunk has no some fields (line = '%s')",
                    self,
                    line,
                )
                continue

            dt = datetime.datetime.fromtimestamp(
                float(dt_epoch_str), datetime.timezone.utc
            )
            net_chunk_data = NetChunkData(
                dt,
                IPv4Address(src_ip),
                IPv4Address(dst_ip),
                PortValue(int(tcp_src_port)) if tcp_src_port else PortValue(-1),
                PortValue(int(tcp_dst_port)) if tcp_dst_port else PortValue(-1),
                PortValue(int(udp_src_port)) if udp_src_port else PortValue(-1),
                PortValue(int(udp_dst_port)) if udp_dst_port else PortValue(-1),
                hex_data.strip(),
            )
            self._new_line_event.set()
            self._net_chunks_data.append(net_chunk_data)
            logger.debug("[%s] A new net chunk added", self)

        self._new_line_event.set()
        logger.debug("[%s] TShark stdout reading stopped", self)

    async def wait_until_stop(self) -> None:
        if not self._started:
            raise Pcap2StreamNotStartedError

        await self._is_finilized_future

    @property
    def is_started(self) -> bool:
        return self._started

    async def start(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        self._create_fifo()

        await self._run_thark_proc()

        await self._run_tail_proc()

        self._read_tshark_stdin_task = asyncio.create_task(
            self._read_tshark_stdin()
        )

        self._started = True
        logger.debug("[%s] Started", self)

    async def stop(self) -> None:
        logger.debug("[%s] %s", self, devonly.func_args_values())
        if not self._started:
            logger.warning("[%s] The object is already stopped", self)

        # Остановить запись tail в pipe
        if self._tail_proc is not None and self._tail_proc.returncode is None:
            self._tail_proc.terminate()

            try:
                await asyncio.wait_for(self._tail_proc.wait(), timeout=1)
            except asyncio.TimeoutError:
                assert self._tail_proc is not None
                if self._tail_proc.returncode is None:
                    self._tail_proc.kill()
                    await self._tail_proc.wait()

            self._tail_proc = None

        # Остановить чтение tshark из pipe
        if (
            self._tshark_proc is not None
            and self._tshark_proc.returncode is None
        ):
            self._tshark_proc.terminate()
            try:
                await asyncio.wait_for(self._tshark_proc.wait(), timeout=1)
            except asyncio.TimeoutError:
                assert self._tshark_proc is not None
                if self._tshark_proc.returncode is None:
                    self._tshark_proc.kill()
                    await self._tshark_proc.wait()

        if self._read_tshark_stdin_task is not None:
            await self._read_tshark_stdin_task
        self._read_tshark_stdin_task = None
        self._tshark_proc = None

        # Удалить pipe
        if self._pipe_path.exists():
            self._pipe_path.unlink()

        self._is_finilized_future.set_result(None)

    def __aiter__(self) -> Self:
        if not self._started:
            msg = "Start the object at first"
            raise Pcap2StreamNotStartedError(msg)
        return self

    async def __anext__(self) -> NetChunkData:
        if (
            self._tshark_proc is None
            or self._tshark_proc.returncode is not None
        ):
            logger.debug(
                "[%s] The tshark process is returned (ret code = %s). Stop iteration",
                self,
                (
                    -1
                    if self._tshark_proc is None
                    else self._tshark_proc.returncode
                ),
            )
            raise StopAsyncIteration

        if self._net_chunks_data:
            return self._net_chunks_data.popleft()

        # Все ответы обработаны. Очищаем событие
        self._new_line_event.clear()

        try:
            # Ожидаем, когда придут новые данные
            await self._new_line_event.wait()
        except CancelledError as err:
            logger.info(
                "[%s] No response. Waiting was canceled",
                self,
            )
            raise StopAsyncIteration from err

        return await self.__anext__()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self._pcap_path.name})"
