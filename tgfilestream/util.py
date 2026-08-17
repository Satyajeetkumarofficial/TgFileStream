# tgfilestream - A Telegram bot that can stream Telegram files to users over HTTP.
# Copyright (C) 2019 Tulir Asokan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Tuple, Union

from telethon import events, utils
from telethon.tl.custom import Message
from telethon.tl.types import (
    TypeInputPeer, InputPeerChannel, InputPeerChat, InputPeerUser,
    PeerChat, PeerChannel,
)
from aiohttp import web

from .config import trust_headers

# Telegram user/chat/channel IDs can now use up to ~52 significant bits (they
# used to comfortably fit in 32 bits when this project was first written), so
# the packed ID needs enough room for the real (unmarked) chat id plus a
# generously sized message id.
chat_id_bits = 64
msg_id_bits = 32
chat_id_mask = (1 << chat_id_bits) - 1
msg_id_mask = (1 << msg_id_bits) - 1

type_user = 0b00
type_chat = 0b01
type_channel = 0b10
type_bits = 2
type_mask = (1 << type_bits) - 1

chat_id_offset = type_bits
msg_id_offset = chat_id_offset + chat_id_bits


def pack_id(evt: events.NewMessage.Event) -> int:
    # resolve_id turns the "marked" (sign-prefixed) chat id telethon exposes
    # back into the real, always-positive id used by the raw MTProto types.
    real_id, peer_type = utils.resolve_id(evt.chat_id)
    if peer_type is PeerChannel:
        kind = type_channel
    elif peer_type is PeerChat:
        kind = type_chat
    else:
        kind = type_user

    file_id = kind
    file_id |= (real_id & chat_id_mask) << chat_id_offset
    file_id |= (evt.id & msg_id_mask) << msg_id_offset
    return file_id


def unpack_id(file_id: int) -> Tuple[TypeInputPeer, int]:
    kind = file_id & type_mask
    chat_id = (file_id >> chat_id_offset) & chat_id_mask
    msg_id = (file_id >> msg_id_offset) & msg_id_mask
    if kind == type_channel:
        peer = InputPeerChannel(channel_id=chat_id, access_hash=0)
    elif kind == type_chat:
        peer = InputPeerChat(chat_id=chat_id)
    else:
        peer = InputPeerUser(user_id=chat_id, access_hash=0)
    return peer, msg_id


def get_file_name(message: Union[Message, events.NewMessage.Event]) -> str:
    if message.file.name:
        return message.file.name
    ext = message.file.ext or ""
    return f"{message.date.strftime('%Y-%m-%d_%H:%M:%S')}{ext}"


def get_requester_ip(req: web.Request) -> str:
    if trust_headers:
        try:
            return req.headers["X-Forwarded-For"]
        except KeyError:
            pass
    peername = req.transport.get_extra_info('peername')
    if peername is not None:
        return peername[0]
