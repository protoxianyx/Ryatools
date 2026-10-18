import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CanvasNode:
    """Represents a single node (card) on the canvas."""
    id: str
    node_type: str                  # 'text', 'file', 'link', or 'group'
    text: str | None = None        # Markdown content for 'text' nodes
    file: str | None = None        # Relative file path for 'file' nodes
    url: str | None = None         # Web address for 'link' nodes
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class CanvasEdge:
    """Represents a directional connection between two nodes."""
    id: str
    from_node: str                 # ID of source node
    to_node: str                   # ID of target node
    from_side: str | None = None   # 'top', 'right', 'bottom', 'left'
    to_side: str | None = None     # 'top', 'right', 'bottom', 'left'
    label: str | None = None       # Optional text label on the arrow


@dataclass
class CanvasData:
    """Container holding all parsed canvas elements."""
    nodes: dict[str, CanvasNode]   # Node ID -> CanvasNode for O(1) lookup
    edges: list[CanvasEdge]        # List of all edges


def parse_canvas(file_path: str | Path) -> CanvasData:
    """
    Parses an Obsidian .canvas file (JSON Canvas format) into structured dataclasses.
    
    Args:
        file_path: Path to the .canvas file.
        
    Returns:
        CanvasData containing parsed nodes dictionary and edges list.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If the file is not valid JSON or lacks canvas structure.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Canvas file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Invalid JSON in canvas file {path}: {err}") from err

    # 1. Parse nodes into a lookup dictionary
    nodes: dict[str, CanvasNode] = {}
    for raw_node in raw_data.get("nodes", []):
        node = CanvasNode(
            id=raw_node["id"],
            node_type=raw_node.get("type", "unknown"),
            text=raw_node.get("text"),
            file=raw_node.get("file"),
            url=raw_node.get("url"),
            x=raw_node.get("x", 0),
            y=raw_node.get("y", 0),
            width=raw_node.get("width", 0),
            height=raw_node.get("height", 0),
        )
        nodes[node.id] = node

    # 2. Parse edges
    edges: list[CanvasEdge] = []
    for raw_edge in raw_data.get("edges", []):
        edge = CanvasEdge(
            id=raw_edge["id"],
            from_node=raw_edge["fromNode"],
            to_node=raw_edge["toNode"],
            from_side=raw_edge.get("fromSide"),
            to_side=raw_edge.get("toSide"),
            label=raw_edge.get("label"),
        )
        edges.append(edge)

    return CanvasData(nodes=nodes, edges=edges)
