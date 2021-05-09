"""Packet gives specification classes of server communication."""

from ._message import MsgArgsType, MessageSpec, Message
from . import app, servererror, entity
from .app import MessageSpec, MsgArgsType
from ._deftype import TYPE_SPEC_BY_ID
