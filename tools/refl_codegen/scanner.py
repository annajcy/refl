from __future__ import annotations

from pathlib import Path

from .constants import REFL_IGNORE_MARKER, REFL_TYPE_MARKER
from .errors import CodegenError
from .io_utils import get_source_lines
from .models import Ancestor, ReflectedField, ReflectedType, SourceLocation
from .paths import resolve_path


def extract_file(node: dict) -> str | None:
    for key in ("loc", "range"):
        value = node.get(key, {})
        if key == "range":
            for nested in ("begin", "end"):
                candidate = value.get(nested, {})
                if candidate.get("file"):
                    return candidate["file"]
        elif value.get("file"):
            return value["file"]
    return None


def get_line_col(node: dict, inherited_file: Path | None, which: str) -> SourceLocation | None:
    payload = node.get(which, {})
    if which == "range":
        payload = payload.get("begin", {})

    file_value = payload.get("file")
    path = resolve_path(file_value, Path.cwd()) if file_value else inherited_file
    line = payload.get("line")
    col = payload.get("col")
    if path is None or line is None or col is None:
        return None
    return SourceLocation(path, int(line), int(col))


def source_span(
    lines: list[str],
    begin_line: int,
    begin_col: int,
    end_line: int,
    end_col_exclusive: int,
) -> str:
    if begin_line > end_line:
        return ""

    collected: list[str] = []
    for line_number in range(begin_line, end_line + 1):
        line = lines[line_number - 1]
        start_index = max(begin_col - 1, 0) if line_number == begin_line else 0
        stop_index = max(end_col_exclusive, 0) if line_number == end_line else len(line)
        collected.append(line[start_index:stop_index])
    return "".join(collected)


def decl_prefix_contains_marker(
    node: dict,
    current_file: Path,
    sources: dict[Path, list[str]],
    marker: str,
) -> bool:
    for child in node.get("inner", []):
        if child.get("kind") != "AnnotateAttr":
            continue

        begin = child.get("range", {}).get("begin", {})
        expansion = begin.get("expansionLoc")
        if expansion:
            file_value = expansion.get("file")
            if not file_value:
                continue
            expansion_file = resolve_path(file_value, Path.cwd())
            lines = get_source_lines(expansion_file, sources)
            if lines is None:
                continue
            line = expansion.get("line")
            col = expansion.get("col")
            tok_len = expansion.get("tokLen")
            if line is None or col is None or tok_len is None:
                continue
            snippet = source_span(lines, int(line), int(col), int(line), int(col) - 1 + int(tok_len))
            if snippet == marker:
                return True

    lines = get_source_lines(current_file, sources)
    if lines is None:
        return False

    range_begin = get_line_col(node, current_file, "range")
    loc = get_line_col(node, current_file, "loc")
    if range_begin and loc:
        snippet = source_span(
            lines,
            range_begin.line,
            range_begin.col,
            loc.line,
            loc.col - 1,
        )
        if marker in snippet:
            return True

    range_info = node.get("range", {})
    begin = range_info.get("begin", {})
    end = range_info.get("end", {})
    if "line" in begin and "col" in begin and "line" in end and "col" in end:
        snippet = source_span(
            lines,
            int(begin["line"]),
            int(begin["col"]),
            int(end["line"]),
            int(end["col"]),
        )
        return marker in snippet
    return False


def format_location(location: SourceLocation) -> str:
    return f"{location.file}:{location.line}:{location.col}"


def require_supported(condition: bool, location: SourceLocation, message: str) -> None:
    if not condition:
        raise CodegenError(f"{format_location(location)}: {message}")


def qualified_name(node: dict, ancestors: list[Ancestor]) -> str:
    namespace_parts = [ancestor.name for ancestor in ancestors if ancestor.kind == "NamespaceDecl" and ancestor.name]
    return "::".join([*namespace_parts, node["name"]])


def first_annotation_expansion_location(node: dict) -> SourceLocation | None:
    for child in node.get("inner", []):
        if child.get("kind") != "AnnotateAttr":
            continue
        begin = child.get("range", {}).get("begin", {}).get("expansionLoc")
        if not begin:
            continue
        file_value = begin.get("file")
        line = begin.get("line")
        col = begin.get("col")
        if file_value is None or line is None or col is None:
            continue
        return SourceLocation(
            file=resolve_path(file_value, Path.cwd()),
            line=int(line),
            col=int(col),
        )
    return None


