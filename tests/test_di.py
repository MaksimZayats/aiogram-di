from dataclasses import dataclass
from datetime import datetime

import pytest
from aiogram import Dispatcher
from aiogram.types import Chat, Message

from aiogram_di import DIMiddleware


@dataclass
class A:
    id: int


@dataclass
class B:
    id: int


def get_a() -> A:
    return A(id=123)


async def get_b() -> B:
    return B(id=456)


dp = Dispatcher()
dp.message.middleware(
    DIMiddleware(
        {
            A: get_a,
            B: get_b,
        }
    )
)


@dp.message()
async def handler(
    _: Message,
    a: A,
    b: B,
) -> None:
    assert a.id == 123
    assert b.id == 456


@pytest.mark.asyncio
async def test_di():
    await dp.message.trigger(
        Message(message_id=0, date=datetime.now(), chat=Chat(id=0, type=""))
    )
    await dp.message.trigger(
        Message(message_id=0, date=datetime.now(), chat=Chat(id=0, type=""))
    )
