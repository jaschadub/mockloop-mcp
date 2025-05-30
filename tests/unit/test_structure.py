"""Test to verify the new test structure works correctly."""

from pathlib import Path

import pytest


def test_fixtures_directory_exists():
    """Test that fixtures directory exists and is accessible."""
    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    assert fixtures_dir.exists()
    assert fixtures_dir.is_dir()


def test_test_spec_fixture_exists():
    """Test that test spec fixture exists."""
    test_spec_path = Path(__file__).parent.parent / "fixtures" / "test_spec.json"
    assert test_spec_path.exists()


def test_integration_directory_exists():
    """Test that integration directory exists."""
    integration_dir = Path(__file__).parent.parent / "integration"
    assert integration_dir.exists()
    assert integration_dir.is_dir()


def test_unit_directory_structure():
    """Test that unit directory has the expected structure."""
    unit_dir = Path(__file__).parent
    assert unit_dir.name == "unit"
    assert (unit_dir / "__init__.py").exists()


@pytest.mark.unit
def test_unit_marker():
    """Test that unit marker works."""
    assert True


if __name__ == "__main__":
    # Simple test runner for verification
    test_fixtures_directory_exists()
    test_test_spec_fixture_exists()
    test_integration_directory_exists()
    test_unit_directory_structure()
    test_unit_marker()
