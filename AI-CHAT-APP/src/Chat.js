import React, { useEffect, useState, useRef } from "react";
import {
  collection,
  addDoc,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp,
  doc,
  setDoc,
  getDocs,
  deleteDoc,
} from "firebase/firestore";
import { db } from "./firebase"; // Firebase config

export default function ChatApp() {
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const ws = useRef(null);

  // Fetch chats on load
  useEffect(() => {
    const fetchChats = async () => {
      const q = query(collection(db, "chats"));
      const snapshot = await getDocs(q);
      const chatList = snapshot.docs.map((doc) => ({
        id: doc.id,
      }));
      setChats(chatList);
    };
    fetchChats();
  }, []);

  // Listen to messages of selected chat
  useEffect(() => {
    if (!selectedChatId) return;

    const messagesRef = collection(db, "chats", selectedChatId, "messages");
    const q = query(messagesRef, orderBy("createdAt"));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const msgs = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }));
      setMessages(msgs);
    });

    // Setup WebSocket for selected chat
    ws.current = new WebSocket("wss://mobileprovider-aiagent-degjh6fcbnatcfcp.italynorth-01.azurewebsites.net/ws");

    ws.current.onopen = () => {
      console.log("WebSocket connected");
    };

    ws.current.onmessage = async (event) => {
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        data = { reply: event.data };
      }

      const assistantReply = data.reply || "Sorry, I couldn't process that.";

      const messagesRef = collection(db, "chats", selectedChatId, "messages");
      await addDoc(messagesRef, {
        text: assistantReply,
        sender: "assistant",
        createdAt: serverTimestamp(),
      });

      setSending(false);
    };

    return () => {
      unsubscribe();
      ws.current?.close();
    };
  }, [selectedChatId]);

  const createNewChat = async () => {
    const newId = `chat-${Date.now()}`;
    await setDoc(doc(db, "chats", newId), {}); // create empty doc
    setChats([...chats, { id: newId }]);
    setSelectedChatId(newId);
  };

  const sendMessage = async () => {
    if (!input.trim() || sending || !selectedChatId) return;

    setSending(true);
    const userMsg = input.trim();

    const messagesRef = collection(db, "chats", selectedChatId, "messages");
    await addDoc(messagesRef, {
      text: userMsg,
      sender: "user",
      createdAt: serverTimestamp(),
    });

    setInput("");
    ws.current.send(userMsg);
  };

  // Delete all messages of a chat
  async function deleteChatMessages(chatId) {
    const messagesRef = collection(db, "chats", chatId, "messages");
    const q = query(messagesRef);
    const snapshot = await getDocs(q);
    const deletePromises = snapshot.docs.map((msgDoc) => deleteDoc(msgDoc.ref));
    await Promise.all(deletePromises);
  }

  // Delete chat and its messages
  const deleteChat = async (chatId) => {
    try {
      await deleteChatMessages(chatId); // Delete all messages first
      await deleteDoc(doc(db, "chats", chatId)); // Delete chat doc

      // Remove from local state
      setChats((prev) => prev.filter((chat) => chat.id !== chatId));

      // Reset selection if deleted chat was selected
      if (selectedChatId === chatId) {
        setSelectedChatId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <div style={{ width: 250, borderRight: "1px solid #ccc", padding: 10 }}>
        <h3>Chats</h3>
        <button onClick={createNewChat}>+ New Chat</button>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {chats.map((chat) => (
            <li
              key={chat.id}
              style={{ display: "flex", alignItems: "center", marginTop: 5 }}
            >
              <button
                style={{
                  backgroundColor:
                    chat.id === selectedChatId ? "#ddd" : "white",
                  flexGrow: 1,
                  textAlign: "left",
                  border: "none",
                  padding: "5px 10px",
                  cursor: "pointer",
                }}
                onClick={() => setSelectedChatId(chat.id)}
              >
                {chat.id}
              </button>
              <button
                onClick={() => deleteChat(chat.id)}
                style={{
                  marginLeft: 5,
                  color: "red",
                  background: "none",
                  border: "none",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
                title="Delete Chat"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* Chat Window */}
      <div
        style={{
          flex: 1,
          padding: 10,
          display: "flex",
          flexDirection: "column",
        }}
      >
        {!selectedChatId ? (
          <p>Select a chat or create a new one</p>
        ) : (
          <>
            <div
              style={{
                flex: 1,
                overflowY: "scroll",
                border: "1px solid #ccc",
                padding: 10,
              }}
            >
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  style={{
                    padding: 5,
                    textAlign: msg.sender === "user" ? "right" : "left",
                    margin: "6px 0",
                  }}
                >
                  {msg.sender === "assistant" && msg.text.includes("Month") ? (
                    <div
                      style={{ display: "flex", flexDirection: "column", gap: "10px" }}
                    >
                      {msg.text
                        .split("Month")
                        .filter(Boolean)
                        .map((entry, idx) => {
                          const parts = entry.trim().split(",");
                          const month = entry.trim().split(":")[0];
                          const phone = parts
                            .find((p) => p.includes("Phone charge"))
                            ?.trim();
                          const internet = parts
                            .find((p) => p.includes("Internet charge"))
                            ?.trim();
                          const total = parts
                            .find((p) => p.includes("Total"))
                            ?.trim();
                          const status = parts
                            .find((p) => p.includes("Status"))
                            ?.trim();
                          const isPaid = status?.toLowerCase().includes("status: paid");

                          return (
                            <div
                              key={idx}
                              style={{
                                backgroundColor: isPaid ? "#e8f5e9" : "#ffebee",
                                padding: "10px",
                                borderRadius: "10px",
                                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                                maxWidth: "400px",
                              }}
                            >
                              <div
                                style={{ fontWeight: "bold", marginBottom: 4 }}
                              >{`Month ${month}`}</div>
                              <div>{phone}</div>
                              <div>{internet}</div>
                              <div>{total}</div>
                              <div>
                                Status:{" "}
                                <span style={{ fontWeight: "bold" }}>
                                  {isPaid ? "Paid ✅" : "Unpaid ❌"}
                                </span>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  ) : (
                    <div
                      style={{
                        backgroundColor:
                          msg.sender === "user" ? "#DCF8C6" : "#FFF",
                        borderRadius: 8,
                        padding: 8,
                        maxWidth: "70%",
                        marginLeft: msg.sender === "user" ? "auto" : 0,
                        boxShadow: "0 1px 2px rgba(0,0,0,0.1)",
                      }}
                    >
                      <b>{msg.sender === "user" ? "You" : "Assistant"}:</b>{" "}
                      {msg.text}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <div>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Type your message"
                style={{ width: "80%" }}
                disabled={sending}
              />
              <button onClick={sendMessage} disabled={sending}>
                {sending ? "Sending..." : "Send"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
