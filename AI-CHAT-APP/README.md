# 💬 ChatApp – Firebase + WebSocket AI Assistant

A React-based chat application that allows users to create multiple chat sessions and interact with an AI assistant in real-time using WebSocket. Messages are stored and synced with Firebase Firestore.

---

## 🚀 Features

- 🔥 Firebase Firestore integration for real-time message storage
- 🔁 Real-time updates using Firestore `onSnapshot`
- 🌐 WebSocket connection to a remote AI assistant
- 💬 Multiple chat sessions support
- 🧠 Smart UI for AI responses (bill summaries with paid/unpaid indicators)
- 🗑️ Chat deletion with message cleanup
- ⏳ Message sending states and validations

---

## 📦 Tech Stack

| Technology      | Usage                          |
|-----------------|--------------------------------|
| React           | Frontend Framework             |
| Firebase Firestore | Real-time database           |
| Firebase SDK    | Firestore interactions         |
| WebSocket       | Communication with AI backend  |
| JavaScript (ES6)| Core application logic         |

---

## 🔧 Setup & Installation

1. **Clone the Repository**

```bash
git clone https://github.com/bartutaskin/SE4458-AI-CHAT-APP.git
cd SE4458-AI-CHAT-APP
```

2. **Install Dependencies**

```bash
npm install
```

3. **Firebase Configuration**
Replace the content of firebase.js with your Firebase project config:
```bash
// firebase.js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "...",
  authDomain: "...",
  projectId: "...",
  storageBucket: "...",
  messagingSenderId: "...",
  appId: "..."
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
```

4. **Run the App**
```bash
npm start
```

## 💡 How It Works

### 1. Chat Initialization

* Click "New Chat" to create a new Firestore chat document.

### 2. Messaging

* Messages are stored in subcollections (chats/{chatId}/messages).

* User messages are sent over WebSocket to the AI server.

* AI responses are received via WebSocket and stored in Firestore.

### 3. Message Display

* All messages are streamed using onSnapshot for real-time updates.

* Special UI rendering for bill summaries (structured replies from AI).

### 4. Delete Chat

* Deletes the chat document and its messages from Firestore.


## 🔗 Related Repositories

This project integrates with and depends on the following repositories:

- [SE4458-AI-AGENT](https://github.com/bartutaskin/SE4458-AI-AGENT)  
  *AI agent backend that processes user queries and interacts with billing APIs.*

- [MobileProviderAPI](https://github.com/bartutaskin/MobileProviderAPI)  
  *Backend APIs for billing, querying, and payment functionality.*

- [SE4458-API-GATEWAY](https://github.com/bartutaskin/SE4458-API-GATEWAY)  
  *API Gateway that routes requests between frontend, AI agent, and backend APIs.*
