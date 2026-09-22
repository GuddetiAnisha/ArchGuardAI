from pathlib import Path

from archguard.catalogue import load_catalogue


ROOT = Path(__file__).resolve().parents[1]


def test_catalogue_loads_unique_requirements():
    metadata, requirements = load_catalogue(ROOT / "requirements/synthetic_mars.yaml")
    assert metadata["version"] == "1.0"
    assert len(requirements) == 8
    assert len({item.id for item in requirements}) == len(requirements)
