"""Run ClearCouncil Next API locally."""

import uvicorn

from clearcouncil_next.core.config import get_settings


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "clearcouncil_next.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "dev",
    )
