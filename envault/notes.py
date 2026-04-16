"""Per-secret rich notes (multi-line text annotations)."""

from __future__ import annotations

NOTES_KEY = "__notes__"


def _load_notes(vault) -> dict:
    raw = vault.get(NOTES_KEY)
    if isinstance(raw, dict):
        return raw
    return {}


def _save_notes(vault, notes: dict) -> None:
    vault.set(NOTES_KEY, notes)
    vault.save()


def set_note(vault, key: str, text: str) -> None:
    """Set or replace the note for *key*."""
    notes = _load_notes(vault)
    notes[key] = text
    _save_notes(vault, notes)


def remove_note(vault, key: str) -> bool:
    """Remove the note for *key*. Returns True if a note existed."""
    notes = _load_notes(vault)
    if key in notes:
        del notes[key]
        _save_notes(vault, notes)
        return True
    return False


def get_note(vault, key: str) -> str | None:
    """Return the note text for *key*, or None."""
    return _load_notes(vault).get(key)


def list_notes(vault) -> dict[str, str]:
    """Return a mapping of key -> note text for all annotated secrets."""
    return dict(_load_notes(vault))
