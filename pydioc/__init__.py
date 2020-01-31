from typing import Any, Callable, Iterable, Tuple, Union

__version__ = "0.1"


class Container(object):
    """
    IoC container to automatic dependency orchestration, where order matters.
    """

    def __init__(self, *services: Tuple[str, Callable, Iterable[Union[str, Callable]]]):
        for service, implementation, *args in services:
            if not isinstance(implementation, type) and not callable(implementation):
                raise ValueError(
                    f"IoC: service '{service}' error: neither a class nor a function"
                )

            try:
                args = tuple(
                    [
                        self.__resolve(arg, idx)
                        for idx, arg in enumerate((args or [[]])[0])
                    ]
                )
                self.__dict__[self.__name(service)] = implementation(*args)
            except Exception as ex:
                raise RuntimeError(
                    f"IoC: service '{service}' error: {ex}"
                ).with_traceback(ex.__traceback__) from None

    @staticmethod
    def __name(service: str, revert: bool = False):
        if revert:
            return service.replace("[svc]", "", 1)

        return f"[svc]{service}"

    def __resolve(self, argument: Union[str, Callable], index: int):
        if callable(argument):
            try:
                return argument()
            except Exception as ex:
                raise RuntimeError(
                    f"failed to resolve argument #{index}: {ex}"
                ) from None

        assert isinstance(
            argument, str
        ), f"invalid type of argument #{index}: {type(argument).__qualname__}"

        try:
            return self.__dict__[self.__name(argument)]
        except KeyError:
            raise LookupError(f"service '{argument}' is not yet declared") from None

    def __getattr__(self, service: str):
        try:
            implementation = self.__dict__[self.__name(service)]
        except KeyError:
            raise LookupError(f"IoC: service '{service}' is not declared") from None

        if service.startswith("_"):
            raise RuntimeError(f"IoC: service '{service}' is not public") from None

        return implementation

    def __setattr__(self, service: str, value: Any):
        raise RuntimeError(f"IoC: service '{service}' is immutable")

    def __delattr__(self, service: str):
        raise RuntimeError(f"IoC: service '{service}' is immutable")

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    def __dir__(self):
        return sorted(set(dir(super()) + list(self)))

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter([self.__name(service, revert=True) for service in self.__dict__])

    def __repr__(self):
        return f"{self.__class__.__qualname__}({', '.join(self)})"


class ContextProxy(object):
    """
    Allows to work with request scoped object within compiled container.
    """

    def __init__(self):
        self.__context = None

    def __call__(self, context: object):
        self.__context = context

    def __getattr__(self, attribute: str):
        if not self.__context:
            raise RuntimeError("context is not yet set")

        if not hasattr(self.__context, attribute):
            raise LookupError(f"context does not have '{attribute}' attribute")

        return getattr(self.__context, attribute)
