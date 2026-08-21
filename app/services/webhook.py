from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import Config

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, config: Config) -> None:
        self._url = config.WEBHOOK_URL
        self._timeout = config.WEBHOOK_TIMEOUT_SECONDS

    async def notify_market_fetch(
        self,
        coin_id: str | None,
        category: str | None,
        record_count: int,
    ) -> None:
        if not self._url:
            logger.warning("WEBHOOK_URL is not set; skipping webhook notification")
            return

        payload: dict[str, Any] = {
            "event": "market_data_fetched",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "coin_id": coin_id,
            "category": category,
            "record_count": record_count,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._url, json=payload)
            if not response.is_success:
                logger.error(
                    "Webhook POST failed",
                    extra={"status_code": response.status_code, "url": self._url},
                )
        except Exception as exc:
            logger.error("Webhook POST raised an exception", extra={"error": str(exc), "url": self._url})
