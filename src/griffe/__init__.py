from __future__ import annotations

from dataclasses import dataclass
from typing import List


class DocstringSectionKind:
    text = "text"
    parameters = "parameters"


@dataclass
class _Parameter:
    name: str
    description: str


@dataclass
class _Section:
    kind: str
    value: object


class Docstring:
    def __init__(self, text: str, lineno: int | None = None, parser: str | None = None) -> None:
        self.text = text
        self.lineno = lineno
        self.parser = parser

    def parse(self) -> List[_Section]:
        sections: List[_Section] = []
        lines = [line.strip() for line in self.text.strip().splitlines()]
        description_parts: List[str] = []
        params: List[_Parameter] = []
        current = None
        for line in lines:
            if not line:
                continue
            upper = line.rstrip(":")
            if line in {"Args:", "Arguments:"}:
                current = "params"
                continue
            if line in {"Returns:", "Yields:", "Raises:"}:
                current = None
                continue
            if current == "params":
                if ":" in line:
                    name, desc = line.split(":", 1)
                    params.append(_Parameter(name=name.strip(), description=desc.strip()))
                continue
            description_parts.append(line)
        if description_parts:
            sections.append(_Section(DocstringSectionKind.text, " ".join(description_parts)))
        if params:
            sections.append(_Section(DocstringSectionKind.parameters, params))
        return sections


__all__ = ["Docstring", "DocstringSectionKind"]
