import json
import warnings
import requests
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from hugchat import hugchat
from hugchat.login import Login
from pathlib import Path
import base64

# Suppress InsecureRequestWarning for self-signed localhost certs
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

app = FastAPI()

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load env variables
load_dotenv()

HF_COOKIE = os.getenv("HF_COOKIE")
GATEWAY_URL = os.getenv("GATEWAY_URL")
AUTH_URL = os.getenv("AUTH_URL")
HF_EMAIL = os.getenv("HF_EMAIL")
HF_PASSWORD = os.getenv("HF_PASSWORD")

# Login once and keep the cookies globally
# sign = Login(HF_EMAIL, HF_PASSWORD)
# cookies = sign.login(cookie_dir_path="./cookies/", save_cookies=False)
# chatbot = hugchat.ChatBot(cookies=cookies.get_dict())
# print(cookies.get_dict())

# cookies_path = Path("./cookies/bartutaskin35@gmail.com.json")
# with open(cookies_path, "r") as f:
#     cookies = json.load(f)

hf_cookie_str = os.getenv("HF_COOKIE")
if hf_cookie_str is None:
    raise ValueError("HF_COOKIE environment variable not set")

decoded_bytes = base64.b64decode(hf_cookie_str)
decoded_str = decoded_bytes.decode("utf-8")
cookies = json.loads(decoded_str)
chatbot = hugchat.ChatBot(cookies=cookies)

jwt_token = None


def get_jwt_token(username: str, password: str) -> str:
    global jwt_token
    try:
        response = requests.post(
            AUTH_URL,
            json={"username": username, "password": password},
            verify=False,
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("token")
        if not token:
            raise ValueError("Token not found in auth response")
        jwt_token = token
        print("[AUTH] Got JWT token")
        return token
    except Exception as e:
        print(f"[AUTH ERROR] Failed to get JWT token: {e}")
        return None


def build_prompt(user_input: str) -> str:
    return f"""
You are an AI-powered billing assistant.

Your task is to analyze the user's message and identify one or more billing-related actions they want to perform.

Each action must include:
- intent: one of ["QueryBill", "QueryBillDetailed", "PayBill"]
- parameters:
    - subscriberNo (string)
    - month (1–12)
    - year (e.g., 2024)
    - paymentAmount (float, only required for PayBill)

**Use the "QueryBill" intent when the user asks for their bill in a specific month and year** (e.g., "What’s my bill for May 2025?").

**Use the "QueryBillDetailed" intent only when the user requests a yearly breakdown or multiple months**, like:
- "Show me detailed bills for 2025"
- "What were all my bills this year?"

If any parameter is missing, respond like this:
{{ "intent": "missing_info", "missing": ["subscriberNo", "month"] }}

Only include PayBill if the user clearly says "pay" or "make a payment".

Respond ONLY with raw, valid JSON. DO NOT include any explanation, markdown, or natural language.

User message:
\"{user_input}\"
"""


def ask_hugchat(prompt: str) -> str:
    # Use the HugChat chatbot to get a response
    response = chatbot.chat(prompt)
    return response.wait_until_done().strip()


def call_api(intent: str, params: dict) -> str:
    global jwt_token
    headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}

    try:
        if intent == "QueryBill":
            response = requests.get(
                f"{GATEWAY_URL}/QueryBill/query",
                params=params,
                headers=headers,
                verify=False,
            )
        elif intent == "QueryBillDetailed":
            response = requests.get(
                f"{GATEWAY_URL}/QueryBillDetailed/query-detailed",
                params=params,
                headers=headers,
                verify=False,
            )
        elif intent == "PayBill":
            response = requests.post(
                f"{GATEWAY_URL}/Bill/pay", json=params, headers=headers, verify=False
            )
        else:
            return f"Unknown intent: {intent}"

        if response.status_code == 401:
            print("[API] Unauthorized. Refreshing token and retrying...")
            get_jwt_token("test", "test123")
            headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
            if intent == "QueryBill":
                response = requests.get(
                    f"{GATEWAY_URL}/QueryBill/query",
                    params=params,
                    headers=headers,
                    verify=False,
                )
            elif intent == "QueryBillDetailed":
                response = requests.get(
                    f"{GATEWAY_URL}/QueryBillDetailed/query-detailed",
                    params=params,
                    headers=headers,
                    verify=False,
                )
            elif intent == "PayBill":
                response = requests.post(
                    f"{GATEWAY_URL}/Bill/pay",
                    json=params,
                    headers=headers,
                    verify=False,
                )

        if response.status_code == 200:
            return response.text
        else:
            return f"Failed ({response.status_code}): {response.text}"

    except Exception as e:
        return f"API call failed: {str(e)}"


