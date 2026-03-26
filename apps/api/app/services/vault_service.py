from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from app.core.config import get_settings


class VaultService:
    """Encrypted secret storage helper used as a local stand-in for Supabase Vault."""

    def __init__(self) -> None:
        settings = get_settings()
        self._path = Path(".local_vault.json")
        self._fernet = Fernet(self._build_key(settings.vault_encryption_key, settings.secret_key))

    def _build_key(self, explicit_key: str | None, fallback_secret: str) -> bytes:
        material = (explicit_key or fallback_secret).encode("utf-8")
        digest = hashlib.sha256(material).digest()
        return base64.urlsafe_b64encode(digest)

    def _load(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, str]) -> None:
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def put_json(self, key: str, value: dict[str, Any]) -> None:
        payload = self._load()
        encrypted = self._fernet.encrypt(json.dumps(value).encode("utf-8")).decode("utf-8")
        payload[key] = encrypted
        self._save(payload)

    def get_json(self, key: str) -> dict[str, Any] | None:
        payload = self._load()
        encrypted = payload.get(key)
        if encrypted is None:
            return None
        raw = self._fernet.decrypt(encrypted.encode("utf-8")).decode("utf-8")
        return json.loads(raw)

    def delete(self, key: str) -> None:
        payload = self._load()
        if key in payload:
            del payload[key]
            self._save(payload)

    def oauth_key(self, user_id: str, provider: str) -> str:
        return f"oauth:{provider}:{user_id}"
