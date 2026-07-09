"""Shared fixtures: paths to test data."""
from __future__ import annotations

from pathlib import Path

import pytest

DATA = Path(__file__).parent / "data"


@pytest.fixture
def genelist_path() -> Path:
    return DATA / "mini_genelist.tsv"


@pytest.fixture
def gff_path() -> Path:
    return DATA / "mini.gff3"


@pytest.fixture
def genome_path() -> Path:
    return DATA / "mini.len"
