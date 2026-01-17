import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import Loader from "../components/Loader";
import { SessionAPI } from "../api/sessionApi";
import { motion } from "framer-motion";

/* =======================
   Reusable UI Components
======================= */

function MetricCard({ label, value, suffix = "%" }) {
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
        {typeof value === "number"
          ? `${value.toFixed(1)}${suffix}`
          : value}
      </h3>
    </div>
  );
}

function ConfidenceBar({ label, value }) {
  const pct = Math.max(0, Math.min(100, value * 100));

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
        <strong>{pct.toFixed(1)}%</strong>
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
            width: `${pct}%`,
            height: "100%",
            borderRadius: 6,
            background: "var(--primary)"
          }}
        />
      </div>
    </div>
  );
}

/* =======================
   Finalize Screen
======================= */

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
    return <Loader text="Generating final Bayesian assessment…" />;
  }

  const {
    final_class,
    final_probabilities,
    uncertainty_level,
    diagnostics
  } = result;

  const {
    behavioral_probabilities,
    psychometric_probabilities,
    disagreement_kl,
    mcq_uncertainty
  } = diagnostics || {};

  const uncertaintyHigh = uncertainty_level > 0.7;
  const disagreementHigh = disagreement_kl > 1.0;

  return (
    <Layout
      title="Final Assessment Report"
      subtitle="AIMS-DS — Bayesian Multimodal Mental Health Screening"
    >
      {/* ===== Final Class ===== */}
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
          Final Predicted Severity
        </p>
        <h2 style={{ fontSize: 32 }}>{final_class}</h2>

        {uncertaintyHigh && (
          <p
            style={{
              marginTop: 10,
              fontSize: 13,
              color: "#b45309"
            }}
          >
            ⚠️ High Uncertainty — Further Review Recommended
          </p>
        )}
      </motion.div>

      {/* ===== Core Metrics ===== */}
      <div
        style={{
          display: "flex",
          gap: 16,
          flexWrap: "wrap",
          marginBottom: 28
        }}
      >
        <MetricCard
          label="Overall Uncertainty (Entropy)"
          value={uncertainty_level * 100}
        />
        <MetricCard
          label="MCQ Uncertainty"
          value={mcq_uncertainty * 100}
        />
        <MetricCard
          label="Behavioral–Psychometric Disagreement (KL)"
          value={disagreement_kl}
          suffix=""
        />
      </div>

      {/* ===== Severity Distribution ===== */}
      <div className="card" style={{ marginBottom: 28 }}>
        <h3 style={{ marginBottom: 16 }}>
          Severity Probability Distribution
        </h3>

        <ConfidenceBar
          label="Low Severity"
          value={final_probabilities?.Low || 0}
        />
        <ConfidenceBar
          label="Moderate Severity"
          value={final_probabilities?.Moderate || 0}
        />
        <ConfidenceBar
          label="High Severity"
          value={final_probabilities?.High || 0}
        />
      </div>

      {/* ===== Modality Comparison ===== */}
      <div className="card" style={{ marginBottom: 28 }}>
        <h3 style={{ marginBottom: 16 }}>
          Evidence Comparison
        </h3>

        <p style={{ fontSize: 14, marginBottom: 10 }}>
          <strong>Behavioral (Video)</strong>
        </p>
        <ConfidenceBar
          label="Low"
          value={behavioral_probabilities?.Low || 0}
        />
        <ConfidenceBar
          label="Moderate"
          value={behavioral_probabilities?.Moderate || 0}
        />
        <ConfidenceBar
          label="High"
          value={behavioral_probabilities?.High || 0}
        />

        <hr style={{ margin: "16px 0" }} />

        <p style={{ fontSize: 14, marginBottom: 10 }}>
          <strong>Psychometric (PHQ-8)</strong>
        </p>
        <ConfidenceBar
          label="Low"
          value={psychometric_probabilities?.Low || 0}
        />
        <ConfidenceBar
          label="Moderate"
          value={psychometric_probabilities?.Moderate || 0}
        />
        <ConfidenceBar
          label="High"
          value={psychometric_probabilities?.High || 0}
        />

        {disagreementHigh && (
          <p
            style={{
              marginTop: 12,
              fontSize: 13,
              color: "#991b1b"
            }}
          >
            ⚠️ Significant discrepancy detected between behavioral
            signals and self-report.
          </p>
        )}
      </div>

      {/* ===== Exit ===== */}
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
