from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any
from uuid import uuid4

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt import PyJWKClient

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.redis_client import get_redis_client


@dataclass(slots=True)
class TokenBundle:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


@dataclass(slots=True)
class TokenPayload:
    sub: str
    email: str | None
    name: str | None
    role: str
    exp: int
    jti: str


@lru_cache(maxsize=1)
def _generate_dev_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


class TokenService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.redis = get_redis_client()

        if self.settings.jwt_private_key and self.settings.jwt_public_key:
            self.private_key = self.settings.jwt_private_key
            self.public_key = self.settings.jwt_public_key
        else:
            self.private_key, self.public_key = _generate_dev_keypair()

        self.supabase_jwk_client = (
            PyJWKClient(self.settings.supabase_jwks_url)
            if self.settings.supabase_jwks_url
            else None
        )

    async def issue_tokens(
        self,
        *,
        user_id: str,
        email: str,
        name: str,
        role: str,
        session_id: str | None = None,
    ) -> TokenBundle:
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(seconds=self.settings.access_token_expire_seconds)
        access_jti = f"atk_{uuid4().hex}"
        session_identifier = session_id or f"sess_{uuid4().hex}"
        access_token = jwt.encode(
            {
                "sub": user_id,
                "email": email,
                "name": name,
                "role": role,
                "iat": int(issued_at.timestamp()),
                "exp": int(expires_at.timestamp()),
                "iss": self.settings.jwt_issuer,
                "aud": self.settings.jwt_audience,
                "jti": access_jti,
            },
            self.private_key,
            algorithm="RS256",
            headers={"kid": "local-dev-key"},
        )

        refresh_token = secrets.token_urlsafe(48)
        await self._store_refresh_token(
            refresh_token=refresh_token,
            payload={
                "user_id": user_id,
                "email": email,
                "name": name,
                "role": role,
                "session_id": session_identifier,
            },
        )

        return TokenBundle(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.access_token_expire_seconds,
        )

    async def rotate_refresh_token(self, refresh_token: str) -> tuple[str, TokenBundle]:
        payload = await self._load_refresh_token(refresh_token)
        await self.revoke_refresh_token(refresh_token)
        bundle = await self.issue_tokens(
            user_id=payload["user_id"],
            email=payload["email"],
            name=payload["name"],
            role=payload["role"],
            session_id=payload.get("session_id"),
        )
        return payload["user_id"], bundle

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        hashed = self._hash_token(refresh_token)
        raw = await self.redis.get(f"auth:refresh:{hashed}")
        if raw is None:
            return
        payload = json.loads(raw)
        ttl = self.settings.refresh_token_expire_days * 86400
        await self.redis.setex(
            f"auth:refresh_used:{hashed}",
            ttl,
            json.dumps(
                {
                    "user_id": payload.get("user_id"),
                    "session_id": payload.get("session_id"),
                }
            ),
        )
        await self.redis.delete(f"auth:refresh:{hashed}")
        await self.redis.srem(f"auth:user_refresh:{payload['user_id']}", hashed)

    async def revoke_all_refresh_tokens_for_user(self, user_id: str) -> None:
        member_key = f"auth:user_refresh:{user_id}"
        token_hashes = await self.redis.smembers(member_key)
        if token_hashes:
            keys = [f"auth:refresh:{token_hash}" for token_hash in token_hashes]
            await self.redis.delete(*keys)
        await self.redis.delete(member_key)

    async def decode_access_token(self, token: str) -> TokenPayload:
        decode_errors: list[Exception] = []
        decoded: dict[str, Any] | None = None

        try:
            decoded = jwt.decode(
                token,
                self.public_key,
                algorithms=["RS256"],
                issuer=self.settings.jwt_issuer,
                audience=self.settings.jwt_audience,
            )
        except Exception as exc:  # noqa: BLE001
            decode_errors.append(exc)
            decoded = await self._decode_supabase_token(token)

        if decoded is None:
            if any(isinstance(exc, jwt.ExpiredSignatureError) for exc in decode_errors):
                raise AppError(
                    code="AUTH_TOKEN_EXPIRED",
                    message="Your authentication token has expired. Please log in again.",
                    status_code=401,
                )
            raise AppError(
                code="AUTH_TOKEN_INVALID",
                message="The provided authentication token is invalid.",
                status_code=401,
            )

        payload = TokenPayload(
            sub=str(decoded["sub"]),
            email=decoded.get("email"),
            name=decoded.get("name"),
            role=decoded.get("role", "user"),
            exp=int(decoded["exp"]),
            jti=str(decoded.get("jti", f"legacy_{hashlib.sha256(token.encode('utf-8')).hexdigest()}")),
        )

        is_revoked = await self.redis.exists(f"auth:revoked:{payload.jti}")
        if is_revoked:
            raise AppError(
                code="AUTH_TOKEN_REVOKED",
                message="The provided authentication token has been revoked.",
                status_code=401,
            )
        return payload

    async def revoke_access_token(self, payload: TokenPayload) -> None:
        remaining_ttl = max(payload.exp - int(datetime.now(UTC).timestamp()), 1)
        await self.redis.setex(f"auth:revoked:{payload.jti}", remaining_ttl, "1")

    async def revoke_access_token_by_claims(self, jti: str, exp: int) -> None:
        remaining_ttl = max(exp - int(datetime.now(UTC).timestamp()), 1)
        await self.redis.setex(f"auth:revoked:{jti}", remaining_ttl, "1")

    def get_jwks(self) -> dict[str, Any]:
        public_key = serialization.load_pem_public_key(self.public_key.encode("utf-8"))
        numbers = public_key.public_numbers()
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "local-dev-key",
                    "use": "sig",
                    "alg": "RS256",
                    "n": jwt.utils.base64url_encode(
                        numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")
                    ).decode("utf-8"),
                    "e": jwt.utils.base64url_encode(
                        numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big")
                    ).decode("utf-8"),
                }
            ]
        }

    async def _store_refresh_token(self, *, refresh_token: str, payload: dict[str, Any]) -> None:
        token_hash = self._hash_token(refresh_token)
        ttl = self.settings.refresh_token_expire_days * 86400
        await self.redis.setex(f"auth:refresh:{token_hash}", ttl, json.dumps(payload))
        member_key = f"auth:user_refresh:{payload['user_id']}"
        await self.redis.sadd(member_key, token_hash)
        await self.redis.expire(member_key, ttl)

    async def _load_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        token_hash = self._hash_token(refresh_token)
        raw = await self.redis.get(f"auth:refresh:{token_hash}")
        if raw is None:
            used_raw = await self.redis.get(f"auth:refresh_used:{token_hash}")
            if used_raw:
                used_payload = json.loads(used_raw)
                user_id = used_payload.get("user_id")
                if isinstance(user_id, str) and user_id:
                    await self.revoke_all_refresh_tokens_for_user(user_id)
            raise AppError(
                code="INVALID_REFRESH_TOKEN",
                message="The provided refresh token is invalid or expired.",
                status_code=401,
            )
        return json.loads(raw)

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def _decode_supabase_token(self, token: str) -> dict[str, Any] | None:
        if self.supabase_jwk_client is None:
            return None
        try:
            key = self.supabase_jwk_client.get_signing_key_from_jwt(token).key
            decode_kwargs: dict[str, Any] = {
                "algorithms": ["RS256"],
                "options": {
                    "verify_aud": bool(self.settings.supabase_jwt_audience),
                    "verify_iss": bool(self.settings.supabase_jwt_issuer),
                },
            }
            if self.settings.supabase_jwt_audience:
                decode_kwargs["audience"] = self.settings.supabase_jwt_audience
            if self.settings.supabase_jwt_issuer:
                decode_kwargs["issuer"] = self.settings.supabase_jwt_issuer
            return jwt.decode(token, key, **decode_kwargs)
        except Exception:  # noqa: BLE001
            return None


@lru_cache(maxsize=1)
def get_token_service() -> TokenService:
    return TokenService()
