from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Config:
    APP_VERSION: str = field(
        default_factory=lambda: os.environ.get("APP_VERSION", "1.0.0")
    )
    LOG_LEVEL: str = field(
        default_factory=lambda: os.environ.get("LOG_LEVEL", "INFO")
    )
    JWT_SECRET_KEY: str = field(
        default_factory=lambda: os.environ.get("JWT_SECRET_KEY", "")
    )
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = field(
        default_factory=lambda: int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    API_USERNAME: str = field(
        default_factory=lambda: os.environ.get("API_USERNAME", "")
    )
    API_PASSWORD: str = field(
        default_factory=lambda: os.environ.get("API_PASSWORD", "")
    )
    COINGECKO_BASE_URL: str = field(
        default_factory=lambda: os.environ.get("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
    )
    COINGECKO_TIMEOUT_SECONDS: int = field(
        default_factory=lambda: int(os.environ.get("COINGECKO_TIMEOUT_SECONDS", "10"))
    )
    CACHE_TTL_SECONDS: int = field(
        default_factory=lambda: int(os.environ.get("CACHE_TTL_SECONDS", "60"))
    )
    WEBHOOK_URL: str = field(
        default_factory=lambda: os.environ.get("WEBHOOK_URL", "")
    )
    WEBHOOK_TIMEOUT_SECONDS: int = field(
        default_factory=lambda: int(os.environ.get("WEBHOOK_TIMEOUT_SECONDS", "10"))
    )

    def validate(self) -> None:
        required = {
            "JWT_SECRET_KEY": self.JWT_SECRET_KEY,
            "API_USERNAME": self.API_USERNAME,
            "API_PASSWORD": self.API_PASSWORD,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            for name in missing:
                logger.critical("Required environment variable '%s' is not set.", name)
            raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")
