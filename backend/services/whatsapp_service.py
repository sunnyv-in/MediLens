import requests
from flask import current_app


def send_whatsapp_template(phone_number, medicine_name, scheduled_time, status):
    token = current_app.config.get("WHATSAPP_TOKEN")
    phone_number_id = current_app.config.get("WHATSAPP_PHONE_NUMBER_ID")
    template_name = current_app.config.get("WHATSAPP_TEMPLATE_NAME")
    graph_version = current_app.config.get("WHATSAPP_GRAPH_VERSION", "v23.0")

    if not token or not phone_number_id:
        raise RuntimeError("WhatsApp API credentials are not configured.")

    # WhatsApp API phone numbers must include the country code, without + or spaces.
    recipient = "".join(char for char in str(phone_number) if char.isdigit())

    if not recipient:
        raise ValueError("The user does not have a valid WhatsApp number.")

    url = f"https://graph.facebook.com/{graph_version}/" f"{phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": medicine_name},
                        {"type": "text", "text": scheduled_time},
                        {"type": "text", "text": status},
                    ],
                }
            ],
        },
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )

    if not response.ok:
        raise RuntimeError(
            f"WhatsApp API error {response.status_code}: {response.text}"
        )

    return response.json()
