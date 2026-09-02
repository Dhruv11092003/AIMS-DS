import { useEffect, useState } from "react";
import Landing from "./pages/Landing";
import VideoQuestion from "./pages/VideoQuestion";
import MCQ from "./pages/MCQ";
import Finalize from "./pages/Finalize";
import { SessionAPI } from "./api/sessionApi";
import Loader from "./components/Loader";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [current, setCurrent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /* ===== Restore session on reload ===== */
  useEffect(() => {
    const savedSession = sessionStorage.getItem("session_id");
    const savedStep = sessionStorage.getItem("current_step");

    if (savedSession && savedStep) {
      setSessionId(savedSession);
      setCurrent(JSON.parse(savedStep));
    } else {
      setCurrent({ type: "landing" });
    }

    setLoading(false);
  }, []);

  /* ===== Persist session ===== */
  function persist(sid, step) {
    sessionStorage.setItem("session_id", sid);
    sessionStorage.setItem("current_step", JSON.stringify(step));
  }

  async function fetchNext(sid) {
    if (!sid) return;

    setLoading(true);
    setError(null);
    try {
      const step = await SessionAPI.nextQuestion(sid);
      setCurrent(step);
      persist(sid, step);
    } catch (err) {
      setError(err.message || "Couldn't reach the server. Please retry.");
    } finally {
      setLoading(false);
    }
  }

  function exitSession() {
    sessionStorage.clear();
    setSessionId(null);
    setCurrent({ type: "landing" });
    setError(null);
  }

  if (loading || !current) {
    return <Loader text="Restoring session…" />;
  }

  if (error) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          padding: 24
        }}
      >
        <div className="card" style={{ maxWidth: 420, textAlign: "center" }}>
          <h3 style={{ marginBottom: 10 }}>Something went wrong</h3>
          <p style={{ marginBottom: 20 }}>{error}</p>
          <button
            className="primary"
            onClick={() => {
              setError(null);
              if (sessionId) fetchNext(sessionId);
              else setCurrent({ type: "landing" });
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (current.type === "landing") {
    return (
      <Landing
        onStart={async (username) => {
          setError(null);
          try {
            const res = await SessionAPI.createSession(username);
            const sid = res.session_id;

            setSessionId(sid);
            await fetchNext(sid);
          } catch (err) {
            setError(err.message || "Couldn't start a session. Please retry.");
          }
        }}
      />
    );
  }

  if (current.type === "video") {
    return (
      <VideoQuestion
        data={current}
        sessionId={sessionId}
        onNext={() => fetchNext(sessionId)}
        onExit={exitSession}
      />
    );
  }

  if (current.type === "mcq") {
    return (
      <MCQ
        data={current}            // 🔥 PASS MCQ DATA
        sessionId={sessionId}
        onNext={() => fetchNext(sessionId)}
        onExit={exitSession}
      />
    );
  }


  if (current.type === "finalize") {
    return (
      <Finalize
        sessionId={sessionId}
        onExit={exitSession}
        debugHint={current.debug}
      />
    );
  }

  return null;
}
