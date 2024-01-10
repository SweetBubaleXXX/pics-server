import asyncio
from functools import wraps
from typing import Callable, ParamSpec, Type, TypeVar

from sqlalchemy.exc import NoResultFound

T = TypeVar("T")
P = ParamSpec("P")

InnerFunc = Callable[P, T]


def raises_on_not_found(
    exception: Type[Exception],
    *exc_args,
    **exc_kwargs,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except NoResultFound as exc:
                raise exception(*exc_args, **exc_kwargs) from exc

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except NoResultFound as exc:
                raise exception(*exc_args, **exc_kwargs) from exc

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
