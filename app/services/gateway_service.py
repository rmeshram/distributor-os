import os
import logging
import httpx
from app.config import settings

logger = logging.getLogger("uvicorn.error")

class EvolutionGatewayService:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "https://evolution-api-latest-vma7.onrender.com").rstrip("/")
        self.api_key = os.getenv("EVOLUTION_API_KEY")

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["apikey"] = self.api_key
        return headers

    async def initialize_instance(self, instance_name: str) -> dict:
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        logger.info("Initializing Evolution API instance: url=%s, payload=%s", url, payload)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self._get_headers())
                if response.status_code not in (200, 201):
                    logger.error(
                        "Evolution API instance creation failed. status_code=%d, url=%s, payload=%s, response=%s",
                        response.status_code, url, payload, response.text
                    )
                    response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP error during instance initialization: url=%s, payload=%s, error=%s", url, payload, str(exc))
                raise
            except Exception as exc:
                logger.error("Unexpected error during instance initialization: url=%s, payload=%s, error=%s", url, payload, str(exc))
                raise

 async def generate_qr_code(self, instance_name: str) -> str:
        # Use POST as per Evolution API v2 documentation
        url = f"{self.base_url}/instance/connect/{instance_name}"
        
        logger.info("Generating QR code via POST: url=%s", url)
        
        async with httpx.AsyncClient() as client:
            try:
                # MUST be a POST request
                response = await client.post(url, headers=self._get_headers())
                
                if response.status_code != 200:
                    logger.error(
                        "Evolution API QR generation failed. status_code=%d, url=%s, response=%s",
                        response.status_code, url, response.text
                    )
                    response.raise_for_status()
                
                data = response.json()
                
                # Evolution API v2 usually returns base64 inside a 'qrcode' object
                # or directly in the base64 field of the response
                qrcode_data = data.get("qrcode") or {}
                base64_str = qrcode_data.get("base64") if isinstance(qrcode_data, dict) else data.get("base64")
                
                if base64_str:
                    return base64_str
                else:
                    logger.error("QR Code generation succeeded but no base64 found in response: %s", data)
                    raise RuntimeError("QR code data not found in API response.")
                    
            except Exception as exc:
                logger.error("Error during QR code generation: url=%s, error=%s", url, str(exc))
                raise

    async def configure_webhook(self, instance_name: str) -> dict:
        # ... (ensure this method is also indented by 4 spaces)

    async def configure_webhook(self, instance_name: str) -> dict:
        url = f"{self.base_url}/webhook/set/{instance_name}"
        app_url = os.getenv("APP_URL") or os.getenv("NEXT_PUBLIC_API_URL") or "http://127.0.0.1:8000"
        webhook_url = f"{app_url.rstrip('/')}/api/v1/whatsapp/webhook"
        
        payload = {
            "webhook": {
                "enabled": True,
                "url": webhook_url,
                "byEvents": False,
                "events": [
                    "MESSAGES_UPSERT",
                    "CONNECTION_UPDATE"
                ]
            }
        }
        logger.info("Configuring webhook for instance %s: url=%s, payload=%s", instance_name, url, payload)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self._get_headers())
                if response.status_code != 200:
                    logger.error(
                        "Evolution API webhook configuration failed. status_code=%d, url=%s, payload=%s, response=%s",
                        response.status_code, url, payload, response.text
                    )
                    response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP error during webhook configuration: url=%s, payload=%s, error=%s", url, payload, str(exc))
                raise
            except Exception as exc:
                logger.error("Unexpected error during webhook configuration: url=%s, payload=%s, error=%s", url, payload, str(exc))
                raise

    async def get_connection_status(self, instance_name: str) -> str:
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        logger.info("Fetching connection status for instance %s: url=%s", instance_name, url)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self._get_headers())
                if response.status_code != 200:
                    logger.error(
                        "Evolution API connection state check failed. status_code=%d, url=%s, response=%s",
                        response.status_code, url, response.text
                    )
                    response.raise_for_status()
                data = response.json()
                instance_data = data.get("instance", {})
                status = instance_data.get("state") or instance_data.get("status") or "close"
                return status
            except httpx.HTTPStatusError as exc:
                logger.error("HTTP error during connection status check: url=%s, error=%s", url, str(exc))
                raise
            except Exception as exc:
                logger.error("Unexpected error during connection status check: url=%s, error=%s", url, str(exc))
                raise
