from typing import Annotated, List
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class SpecResult(TypedDict):
    company: str
    output_path: str
    status: str  # "updated" | "unchanged" | "error"
    error: str | None


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    results: List[SpecResult]
