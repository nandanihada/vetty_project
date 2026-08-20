from __future__ import annotations

import logging
import time
import uuid

from flask import Flask, Response, g, request

logger = logging.getLogger(__name__)


def register_middleware(app: Flask) -> None:
    @app.before_request
    def before_request() -> None:
        g.request_id = str(uuid.uuid4())
        g.start_time = time.monotonic()
        logger.info("request started", extra={"method": request.method, "path": request.path, "request_id": g.request_id})

    @app.after_request
    def after_request(response: Response) -> Response:
        duration_ms = round((time.monotonic() - g.start_time) * 1000, 2)
        logger.info("request finished", extra={"status_code": response.status_code, "duration_ms": duration_ms, "request_id": g.request_id})
        response.headers["X-Request-ID"] = g.request_id
        return response
