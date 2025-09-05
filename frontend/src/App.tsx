
import React, { useState, useEffect } from "react";
import "./App.css";

interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
}

interface Session {
  id: string;
  name: string;
  messages: Message[];
}


function App() {
  // User modal state
  const [showModal, setShowModal] = useState(true);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [userId, setUserId] = useState<string>("");

  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>("");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<{ title: string; url: string }[]>([]);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  // Fetch sessions on mount (after user info entered)
  useEffect(() => {
    if (!userId) return;
    const fetchSessions = async () => {
      try {
        const res = await fetch(`http://localhost:8000/sessions/?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to fetch sessions");
        const data = await res.json();
        const sessionsWithMessages = data.map((s: any) => ({ ...s, messages: [] }));
        setSessions(sessionsWithMessages);
        if (sessionsWithMessages.length > 0) {
          setActiveSessionId(sessionsWithMessages[0].id);
        }
      } catch (err) {
        setSessions([]);
      }
    };
    fetchSessions();
  }, [userId]);

  // Fetch history when active session changes
  useEffect(() => {
    if (!activeSessionId || !userId) return;
    const fetchHistory = async () => {
      try {
        const res = await fetch(`http://localhost:8000/sessions/${activeSessionId}/history`);
        if (!res.ok) throw new Error("Failed to fetch history");
        const data = await res.json();
        setSessions((prev) =>
          prev.map((session) =>
            session.id === activeSessionId
              ? { ...session, messages: data.messages }
              : session
          )
        );
      } catch (err) {
        // ignore
      }
    };
    fetchHistory();
  }, [activeSessionId, userId]);

  const handleSend = async () => {
    if (!input.trim() || !activeSession) return;
    const newMessage: Message = {
      id: Math.random().toString(36).slice(2),
      role: "user",
      content: input,
    };
    setSessions((prev) =>
      prev.map((session) =>
        session.id === activeSessionId
          ? { ...session, messages: [...session.messages, newMessage] }
          : session
      )
    );
    setInput("");
    setLoading(true);
    setSources([]);
    try {
      const res = await fetch("http://localhost:8000/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          session_id: activeSessionId,
          query: newMessage.content,
        }),
      });
      if (!res.ok) throw new Error("Network error");
      const data = await res.json();
      const assistantMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: data.answer,
      };
      setSessions((prev) =>
        prev.map((session) =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, assistantMsg] }
            : session
        )
      );
      setSources(data.sources || []);
    } catch (err) {
      const errorMsg: Message = {
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: "Error: Unable to get response.",
      };
      setSessions((prev) =>
        prev.map((session) =>
          session.id === activeSessionId
            ? { ...session, messages: [...session.messages, errorMsg] }
            : session
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleNewSession = async () => {
    try {
      const res = await fetch("http://localhost:8000/sessions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId }),
      });
      if (!res.ok) throw new Error("Failed to create session");
      const data = await res.json();
      const newSession: Session = { ...data, messages: [] };
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSession.id);
    } catch (err) {
      // ignore
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/sessions/${sessionId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Failed to delete session");
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId && sessions.length > 1) {
        setActiveSessionId(sessions[0].id);
      }
    } catch (err) {
      // ignore
    }
  };

  const handleModalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !username.trim()) return;
    try {
      const res = await fetch("http://localhost:8000/user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), username: username.trim() }),
      });
      if (!res.ok) throw new Error("Failed to create user");
      const data = await res.json();
      setUserId(data.id); // Save user id from backend
      setShowModal(false);
    } catch (err) {
      alert("Failed to create or fetch user. Please try again.");
    }
  };

  return (
    <>
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Enter your details</h2>
            <form onSubmit={handleModalSubmit} className="modal-form">
              <label>
                Email:
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </label>
              <label>
                Username:
                <input
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                />
              </label>
              <button type="submit">Continue</button>
            </form>
          </div>
        </div>
      )}
      {!showModal && (
        <div className="chat-app">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Sessions</h2>
          <button onClick={handleNewSession}>+</button>
        </div>
        <ul className="session-list">
          {sessions.map((session) => (
            <li
              key={session.id}
              className={session.id === activeSessionId ? "active" : ""}
              onClick={() => setActiveSessionId(session.id)}
            >
              <span>{session.name}</span>
              <button
                className="delete-session"
                onClick={e => { e.stopPropagation(); handleDeleteSession(session.id); }}
                title="Delete session"
              >×</button>
            </li>
          ))}
        </ul>
      </aside>
      <main className="chat-main">
        <div className="chat-header">
          <h2>{activeSession?.name}</h2>
        </div>
        <div className="chat-messages">
          {activeSession?.messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role}`}>
              <span className="role">{msg.role === "user" ? "You" : "Assistant"}:</span>
              <span className="content">{msg.content}</span>
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()}>
            {loading ? "..." : "Send"}
          </button>
        </div>
        {sources.length > 0 && (
          <div className="chat-sources">
            <div className="sources-title">Sources:</div>
            <ul>
              {sources.map((src, idx) => (
                <li key={idx}><a href={src.url} target="_blank" rel="noopener noreferrer">{src.title}</a></li>
              ))}
            </ul>
          </div>
        )}
      </main>
        </div>
      )}
    </>
  );
}

export default App;
