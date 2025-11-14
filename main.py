from flask import Flask, request, render_template_string
from pyrogram import Client
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "mysafekey123")


html_home = """
<h2>Telegram Session String Generator</h2>
<form method="POST" action="/send_code">
  <label>Phone Number (with country code):</label><br>
  <input name="phone" placeholder="+91XXXXXXXXXX" required>
  <button type="submit">Send Code</button>
</form>
"""


html_code = """
<h2>Enter the Code Received on Telegram</h2>
<form method="POST" action="/verify_code">
  <input type="hidden" name="phone" value="{{phone}}">
  <label>Code:</label><br>
  <input name="code" placeholder="12345" required>
  <br><br>
  <label>2FA Password (if enabled):</label><br>
  <input name="password" placeholder="Leave empty if none">
  <br><br>
  <button type="submit">Generate Session</button>
</form>
"""


html_result = """
<h2>Session String Generated Successfully 🎉</h2>
<textarea style="width:100%; height:200px;">{{session}}</textarea>
<br><br>
<strong>Copy and save it safely!</strong>
"""


@app.route("/")
def home():
    return html_home


@app.route("/send_code", methods=["POST"])
def send_code():
    phone = request.form["phone"]

    async def _send():
        app.session_client = Client("session_gen", api_id=API_ID, api_hash=API_HASH)
        await app.session_client.connect()
        sent = await app.session_client.send_code(phone)
        return True

    asyncio.run(_send())
    return render_template_string(html_code, phone=phone)


@app.route("/verify_code", methods=["POST"])
def verify_code():
    phone = request.form["phone"]
    code = request.form["code"]
    password = request.form.get("password")

    async def _login():
        client = app.session_client

        try:
            if password:
                await client.sign_in(phone, code, password=password)
            else:
                await client.sign_in(phone, code)
        except Exception as e:
            return f"Login error: {e}"

        session = await client.export_session_string()
        await client.disconnect()
        return session

    session_string = asyncio.run(_login())

    return render_template_string(html_result, session=session_string)


if __name__ == "__main__":
    app.run(debug=True)
