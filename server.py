import hashlib
import os
import random
from urllib.parse import urlencode

from flask import Flask, jsonify, request, redirect, Response
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)


MERCHANT_LOGIN = os.getenv("ROBOKASSA_MERCHANT_LOGIN")
PASSWORD_1 = os.getenv("ROBOKASSA_PASSWORD_1")
PASSWORD_2 = os.getenv("ROBOKASSA_PASSWORD_2")

TICKET_PRICE = "1590.00"


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


@app.get("/")
def home():
    return "KATARSIS payment server is running"


@app.post("/create-payment")
def create_payment():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()

    if not email:
        return jsonify({
            "error": "Email обязателен"
        }), 400

    if not MERCHANT_LOGIN or not PASSWORD_1:
        return jsonify({
            "error": "Robokassa не настроена на сервере"
        }), 500

    # Пока случайный номер заказа.
    # Позже подключим нормальную базу данных.
    inv_id = random.randint(100000, 999999999)

    description = f"Билет КАТАРСИС fest. Заказ {inv_id}"

    signature_string = (
        f"{MERCHANT_LOGIN}:"
        f"{TICKET_PRICE}:"
        f"{inv_id}:"
        f"{PASSWORD_1}"
    )

    signature = md5(signature_string)

    params = {
        "MerchantLogin": MERCHANT_LOGIN,
        "OutSum": TICKET_PRICE,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Email": email,
        "Culture": "ru",
        "IsTest": "1"
    }

    payment_url = (
        "https://auth.robokassa.ru/Merchant/Index.aspx?"
        + urlencode(params)
    )

    return jsonify({
        "payment_url": payment_url,
        "order_id": inv_id
    })

@app.get("/pay")
def pay():
    email = request.args.get("email", "").strip()

    if not email:
        return "Email обязателен", 400

    if not MERCHANT_LOGIN or not PASSWORD_1:
        return "Robokassa не настроена", 500

    inv_id = random.randint(100000, 999999999)

    description = f"Билет КАТАРСИС fest. Заказ {inv_id}"

    signature_string = (
        f"{MERCHANT_LOGIN}:"
        f"{TICKET_PRICE}:"
        f"{inv_id}:"
        f"{PASSWORD_1}"
    )

    signature = md5(signature_string)

    params = {
        "MerchantLogin": MERCHANT_LOGIN,
        "OutSum": TICKET_PRICE,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Email": email,
        "Culture": "ru",
        "IsTest": "1"
    }

    payment_url = (
        "https://auth.robokassa.ru/Merchant/Index.aspx?"
        + urlencode(params)
    )

    return redirect(payment_url)

@app.get("/checkout")
def checkout():
    email = request.args.get("email", "").strip()

    if not email:
        return "Email обязателен", 400

    if not MERCHANT_LOGIN or not PASSWORD_1:
        return "Robokassa не настроена", 500

    inv_id = random.randint(100000, 999999999)

    description = f"Билет КАТАРСИС fest. Заказ {inv_id}"

    signature = md5(
        f"{MERCHANT_LOGIN}:{TICKET_PRICE}:{inv_id}:{PASSWORD_1}"
    )

    params = {
        "MerchantLogin": MERCHANT_LOGIN,
        "OutSum": TICKET_PRICE,
        "InvId": inv_id,
        "Description": description,
        "SignatureValue": signature,
        "Email": email,
        "Culture": "ru",
        "IsTest": "1"
    }

    payment_url = (
        "https://auth.robokassa.ru/Merchant/Index.aspx?"
        + urlencode(params)
    )

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Оплата — КАТАРСИС</title>

        <style>
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background: #030508;
                overflow: hidden;
            }}

            iframe {{
                width: 100%;
                height: 100vh;
                border: 0;
                background: white;
            }}
        </style>
    </head>

    <body>
        <iframe
            src="{payment_url}"
            allow="payment *"
        ></iframe>
    </body>
    </html>
    """

    return Response(html, mimetype="text/html")

@app.route("/payment/result", methods=["GET", "POST"])
def payment_result():
    data = request.values

    out_sum = data.get("OutSum", "")
    inv_id = data.get("InvId", "")
    received_signature = data.get("SignatureValue", "").lower()

    if not out_sum or not inv_id or not received_signature:
        return "Missing parameters", 400

    if not PASSWORD_2:
        return "Server configuration error", 500

    expected_signature = md5(
        f"{out_sum}:{inv_id}:{PASSWORD_2}"
    ).lower()

    if received_signature != expected_signature:
        return "Invalid signature", 403

    print(f"PAYMENT CONFIRMED: order={inv_id}, sum={out_sum}")

    return f"OK{inv_id}"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=80,
        debug=False
    )
