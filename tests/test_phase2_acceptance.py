"""Phase 2 Acceptance Tests — Authentication & User Management."""

import asyncio
import json
import httpx

BASE = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient(base_url=BASE, timeout=15) as c:
        print("=" * 60)
        print("  Phase 2 Acceptance Tests — Auth & User Management")
        print("=" * 60)
        passed = 0
        failed = 0

        # ─── Test 1: Health check still works ───────────────────────
        print("\n[T1] GET /health ...")
        r = await c.get("/health")
        if r.status_code == 200 and r.json().get("status") == "healthy":
            print("  ✅  PASS — healthy")
            passed += 1
        else:
            print(f"  ❌  FAIL — {r.status_code} {r.text}")
            failed += 1

        # ─── Test 2: Unauthenticated request → 401 ─────────────────
        print("\n[T2] GET /v1/users/me (no token) ...")
        r = await c.get("/v1/users/me")
        if r.status_code in (401, 403):
            print(f"  ✅  PASS — {r.status_code}")
            passed += 1
        else:
            print(f"  ❌  FAIL — expected 401/403, got {r.status_code} {r.text}")
            failed += 1

        # ─── Test 3: Register a test user ───────────────────────────
        print("\n[T3] POST /v1/auth/register ...")
        reg_data = {
            "email": "test_phase2@antigravity.dev",
            "password": "T3stP@ssw0rd!!2026",
            "full_name": "Phase2 Tester",
        }
        r = await c.post("/v1/auth/register", json=reg_data)
        if r.status_code == 201:
            body = r.json()
            print(f"  ✅  PASS — user created: {body['data']['id']}")
            passed += 1
        elif r.status_code == 409:
            print(f"  ⏭  SKIP — user already exists (re-run safe)")
            passed += 1
        else:
            print(f"  ❌  FAIL — {r.status_code} {r.text}")
            failed += 1

        # ─── Test 4: Login with correct credentials ─────────────────
        print("\n[T4] POST /v1/auth/login ...")
        r = await c.post(
            "/v1/auth/login",
            json={"email": "test_phase2@antigravity.dev", "password": "T3stP@ssw0rd!!2026"},
        )
        if r.status_code == 200:
            body = r.json()
            access_token = body["data"]["access_token"]
            refresh_token = body["data"]["refresh_token"]
            user_id = body["data"]["user"]["id"]
            print(f"  ✅  PASS — logged in, token type: {body['data']['token_type']}")
            passed += 1
        else:
            print(f"  ❌  FAIL — {r.status_code} {r.text}")
            failed += 1
            access_token = refresh_token = user_id = None

        # ─── Test 5: Login with invalid credentials → 401 ──────────
        print("\n[T5] POST /v1/auth/login (wrong password) ...")
        r = await c.post(
            "/v1/auth/login",
            json={"email": "test_phase2@antigravity.dev", "password": "WrongPassword!123"},
        )
        if r.status_code == 401:
            err = r.json()
            print(f"  ✅  PASS — rejected: {err['error']['code']}")
            passed += 1
        else:
            print(f"  ❌  FAIL — expected 401, got {r.status_code}")
            failed += 1

        # ─── Test 6: Authenticated profile fetch ────────────────────
        if access_token:
            print("\n[T6] GET /v1/users/me (with token) ...")
            r = await c.get("/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
            if r.status_code == 200:
                body = r.json()
                print(f"  ✅  PASS — profile: {body['data']['email']}")
                passed += 1
            else:
                print(f"  ❌  FAIL — {r.status_code} {r.text}")
                failed += 1
        else:
            print("\n[T6] SKIP — no access token")

        # ─── Test 7: Expired/invalid JWT → 401 ─────────────────────
        print("\n[T7] GET /v1/users/me (garbage token) ...")
        r = await c.get("/v1/users/me", headers={"Authorization": "Bearer totally.invalid.token"})
        if r.status_code == 401:
            print(f"  ✅  PASS — rejected invalid token")
            passed += 1
        else:
            print(f"  ❌  FAIL — expected 401, got {r.status_code}")
            failed += 1

        # ─── Test 8: Refresh token rotation ─────────────────────────
        if refresh_token:
            print("\n[T8] POST /v1/auth/refresh ...")
            r = await c.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
            if r.status_code == 200:
                body = r.json()
                new_access = body["data"]["access_token"]
                new_refresh = body["data"]["refresh_token"]
                print(f"  ✅  PASS — tokens rotated")
                passed += 1

                # Verify old refresh token is now invalid (reuse detection)
                print("\n[T8b] POST /v1/auth/refresh (reuse old token) ...")
                r2 = await c.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
                if r2.status_code == 401:
                    print(f"  ✅  PASS — old refresh token rejected (reuse detection)")
                    passed += 1
                else:
                    print(f"  ❌  FAIL — expected 401 on old token, got {r2.status_code}")
                    failed += 1

                access_token = new_access
                refresh_token = new_refresh
            else:
                print(f"  ❌  FAIL — {r.status_code} {r.text}")
                failed += 1
        else:
            print("\n[T8] SKIP — no refresh token")

        # ─── Test 9: Update profile ─────────────────────────────────
        if access_token:
            print("\n[T9] PATCH /v1/users/me ...")
            r = await c.patch(
                "/v1/users/me",
                json={"full_name": "Phase2 Updated Tester"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if r.status_code == 200:
                body = r.json()
                print(f"  ✅  PASS — updated name: {body['data']['full_name']}")
                passed += 1
            else:
                print(f"  ❌  FAIL — {r.status_code} {r.text}")
                failed += 1
        else:
            print("\n[T9] SKIP — no access token")

        # ─── Test 10: JWKS endpoint ─────────────────────────────────
        print("\n[T10] GET /.well-known/jwks.json ...")
        r = await c.get("/.well-known/jwks.json")
        if r.status_code == 200:
            body = r.json()
            keys = body.get("keys", [])
            print(f"  ✅  PASS — JWKS served, {len(keys)} key(s)")
            passed += 1
        else:
            print(f"  ❌  FAIL — {r.status_code}")
            failed += 1

        # ─── Test 11: Password validation (too weak) ────────────────
        print("\n[T11] POST /v1/auth/register (weak password) ...")
        r = await c.post(
            "/v1/auth/register",
            json={"email": "weak@test.com", "password": "short", "full_name": "Weak"},
        )
        if r.status_code == 422:
            print(f"  ✅  PASS — weak password rejected (422)")
            passed += 1
        else:
            print(f"  ❌  FAIL — expected 422, got {r.status_code}")
            failed += 1

        # ─── Test 12: Logout ─────────────────────────────────────────
        if access_token:
            print("\n[T12] POST /v1/auth/logout ...")
            r = await c.post("/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
            if r.status_code == 204:
                print(f"  ✅  PASS — logged out")
                passed += 1

                # Verify token is revoked after logout
                print("\n[T12b] GET /v1/users/me (revoked token after logout) ...")
                r2 = await c.get("/v1/users/me", headers={"Authorization": f"Bearer {access_token}"})
                if r2.status_code == 401:
                    print(f"  ✅  PASS — revoked token rejected")
                    passed += 1
                else:
                    print(f"  ❌  FAIL — expected 401, got {r2.status_code}")
                    failed += 1
            else:
                print(f"  ❌  FAIL — {r.status_code} {r.text}")
                failed += 1
        else:
            print("\n[T12] SKIP — no access token")

        # ─── Summary ────────────────────────────────────────────────
        total = passed + failed
        print("\n" + "=" * 60)
        print(f"  Results: {passed}/{total} passed, {failed} failed")
        print("=" * 60)
        if failed > 0:
            print("  ⚠️  Some tests failed — review output above")
        else:
            print("  🎉  ALL PHASE 2 ACCEPTANCE TESTS PASSED!")


if __name__ == "__main__":
    asyncio.run(main())
