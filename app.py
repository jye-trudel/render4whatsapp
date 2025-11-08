from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# --------------------------
# Google Sheets setup
# --------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from environment variable instead of a file
credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
if not credentials_json:
    raise Exception("GOOGLE_CREDENTIALS environment variable not set")

credentials_dict = json.loads(credentials_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("Expenses").sheet1  # Make sure your sheet is named "Expenses"

# --------------------------
# WhatsApp message endpoint
# --------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    msg = request.form.get("Body").strip()
    resp = MessagingResponse()
    try:
        parts = msg.split()
        category = parts[0]
        amount = float(parts[1])
        sheet.append_row([str(datetime.now()), category, amount])
        resp.message(f"✅ Logged {amount} under {category}.")
    except:
        resp.message("❌ Format error. Use: Category Amount (e.g., Food 12.50)")
    return str(resp)

# --------------------------
# Start server
# --------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
