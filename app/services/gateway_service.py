import os
import asyncio
import logging
import httpx
from typing import Optional

logger = logging.getLogger("uvicorn.error")

class EvolutionGatewayService:
    def __init__(self, client: Optional[httpx.AsyncClient] = None):
        self.base_url = os.getenv("EVOLUTION_API_URL", "https://evolution-api-latest-vma7.onrender.com").rstrip("/")
        self.api_key = os.getenv("EVOLUTION_API_KEY")
        self._client = client

    def _get_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["apikey"] = self.api_key
        return headers

    def _get_client(self) -> httpx.AsyncClient:
        return self._client if self._client is not None else httpx.AsyncClient(timeout=30.0)

    async def initialize_instance(self, instance_name: str) -> dict:
        """POST /instance/create — registers instance in Evolution API."""
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        logger.info("Creating instance: POST %s payload=%s", url, payload)
        client = self._get_client()
        try:
            response = await client.post(url, json=payload, headers=self._get_headers())
            logger.info("Create instance response: status=%d body=%s", response.status_code, response.text[:300])
            if response.status_code not in (200, 201):
                response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error creating instance: status=%d body=%s", exc.response.status_code, exc.response.text)
            raise
        finally:
            if self._client is None:
                await client.aclose()

    async def configure_webhook(self, instance_name: str) -> dict:
        """POST /webhook/set/:instanceName — point Evolution API at our webhook."""
        url = f"{self.base_url}/webhook/set/{instance_name}"
        app_url = (
            os.getenv("APP_URL")
            or os.getenv("RENDER_EXTERNAL_URL")
            or "https://distributor-os-backend.onrender.com"
        ).rstrip("/")
        webhook_url = f"{app_url}/api/v1/whatsapp/webhook"
        payload = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "byEvents": False,
                "base64": False,
                "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
            }
        }
        logger.info("Configuring webhook: POST %s payload=%s", url, payload)
        client = self._get_client()
        try:
            response = await client.post(url, json=payload, headers=self._get_headers())
            logger.info("Webhook config response: status=%d body=%s", response.status_code, response.text[:300])
            if response.status_code != 200:
                response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error configuring webhook: status=%d body=%s", exc.response.status_code, exc.response.text)
            raise
        finally:
            if self._client is None:
                await client.aclose()

    async def generate_qr_code(self, instance_name: str, max_attempts: int = 10, interval_seconds: float = 2.0) -> str:
        """
        GET /instance/connect/:instanceName — triggers Baileys socket + returns QR base64.

        WHY THE POLL LOOP:
        Evolution API creates the instance synchronously, but the WhatsApp QR code
        is generated asynchronously by the Baileys socket (~1-3s after connect is called).
        The first call returns { count: 0 } with no base64 because Baileys hasn't finished
        yet. We retry until base64 appears or we hit max_attempts.
        """
        url = f"{self.base_url}/instance/connect/{instance_name}"
        logger.info("Requesting QR code: GET %s (will poll up to %d times)", url, max_attempts)

        client = self._get_client()
        try:
            for attempt in range(1, max_attempts + 1):
                response = await client.get(url, headers=self._get_headers())
                logger.info(
                    "QR poll attempt %d/%d: status=%d body=%s",
                    attempt, max_attempts, response.status_code, response.text[:400]
                )

                if response.status_code != 200:
                    response.raise_for_status()

                data = response.json()

                # Already connected — no QR needed
                state = (
                    data.get("state")
                    or data.get("connectionStatus")
                    or (data.get("instance") or {}).get("state")
                    or ""
                )
                if state == "open":
                    logger.info("Instance already open/connected.")
                    return "ALREADY_CONNECTED"

                # QR code lives at data.qrcode.base64
                qr_block = data.get("qrcode") or {}
                base64_str = qr_block.get("base64") if isinstance(qr_block, dict) else None

                if base64_str:
                    logger.info("QR base64 received on attempt %d.", attempt)
                    return base64_str

                count = qr_block.get("count", "?") if isinstance(qr_block, dict) else "?"
                logger.info(
                    "QR not ready yet (count=%s). Waiting %.1fs before retry...",
                    count, interval_seconds
                )

                if attempt < max_attempts:
                    await asyncio.sleep(interval_seconds)

            raise RuntimeError(
                f"QR code base64 not received after {max_attempts} attempts "
                f"({max_attempts * interval_seconds:.0f}s). "
                "Instance may be taking longer than expected to connect to WhatsApp."
            )
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error polling QR: status=%d body=%s", exc.response.status_code, exc.response.text)
            raise
        finally:
            if self._client is None:
                await client.aclose()

    async def get_connection_status(self, instance_name: str) -> str:
        """GET /instance/connectionState/:instanceName"""
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        logger.info("Checking connection state: GET %s", url)
        client = self._get_client()
        try:
            response = await client.get(url, headers=self._get_headers())
            logger.info("Connection state response: status=%d body=%s", response.status_code, response.text[:300])
            if response.status_code != 200:
                response.raise_for_status()
            data = response.json()
            instance_data = data.get("instance", {})
            status = (
                data.get("connectionStatus")
                or instance_data.get("connectionStatus")
                or instance_data.get("state")
                or instance_data.get("status")
                or "close"
            )
            return status
        except httpx.HTTPStatusError as exc:
            logger.error("HTTP error checking connection state: status=%d body=%s", exc.response.status_code, exc.response.text)
            raise
        finally:
            if self._client is None:
                await client.aclose()
