"""Чтение pcap-файла в режиме online."""

import asyncio
import hashlib
import logging
import os
import shlex
from asyncio import CancelledError, Event, Task, create_subprocess_exec
from asyncio.subprocess import PIPE, Process
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from ipaddress import IPv4Address
from pathlib import Path
from typing import Self, TypeAlias

import dateutil.parser

logger = logging.getLogger(__name__)


Port: TypeAlias = int


@dataclass
class NetChunkData:
    """Представление чанка данных из pcap-файла.

    Данные из чанка имеет начальный формат:
    Sep 19, 2025 19:03:05.867275000 +05|172.18.0.11|172.18.0.11|38048|32969|0900
    """

    time: datetime
    src: IPv4Address
    dst: IPv4Address
    tcp_src_port: Port
    tcp_dst_port: Port
    udp_src_port: Port
    udp_dst_port: Port
    data: str


class Pcap2StreamNotStartedError(Exception):
    """Ошибка, если чтец pcap-файла не запущен."""


class Pcap2Stream:
    """Чтение pcap-файла в режиме online."""

    # Команда tshark читает данные из именованного канала
    _TSHARK_CMD_TEMLATE = (
        "tshark -r {fifo} -Y '(tcp or udp) and not "
        "(arp or ssdp or dns or ip.addr == 127.0.0.11 or mdns or icmpv6)' "
        "-T fields -e frame.time -e ip.src -e ip.dst -e tcp.srcport "
        "-e tcp.dstport -e udp.srcport -e udp.dstport -e data -E separator=| "
        "-E occurrence=f"
    )

    # Команда, всё время читает из pcap-файла данные (для отправки в
    # именованный канал)
    _TAIL_PCAP_CMD_TEMPLATE = "tail -f -c +0 {pcap_path}"

    # Папка с именованными каналами
    _FIFO_DIR = Path("/tmp/enki/msgreader/fifos")  # noqa: S108

    def __init__(self, pcap_path: Path) -> None:
        """Конструктор."""
        self._pcap_path = pcap_path

        # Именнованный канал, из которого будет читать TShark и в который будет
        # записывать tail
        self._FIFO_DIR.mkdir(parents=True, exist_ok=True)
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

    async def _run_tail_proc(self) -> None:
        """Запустить дочерний процесс с tail."""
        assert self._pipe_path.exists()
        assert self._pipe_path.is_fifo()
        self._tail_proc = await create_subprocess_exec(
            *self._tail_cmd, stdout=self._pipe_path.open("bw")
        )

    def _create_fifo(self) -> None:
        if self._pipe_path.exists():
            self._pipe_path.unlink()
        os.mkfifo(self._pipe_path)

    async def _run_thark_proc(self) -> None:
        self._tshark_proc = await create_subprocess_exec(
            *self._tshark_cmd,
            stdout=PIPE,
            stderr=PIPE,
        )

    async def _read_tshark_stdin(self) -> None:
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
                    dt_str,
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

            if not src_ip or not dst_ip or not hex_data:
                logger.warning(
                    "[%s] The chunk has no some fields (line = '%s')", self, line
                )
                continue

            dt = dateutil.parser.parse(dt_str, ignoretz=True)
            net_chunk_data = NetChunkData(
                dt,
                IPv4Address(src_ip),
                IPv4Address(dst_ip),
                Port(tcp_src_port) if tcp_src_port else Port(-1),
                Port(tcp_dst_port) if tcp_dst_port else Port(-1),
                Port(udp_src_port) if udp_src_port else Port(-1),
                Port(udp_dst_port) if udp_dst_port else Port(-1),
                hex_data.strip(),
            )
            self._new_line_event.set()
            self._net_chunks_data.append(net_chunk_data)

        self._new_line_event.set()

    @property
    def is_started(self) -> bool:
        return False

    async def start(self) -> None:
        self._create_fifo()

        await self._run_thark_proc()
        self._read_tshark_stdin_task = asyncio.create_task(
            self._read_tshark_stdin()
        )

        await self._run_tail_proc()

        self._started = True

    async def stop(self) -> None:
        if not self._started:
            logger.warning("[%s] The object is already stopped", self)

        self._started = False

        # Остановить запись tail в pipe
        if self._tail_proc is not None:
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
        if self._tshark_proc is not None:
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

    def __aiter__(self) -> Self:
        if not self._started:
            msg = "Start the object at first"
            raise Pcap2StreamNotStartedError(msg)
        return self

    async def __anext__(self) -> NetChunkData:
        if self._tshark_proc is None or self._tshark_proc.returncode is not None:
            logger.debug(
                "[%s] The tshark process is returned (ret code = %s). Stop iteration",
                self,
                -1 if self._tshark_proc is None else self._tshark_proc.returncode,
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