def has_unsupported_ancestor(ancestors: list[Ancestor], location: SourceLocation) -> None:
    local_scope_kinds = {"FunctionDecl", "CXXMethodDecl", "CXXConstructorDecl", "CXXDestructorDecl", "LambdaExpr"}
    require_supported(
        all(ancestor.kind not in local_scope_kinds for ancestor in ancestors),
        location,
        "local types are not supported by refl_codegen v1",
    )
    require_supported(
        all(ancestor.kind not in {"CXXRecordDecl", "RecordDecl"} for ancestor in ancestors),
        location,
        "nested types are not supported by refl_codegen v1",
    )
    require_supported(
        all(not ancestor.kind.endswith("TemplateDecl") for ancestor in ancestors),
        location,
        "template types are not supported by refl_codegen v1",
    )


def collect_fields(
    node: dict,
    current_file: Path,
    sources: dict[Path, list[str]],
    location: SourceLocation,
) -> tuple[ReflectedField, ...]:
    fields: list[ReflectedField] = []

    for child in node.get("inner", []):
        if child.get("kind") != "FieldDecl":
            continue

        if decl_prefix_contains_marker(child, current_file, sources, REFL_IGNORE_MARKER):
            continue

        field_location = get_line_col(child, current_file, "loc") or location
        access = child.get("access", "public")
        require_supported(
            access == "public",
            field_location,
            "private/protected fields must be removed or marked with REFL_IGNORE",
        )
        require_supported(
            not child.get("isBitfield", False),
            field_location,
            "bit-fields are not supported by refl_codegen v1",
        )

        field_name = child.get("name")
        require_supported(field_name is not None, field_location, "anonymous fields are not supported by refl_codegen v1")
        fields.append(ReflectedField(field_name))

    return tuple(fields)


def maybe_collect_type(
    node: dict,
    ancestors: list[Ancestor],
    current_file: Path | None,
    sources: dict[Path, list[str]],
) -> ReflectedType | None:
    if current_file is None:
        return None
    if not decl_prefix_contains_marker(node, current_file, sources, REFL_TYPE_MARKER):
        return None

    location = get_line_col(node, current_file, "loc") or get_line_col(node, current_file, "range")
    if location is None:
        raise CodegenError(f"{current_file}: unable to determine declaration location for marked type")

    has_unsupported_ancestor(ancestors, location)

    name = node.get("name")
    require_supported(name is not None, location, "anonymous types are not supported by refl_codegen v1")
    require_supported(
        node.get("tagUsed") in {"struct", "class"},
        location,
        "only struct/class declarations are supported by refl_codegen v1",
    )
    require_supported(
        not any(child.get("kind") == "CXXBaseSpecifier" for child in node.get("inner", [])),
        location,
        "inheritance is not supported by refl_codegen v1",
    )
    require_supported(
        not any(child.get("kind", "").endswith("TemplateParmDecl") for child in node.get("inner", [])),
        location,
        "template types are not supported by refl_codegen v1",
    )

    return ReflectedType(
        qualified_name=qualified_name(node, ancestors),
        source=location,
        fields=collect_fields(node, current_file, sources, location),
    )


def walk_ast(
    node: dict,
    ancestors: list[Ancestor],
    inherited_file: Path | None,
    sources: dict[Path, list[str]],
    collected: dict[tuple[Path, int, int, str], ReflectedType],
) -> None:
    current_file = inherited_file
    explicit_file = extract_file(node)
    if explicit_file:
        current_file = resolve_path(explicit_file, Path.cwd())
    else:
        annotation_loc = first_annotation_expansion_location(node)
        if annotation_loc is not None:
            current_file = annotation_loc.file

    kind = node.get("kind")
    if kind in {"CXXRecordDecl", "RecordDecl"} and node.get("completeDefinition", False):
        reflected = maybe_collect_type(node, ancestors, current_file, sources)
        if reflected is not None:
            key = (
                reflected.source.file,
                reflected.source.line,
                reflected.source.col,
                reflected.qualified_name,
            )
            collected[key] = reflected

    next_ancestors = ancestors + [Ancestor(kind=kind or "", name=node.get("name"), file=current_file)]
    for child in node.get("inner", []):
        walk_ast(child, next_ancestors, current_file, sources, collected)
