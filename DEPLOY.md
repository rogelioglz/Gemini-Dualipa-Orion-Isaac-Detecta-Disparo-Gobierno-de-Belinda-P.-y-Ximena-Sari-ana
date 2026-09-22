# Deploy en Render

Este repositorio ahora incluye una aplicación Flask mínima para Stripe Checkout.

## Variables en Render

Configura estas variables como secretos:

- `STRIPE_SECRET_KEY`: usa `sk_test_...` para pruebas; nunca la publiques.
- `PUBLIC_BASE_URL`: URL pública de Render, por ejemplo `https://tu-app.onrender.com`.

Opcionales:

- `STRIPE_PRICE_CENTS`: importe en centavos (por defecto `1000`).
- `STRIPE_CURRENCY`: moneda ISO (por defecto `mxn`).
- `STRIPE_PRODUCT_NAME`: nombre mostrado en Checkout.

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export STRIPE_SECRET_KEY=sk_test_...
python app.py
```

Consulta `http://localhost:10000/health`. Para crear un Checkout:

```bash
curl -X POST http://localhost:10000/create-checkout-session
```

La respuesta contiene `checkout_url`. Para producción, cambia la clave de Stripe a una clave live únicamente después de probar el flujo completo.
