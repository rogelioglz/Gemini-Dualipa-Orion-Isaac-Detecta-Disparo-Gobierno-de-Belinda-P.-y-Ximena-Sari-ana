import os
from flask import Flask, jsonify, redirect, request
import stripe

app = Flask(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

PRICE_CENTS = int(os.environ.get("STRIPE_PRICE_CENTS", "1000"))
CURRENCY = os.environ.get("STRIPE_CURRENCY", "mxn")
PRODUCT_NAME = os.environ.get("STRIPE_PRODUCT_NAME", "Acceso al servicio")
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")


def public_base_url():
    return BASE_URL or request.url_root.rstrip("/")


@app.get("/")
def index():
    return jsonify({
        "service": "stripe-checkout",
        "status": "ok",
        "checkout": "/create-checkout-session",
        "health": "/health",
    })


@app.get("/health")
def health():
    return jsonify({"ok": True, "stripe_configured": bool(stripe.api_key)})


@app.post("/create-checkout-session")
def create_checkout_session():
    if not stripe.api_key:
        return jsonify({"error": "STRIPE_SECRET_KEY no está configurada en Render"}), 503

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": CURRENCY,
                    "product_data": {"name": PRODUCT_NAME},
                    "unit_amount": PRICE_CENTS,
                },
                "quantity": 1,
            }],
            success_url=f"{public_base_url()}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{public_base_url()}/cancel",
        )
        return jsonify({"checkout_url": session.url, "session_id": session.id})
    except stripe.error.StripeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.get("/success")
def success():
    return "Pago completado correctamente. Gracias."


@app.get("/cancel")
def cancel():
    return "Pago cancelado."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
