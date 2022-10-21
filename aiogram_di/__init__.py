from __future__ import annotations

from asyncio import iscoroutine
from inspect import FullArgSpec
from typing import Any, Awaitable, Callable, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject

__all__ = [
    "DIMiddleware",
    "SyncDependencyResolverType",
    "AsyncDependencyResolverType",
    "DependencyResolverType",
]

SyncDependencyResolverType = Callable[[], Any]
AsyncDependencyResolverType = Callable[[], Awaitable[Any]]

DependencyResolverType = Union[SyncDependencyResolverType, AsyncDependencyResolverType]


class DIMiddleware(BaseMiddleware):
    def __init__(
        self,
        dependencies: dict[type, DependencyResolverType],
    ) -> None:
        self._dependencies = dependencies
        self._handlers_dependencies_resolvers: dict[
            int, dict[str, DependencyResolverType]
        ] = {}

    def _get_dependencies_resolvers(
        self,
        func_spec: FullArgSpec,
    ) -> dict[str, DependencyResolverType]:
        dependencies_resolvers: dict[str, DependencyResolverType] = {}

        for arg_name, arg_type in func_spec.annotations.items():
            if arg_name == "return":
                continue

            if arg_type in self._dependencies:
                dependencies_resolvers[arg_name] = self._dependencies[arg_type]

        return dependencies_resolvers

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        handler_obj: HandlerObject = handler.__wrapped__.__self__  # type: ignore
        handler_id = id(handler_obj)

        if handler_id not in self._handlers_dependencies_resolvers:
            self._handlers_dependencies_resolvers[
                handler_id
            ] = self._get_dependencies_resolvers(handler_obj.spec)

        for arg_name, resolver in self._handlers_dependencies_resolvers[
            handler_id
        ].items():
            value = resolver()

            if iscoroutine(value):
                data[arg_name] = await value
            else:
                data[arg_name] = value

        return await handler(event, data)
