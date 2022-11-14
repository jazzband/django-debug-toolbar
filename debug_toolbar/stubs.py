from typing import Any, List, NamedTuple, Optional, Tuple, TypedDict

from django import template as dj_template


class InspectStack(NamedTuple):
    frame: Any
    filename: str
    lineno: int
    function: str
    code_context: str
    index: int


TidyStackTrace = List[Tuple[str, int, str, str, Optional[Any]]]


class DebugContext(TypedDict):
    num: int
    content: str
    highlight: bool


class TemplateContext(TypedDict):
    name: str
    context: List[DebugContext]


class RenderContext(dj_template.context.RenderContext):
    template: dj_template.Template


class RequestContext(dj_template.RequestContext):
    template: dj_template.Template
    render_context: RenderContext
