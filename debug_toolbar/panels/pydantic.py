import inspect
import statistics
import typing as t
from collections import OrderedDict
from time import perf_counter

from fastapi import Request, Response
from pydantic import BaseModel
from pydantic.fields import ModelField

from debug_toolbar.panels import Panel
from debug_toolbar.types import ServerTiming, Stats
from debug_toolbar.utils import pluralize

if t.TYPE_CHECKING:
    from pydantic.fields import LocStr, ValidateReturn
    from pydantic.types import ModelOrDc

_validate = ModelField.validate


class PydanticPanel(Panel):
    title = "Pydantic"
    template = "panels/pydantic.html"

    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self._validation_time: float = 0
        self._parent_ids: t.Dict[t.Any, str] = {}
        self._validations: t.Dict[str, t.Any] = OrderedDict()

    @property
    def nav_subtitle(self) -> str:
        validation_count = len(self._validations)
        return (
            f"{validation_count} validation{pluralize(validation_count)}"
            f" in {self._validation_time:.2f}ms"
        )

    @property
    def validate(self) -> t.Callable[..., t.Any]:
        def decorator(
            field: ModelField,
            v: t.Any,
            values: t.Dict[str, t.Any],
            *,
            loc: "LocStr",
            cls: t.Optional["ModelOrDc"] = None,
        ) -> "ValidateReturn":
            parent_id = self._parent_ids.get(cls)
            field_id = str(id(field))

            if parent_id is not None:
                field_id = f"{parent_id}-{field_id}"
                self._validations[parent_id]["has_childs"] = True

            if field_id not in self._validations:
                self._validations[field_id] = {
                    "obj": field,
                    "ncalls": 1,
                    "durations": [],
                    "has_childs": False,
                    "class_name": cls.__name__ if cls else "",
                }
            else:
                self._validations[field_id]["ncalls"] += 1

            if (
                field.sub_fields is None
                and inspect.isclass(field.type_)
                and issubclass(field.type_, BaseModel)
            ):
                self._parent_ids[field.type_] = field_id

            start_time = perf_counter()
            result = _validate(field, v, values, loc=loc, cls=cls)
            duration = (perf_counter() - start_time) * 1000
            self._validations[field_id]["durations"].append(duration)

            if parent_id is None:
                self._validation_time += duration
            return result

        return decorator

    async def process_request(self, request: Request) -> Response:
        ModelField.validate = self.validate  # type: ignore[assignment]
        try:
            response = await super().process_request(request)
        finally:
            ModelField.validate = _validate  # type: ignore[assignment]
        return response

    async def generate_stats(self, request: Request, response: Response) -> Stats:
        return {
            "validation_time": self._validation_time,
            "validations": self._validations,
            "mean": statistics.mean,
        }

    async def generate_server_timing(
        self,
        request: Request,
        response: Response,
    ) -> ServerTiming:
        stats = self.get_stats()
        return [
            ("pydantic", "Pydantic validation time", stats.get("validation_time", 0)),
        ]
