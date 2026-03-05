"""
WebhookService – triggers the n8n automation webhook when new evidence is uploaded.

n8n then:
  1. Sends SMS/email alerts to trusted contacts
  2. Calls Gemini API to generate the FIR
  3. POSTs the FIR back to /api/fir/save
"""
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Timeout for webhook POST requests (seconds)
WEBHOOK_TIMEOUT = 10


class WebhookService:
    """
    Sends a POST request to the configured n8n webhook URL
    with the emergency case payload.
    """

    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL

    def trigger(self, payload: dict) -> dict:
        """
        Fires the n8n webhook with the emergency evidence payload.

        Expected payload keys:
            case_id, user_name, user_phone, user_email,
            latitude, longitude, timestamp,
            evidence_url, evidence_count,
            trusted_contacts (list of {name, phone, email})

        Returns:
            Response dict from n8n (or error info)

        Raises:
            Exception if the webhook call fails critically
        """
        if not self.webhook_url:
            raise ValueError("N8N_WEBHOOK_URL is not configured.")

        logger.info(f"Triggering n8n webhook for case: {payload.get('case_id')}")
        logger.debug(f"Webhook URL: {self.webhook_url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-SafeSphere-Source": "backend",
                },
                timeout=WEBHOOK_TIMEOUT,
            )

            # n8n returns 200 on success
            if response.status_code == 200:
                logger.info(f"n8n webhook triggered successfully. Response: {response.text[:200]}")
                try:
                    return response.json()
                except Exception:
                    return {"status": "ok", "raw": response.text}
            else:
                logger.warning(
                    f"n8n webhook returned non-200 status: {response.status_code} – {response.text}"
                )
                return {
                    "status": "warning",
                    "http_status": response.status_code,
                    "response": response.text,
                }

        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to n8n webhook at {self.webhook_url}")
            raise ConnectionError(f"n8n is not reachable at {self.webhook_url}")

        except requests.exceptions.Timeout:
            logger.error(f"n8n webhook timed out after {WEBHOOK_TIMEOUT}s")
            raise TimeoutError("n8n webhook request timed out.")

        except Exception as e:
            logger.error(f"Unexpected error triggering webhook: {e}")
            raise
