"""Tests for envault.template."""

from __future__ import annotations

import pytest
from envault.template import render_template, RenderResult


# ---------------------------------------------------------------------------
# Minimal fake vault
# ---------------------------------------------------------------------------

class _FakeVault:
    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets

    def get(self, key: str, passphrase: str) -> str:  # noqa: ARG002
        if key not in self._secrets:
            raise KeyError(key)
        return self._secrets[key]


PASS = "irrelevant"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_render_single_placeholder():
    vault = _FakeVault({"DB_PASS": "s3cr3t"})
    result = render_template("password={{ DB_PASS }}", vault, PASS)
    assert result.rendered == "password=s3cr3t"
    assert result.resolved == ["DB_PASS"]
    assert result.missing == []
    assert result.ok is True


def test_render_multiple_placeholders():
    vault = _FakeVault({"HOST": "localhost", "PORT": "5432"})
    result = render_template("{{HOST}}:{{PORT}}", vault, PASS)
    assert result.rendered == "localhost:5432"
    assert set(result.resolved) == {"HOST", "PORT"}
    assert result.ok is True


def test_render_missing_key_leaves_placeholder():
    vault = _FakeVault({})
    result = render_template("value={{ MISSING }}", vault, PASS)
    assert "{{ MISSING }}" in result.rendered
    assert "MISSING" in result.missing
    assert result.ok is False


def test_render_partial_missing():
    vault = _FakeVault({"PRESENT": "yes"})
    result = render_template("{{ PRESENT }} and {{ ABSENT }}", vault, PASS)
    assert "yes" in result.rendered
    assert "{{ ABSENT }}" in result.rendered
    assert result.resolved == ["PRESENT"]
    assert result.missing == ["ABSENT"]


def test_render_no_placeholders():
    vault = _FakeVault({})
    text = "no substitutions here"
    result = render_template(text, vault, PASS)
    assert result.rendered == text
    assert result.resolved == []
    assert result.missing == []
    assert result.ok is True


def test_render_whitespace_variants():
    """Placeholders with varying internal whitespace should all resolve."""
    vault = _FakeVault({"KEY": "val"})
    for tmpl in ["{{KEY}}", "{{ KEY }}", "{{  KEY  }}"]:
        result = render_template(tmpl, vault, PASS)
        assert result.rendered == "val", f"Failed for template: {tmpl!r}"


def test_render_result_ok_property():
    vault = _FakeVault({"A": "1"})
    good = render_template("{{A}}", vault, PASS)
    bad = render_template("{{NOPE}}", vault, PASS)
    assert good.ok is True
    assert bad.ok is False
