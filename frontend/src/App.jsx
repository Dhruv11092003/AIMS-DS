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
    const step = await SessionAPI.nextQuestion(sid);
    setCurrent(step);
    persist(sid, step);
    setLoading(false);
  }

  function exitSession() {
    sessionStorage.clear();
    setSessionId(null);
    setCurrent({ type: "landing" });
  }

  if (loading || !current) {
    return <Loader text="Restoring session…" />;
  }

  if (current.type === "landing") {
    return (
      <Landing
        onStart={async (username) => {
          const res = await SessionAPI.createSession(username);
          const sid = res.session_id;

          setSessionId(sid);
          await fetchNext(sid);
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
    return <Finalize sessionId={sessionId} onExit={exitSession} />;
  }

  return null;
}
