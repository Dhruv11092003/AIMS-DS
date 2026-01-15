import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import Loader from "../components/Loader";
import { SessionAPI } from "../api/sessionApi";
import { motion } from "framer-motion";

function MetricCard({ label, value }) {
  return (
    <div
      className="card"
      style={{
        flex: 1,
        textAlign: "center",
        padding: 20
      }}
    >
      <p style={{ fontSize: 14, marginBottom: 6 }}>{label}</p>
      <h3 style={{ fontSize: 22 }}>
        {(value * 100).toFixed(1)}%
      </h3>
    </div>
  );
}

function ConfidenceBar({ label, value }) {
  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: 6
        }}
      >
        <span>{label}</span>
        <strong>{(value * 100).toFixed(1)}%</strong>
      </div>

      <div
        style={{
          height: 10,
          borderRadius: 6,
          background: "var(--primary-soft)"
        }}
      >
        <div
          style={{
            width: `${value * 100}%`,
            height: "100%",
            borderRadius: 6,
            background: "var(--primary)"
          }}
        />
      </div>
    </div>
  );
}

export default function Finalize({ sessionId, onExit }) {
  const [result, setResult] = useState(null);

  useEffect(() => {
    async function load() {
      const res = await SessionAPI.finalize(sessionId);
      setResult(res);
    }
    load();
  }, [sessionId]);

  if (!result) {
    return <Loader text="Generating final assessment report…" />;
  }

  const {
    final_class,
    final_confidence,
    behavioral_confidence,
    mcq_score,
    mcq_uncertainty,
    explanation
  } = result;

  return (
    <Layout
      title="Final Assessment Report"
      subtitle="AIMS-DS — AI-Based Multimodal Interview & Screening System"
    >
      {/* ===== Predicted Class ===== */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        style={{
          padding: 24,
          borderRadius: 20,
          background: "var(--primary-soft)",
          textAlign: "center",
          marginBottom: 28
        }}
      >
        <p style={{ fontSize: 14, marginBottom: 6 }}>
          Final Predicted Class
        </p>
        <h2 style={{ fontSize: 32 }}>{final_class}</h2>
      </motion.div>

      {/* ===== Metric Cards ===== */}
      <div
        style={{
          display: "flex",
          gap: 16,
          flexWrap: "wrap",
          marginBottom: 28
        }}
      >
        <MetricCard
          label="Final Confidence"
          value={final_confidence}
        />
        <MetricCard
          label="Behavioral Confidence"
          value={behavioral_confidence}
        />
        <MetricCard
          label="MCQ Score"
          value={mcq_score}
        />
        <MetricCard
          label="MCQ Uncertainty"
          value={mcq_uncertainty}
        />
      </div>

      {/* ===== Confidence Visualization ===== */}
      <div
        className="card"
        style={{ marginBottom: 28 }}
      >
        <h3 style={{ marginBottom: 16 }}>
          Confidence Breakdown
        </h3>

        <ConfidenceBar
          label="Behavioral (Video)"
          value={behavioral_confidence}
        />
        <ConfidenceBar
          label="Psychometric (MCQ)"
          value={mcq_score}
        />
        <ConfidenceBar
          label="Final Combined Confidence"
          value={final_confidence}
        />
      </div>

      {/* ===== Decision Explanation ===== */}
      <div className="card">
        <h3 style={{ marginBottom: 12 }}>
          Decision Explanation
        </h3>

        <p style={{ marginBottom: 8 }}>
          <strong>Decision Rule:</strong>{" "}
          {explanation?.decision_rule}
        </p>

        <p>
          The final confidence score is computed using a weighted
          fusion of video-based behavioral confidence and
          psychometric MCQ scoring.
        </p>

        <p style={{ marginTop: 8 }}>
          <strong>Fusion Weights:</strong>  
          Video = {explanation?.fusion_weight},  
          MCQ = {explanation?.mcq_weight}
        </p>
      </div>

      {/* ===== Exit Button (ONLY HERE) ===== */}
      <div
        style={{
          marginTop: 40,
          display: "flex",
          justifyContent: "center"
        }}
      >
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          className="primary"
          onClick={onExit}
          style={{ maxWidth: 260 }}
        >
          Exit Session & Return Home
        </motion.button>
      </div>
    </Layout>
  );
}
