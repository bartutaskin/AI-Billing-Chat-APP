# 💬 AI Billing Assistant (FastAPI + HuggingFace + WebSocket)

This project is an AI-powered billing assistant built using **FastAPI**, **WebSocket**, and **Hugging Face Chatbot (HugChat)**. It allows users to query and pay their bills using natural language via a real-time WebSocket chat interface.

---

## 🚀 Features

- 🌐 WebSocket-based real-time chat interface
- 🧠 Uses Hugging Face LLM (via HugChat) for natural language understanding
- 🔐 Authenticates via JWT before making API calls
- 📄 Supports three main actions:
  - `QueryBill` — Get billing info for a specific month
  - `QueryBillDetailed` — Get detailed bills for a full year
  - `PayBill` — Make a payment for a given month
- 🔁 Automatically refreshes JWT on unauthorized responses
- 🔒 Secure credential management using `.env` and Base64-encoded cookies

---

## 🧩 Tech Stack

- Python 3.13
- FastAPI
- HugChat
- WebSocket
- Dotenv
- JSON
- Base64

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/bartutaskin/SE4458-AI-AGENT.git
cd SE4458-AI-AGENT
```

### 2. Log in to Hugging Face and Generate Cookie

To authenticate with HugChat and generate your session cookies:

1. Install hugchat if you haven’t already:
```bash
pip install hugchat
```
2. Use the following script to log in and print your cookies:
```bash
from hugchat.login import Login

HF_EMAIL = "your_email@example.com"
HF_PASSWORD = "your_password"

sign = Login(HF_EMAIL, HF_PASSWORD)
cookies = sign.login(cookie_dir_path="./cookies/", save_cookies=True)
```
3. Use PowerShell to Base64-encode the saved cookie file:
```bash
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies/your_email@example.com.json")) > encoded_cookie.txt
```
4. Copy the Base64 string from encoded_cookie.txt and paste it into your .env file as shown below.
```bash
hf_cookie_str = os.getenv("HF_COOKIE")
if hf_cookie_str is None:
    raise ValueError("HF_COOKIE environment variable not set")

decoded_bytes = base64.b64decode(hf_cookie_str)
decoded_str = decoded_bytes.decode("utf-8")
cookies = json.loads(decoded_str)
chatbot = hugchat.ChatBot(cookies=cookies) 
```

### 3. Create .env file

```bash
HF_COOKIE=PASTE_THE_BASE64_STRING_HERE
GATEWAY_URL=https://your-api-gateway.com
AUTH_URL=https://your-auth-service.com/auth
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the app

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔗 Related Repositories

This project integrates with and depends on the following repositories:

- [SE4458-AI-CHAT-APP](https://github.com/bartutaskin/SE4458-AI-CHAT-APP)  
  *Frontend chat application that interacts with the AI agent backend.*

- [MobileProviderAPI](https://github.com/bartutaskin/MobileProviderAPI)  
  *Backend APIs for billing, querying, and payment functionality.*

- [SE4458-API-GATEWAY](https://github.com/bartutaskin/SE4458-API-GATEWAY)  
  *API Gateway that routes requests between frontend, AI agent, and backend APIs.*
