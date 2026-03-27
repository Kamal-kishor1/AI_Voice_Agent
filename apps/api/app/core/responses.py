from datetime import datetime, timezone
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi import Request, status
from fastapi.responses import JSONResponse


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def success_response(
    request: Request,
    data: Any,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
            "success": True,
            "data": data,
            "meta": {
                "request_id": getattr(request.state, "request_id", "unknown"),
                "timestamp": _timestamp(),
            },
            }
        ),
    )


def error_response(
    request: Request,
    code: str,
    message: str,
    details: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", "unknown"),
                "timestamp": _timestamp(),
            },
            }
        ),
    )


def paginated_response(
    request: Request,
    data: Any,
    *,
    page: int,
    per_page: int,
    total_items: int,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    total_pages = (total_items + per_page - 1) // per_page if total_items else 0
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(
            {
                "success": True,
                "data": data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_items": total_items,
                    "total_pages": total_pages,
                },
                "meta": {
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "timestamp": _timestamp(),
                },
            }
        ),
    )
