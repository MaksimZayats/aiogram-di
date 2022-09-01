from asyncio import iscoroutine
from inspect import FullArgSpec
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram import BaseMiddleware
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import TelegramObject

__all__ = ["DIMiddleware"]


class DIMiddleware(BaseMiddleware):
    def __init__(
        self,
        dependencies: Dict[type, Union[Callable[[], Any], Callable[[], Awaitable[Any]]]],
    ) -> None:
        self._dependencies = dependencies

    def _get_dependencies_resolvers(
        self,
        func_spec: FullArgSpec,
    ) -> Dict[str, Callable[[], Any]]:
        dependencies_resolvers = {}

        for arg_name, arg_type in func_spec.annotations.items():
            if arg_name == "return":
                continue

            if arg_type in self._dependencies:
                dependencies_resolvers[arg_name] = self._dependencies[arg_type]

        return dependencies_resolvers

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        handler_obj: HandlerObject = handler.__wrapped__.__self__  # type: ignore

        if not hasattr(handler_obj, "dependencies_resolvers"):
            setattr(
                handler_obj,
                "dependencies_resolvers",
                self._get_dependencies_resolvers(
                    handler_obj.spec,
                ),
            )

        dependencies_resolvers: Dict[
            str, Union[Callable[[], Any], Callable[[], Awaitable[Any]]]
        ] = getattr(handler_obj, "dependencies_resolvers")

        for arg_name, resolver_function in dependencies_resolvers.items():
            dependant = resolver_function()

            if iscoroutine(dependant):
                data[arg_name] = await dependant
            else:
                data[arg_name] = dependant

        return await handler(event, data)