def format_api_response(intent: str, raw_text: str, params: dict) -> str:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return raw_text

    if intent == "QueryBillDetailed":
        items = data.get("items", [])
        if not items:
            return "No detailed billing information found for your account."

        messages = []
        for item in items:
            month = item.get("month", "unknown")
            phone = item.get("phoneCharge", "unknown")
            internet = item.get("internetCharge", "unknown")
            total = item.get("totalAmount", "unknown")
            paid = item.get("paidStatus", False)
            status = "Paid ✅" if paid else "Unpaid ❌"
            messages.append(
                f"Month {month}: Phone charge {phone} TL, Internet charge {internet} TL, Total {total} TL — Status: {status}"
            )
        return "\n".join(messages)

    elif intent == "QueryBill":
        total = data.get("totalAmount", "unknown")
        paid = data.get("paidStatus", False)
        status = "Paid ✅" if paid else "Unpaid ❌"
        month = params.get("month", "unknown")
        year = params.get("year", "unknown")
        return f"Your bill for {month}/{year} amounts to {total} TL. Payment status: {status}."

    elif intent == "PayBill":
        message = data.get("message", "")
        if "successful" in message.lower():
            return "Payment completed successfully. ✅ Thank you!"
        elif "already paid" in message.lower():
            return "This bill was already paid. ✅ No further action needed."
        elif "insufficient" in message.lower():
            return "Payment failed due to insufficient amount. ❌ Please check and try again."
        else:
            return message

    return raw_text


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hi! How can I help you?")

    # Get initial JWT token
    get_jwt_token("test", "test123")

    while True:
        try:
            user_message = await websocket.receive_text()
            print("🟡 Message received:", user_message)

            prompt = build_prompt(user_message)
            print("🟡 Prompt for LLM:\n", prompt)

            llm_response = ask_hugchat(prompt).strip()
            print("🟢 LLM response:\n", llm_response)

            try:
                data = json.loads(llm_response)
            except json.JSONDecodeError:
                await websocket.send_text("⚠️ AI response was not valid JSON.")
                continue

            if data.get("intent") == "missing_info":
                missing = data.get("missing", [])
                await websocket.send_text(
                    f"🛑 I need more information: {', '.join(missing)}"
                )
                continue

            # Wrap single action in "actions" array
            if "actions" not in data and "intent" in data:
                parameters = data.get(
                    "parameters", {k: v for k, v in data.items() if k != "intent"}
                )
                data = {
                    "actions": [{"intent": data["intent"], "parameters": parameters}]
                }

            if "actions" in data:
                for action in data["actions"]:
                    intent = action["intent"]
                    params = action["parameters"]

                    missing_params = [k for k, v in params.items() if v is None]
                    if missing_params:
                        await websocket.send_text(
                            f"🛑 I need more information: {', '.join(missing_params)}"
                        )
                        continue

                    if intent == "QueryBillDetailed":
                        params.setdefault("page", 1)
                        params.setdefault("pageSize", 50)

                    if intent == "PayBill" and "pay" not in user_message.lower():
                        await websocket.send_text(
                            "⚠️ You didn't ask to pay. Skipping payment."
                        )
                        continue

                    print(f"[API LOG] Intent: {intent} → Params: {params}")
                    result = call_api(intent, params)
                    print(f"[API RAW RESULT]:\n{result}")
                    formatted = format_api_response(intent, result, params)
                    await websocket.send_text(formatted)

            else:
                await websocket.send_text(
                    "⚠️ Sorry, I couldn't understand your request."
                )

        except Exception as e:
            print("🔥 Fatal error:", e)
            try:
                await websocket.send_text(f"❌ Internal error: {str(e)}")
            except:
                print("⚠️ Could not send error message.")
            break
