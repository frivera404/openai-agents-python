import abc
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .spans import Span
    from .traces import Trace


class TracingProcessor(abc.ABC):
    """Interface for processing and monitoring traces and spans.

    Minimal ABC used by tracing implementations. Methods are intentionally thin and
    typed to -> None so they are safe to call from runtime code and simple to stub
    in tests.
    """

    @abc.abstractmethod
    def on_trace_start(self, trace: "Trace") -> None:
        """Called when a new trace begins execution."""
        ...

    @abc.abstractmethod
    def on_trace_end(self, trace: "Trace") -> None:
        """Called when a trace completes execution."""
        ...

    @abc.abstractmethod
    def on_span_start(self, span: "Span[Any]") -> None:
        """Called when a new span begins execution."""
        ...

    @abc.abstractmethod
    def on_span_end(self, span: "Span[Any]") -> None:
        """Called when a span completes execution."""
        ...

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Perform shutdown/cleanup tasks."""
        ...

    @abc.abstractmethod
    def force_flush(self) -> None:
        """Force processing of any queued traces/spans."""
        ...


class TracingExporter(abc.ABC):
    """Exports traces and spans to an external backend or sink."""

    @abc.abstractmethod
    def export(self, items: list["Trace | Span[Any]"]) -> None:
        """Export the given traces/spans."""
        ...
