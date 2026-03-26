from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from urllib.parse import urlencode
from uuid import UUID

import httpx
import jwt
from fastapi import status
from jwt import PyJWKClient

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.services.vault_service import VaultService


GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"


@lru_cache(maxsize=1)
def _google_jwk_client() -> PyJWKClient:
    return PyJWKClient(GOOGLE_JWKS_URL)


@dataclass(slots=True)
class GoogleIdentity:
    email: str
    full_name: str
    provider_subject: str


class OAuthService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.vault = VaultService()

    def build_google_authorize_url(
        self,
        *,
        redirect_uri: str | None,
        code_challenge: str,
        state: str,
    ) -> str:
        if not self.settings.google_client_id:
            raise AppError(
                code="CONFIG_ERROR",
                message="Google OAuth is not configured.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self._resolve_redirect_uri(redirect_uri),
            "response_type": "code",
            "scope": " ".join(self.settings.parsed_google_oauth_scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "include_granted_scopes": "true",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_google_code(
        self,
        *,
        code: str,
        code_verifier: str,
        redirect_uri: str | None,
    ) -> tuple[GoogleIdentity, dict]:
        if not self.settings.google_client_id or not self.settings.google_client_secret:
            raise AppError(
                code="CONFIG_ERROR",
                message="Google OAuth is not configured.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        resolved_redirect_uri = self._resolve_redirect_uri(redirect_uri)
        payload = {
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "code": code,
            "code_verifier": code_verifier,
            "grant_type": "authorization_code",
            "redirect_uri": resolved_redirect_uri,
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code >= 400:
            raise AppError(
                code="GOOGLE_OAUTH_EXCHANGE_FAILED",
                message="Unable to exchange Google OAuth code.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details=response.text,
            )

        token_data = response.json()
        id_token = token_data.get("id_token")
        if not id_token:
            raise AppError(
                code="GOOGLE_OAUTH_EXCHANGE_FAILED",
                message="Google OAuth response did not include an id_token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        claims = self._decode_google_id_token(id_token)
        email = claims.get("email")
        full_name = claims.get("name") or email
        provider_subject = claims.get("sub")
        if not email or not provider_subject:
            raise AppError(
                code="GOOGLE_IDENTITY_INVALID",
                message="Google identity payload was incomplete.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return (
            GoogleIdentity(email=email, full_name=full_name, provider_subject=provider_subject),
            token_data,
        )

    def store_google_tokens(self, user_id: UUID, token_data: dict) -> None:
        key = self.vault.oauth_key(str(user_id), "google")
        self.vault.put_json(
            key,
            {
                "provider": "google",
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "scope": token_data.get("scope"),
                "token_type": token_data.get("token_type"),
                "expires_in": token_data.get("expires_in"),
            },
        )

    def _resolve_redirect_uri(self, request_redirect_uri: str | None) -> str:
        configured = (self.settings.google_redirect_uri or "").strip()
        provided = (request_redirect_uri or "").strip()

        if configured:
            if provided and provided != configured:
                raise AppError(
                    code="GOOGLE_REDIRECT_URI_MISMATCH",
                    message="Google OAuth redirect URI does not match configured value.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            return configured

        if not provided:
            raise AppError(
                code="GOOGLE_REDIRECT_URI_MISSING",
                message="Google OAuth redirect URI is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return provided

    def _decode_google_id_token(self, id_token: str) -> dict:
        if not self.settings.google_client_id:
            raise AppError(
                code="CONFIG_ERROR",
                message="Google OAuth is not configured.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            signing_key = _google_jwk_client().get_signing_key_from_jwt(id_token).key
            return jwt.decode(
                id_token,
                signing_key,
                algorithms=["RS256"],
                audience=self.settings.google_client_id,
                issuer=["accounts.google.com", "https://accounts.google.com"],
            )
        except jwt.ExpiredSignatureError as exc:
            raise AppError(
                code="GOOGLE_IDENTITY_INVALID",
                message="Google identity token has expired.",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise AppError(
                code="GOOGLE_IDENTITY_INVALID",
                message="Google identity token could not be verified.",
                status_code=status.HTTP_400_BAD_REQUEST,
            ) from exc
