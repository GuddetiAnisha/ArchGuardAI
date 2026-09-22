from __future__ import annotations

import json
import re
from pathlib import Path

MAX_DOCUMENT_CHARACTERS = 500_000


def normalize(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_document(path: str | Path) -> str:
    path = Path(path)
    if path.stat().st_size > MAX_DOCUMENT_CHARACTERS * 4:
        raise ValueError("Document exceeds the configured size limit")
    suffix = path.suffix.lower()
    if suffix in {".md", ".txt", ".mmd", ".mermaid"}:
        text = path.read_text(encoding="utf-8")
    elif suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        text = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        raise ValueError("Supported formats are .md, .txt, .json, .mmd, and .mermaid")
    if len(text) > MAX_DOCUMENT_CHARACTERS:
        raise ValueError("Document exceeds the configured character limit")
    return normalize(text)


def split_passages(text: str, max_chars: int = 1200) -> list[tuple[int, int, str]]:
    paragraphs = [match for match in re.finditer(r"[^\n]+(?:\n|$)", text)]
    passages, current, start = [], "", 0
    for match in paragraphs:
        piece = match.group(0).strip()
        if not piece:
            continue
        if current and len(current) + len(piece) + 1 > max_chars:
            passages.append((start, start + len(current), current))
            current, start = piece, match.start()
        else:
            if not current:
                start = match.start()
            current = f"{current}\n{piece}".strip()
    if current:
        passages.append((start, start + len(current), current))
    return passages or [(0, len(text), text)]
