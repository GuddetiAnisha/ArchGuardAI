from __future__ import annotations

from pathlib import Path

import yaml

from .models import Requirement


def load_catalogue(path: str | Path) -> tuple[dict, list[Requirement]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "requirements" not in data:
        raise ValueError("Requirement catalogue must contain a requirements list")
    requirements = [Requirement.model_validate(item) for item in data["requirements"]]
    ids = [item.id for item in requirements]
    if len(ids) != len(set(ids)):
        raise ValueError("Requirement IDs must be unique")
    return data.get("catalogue", {}), requirements
