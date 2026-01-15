import { useState } from "react";
import Layout from "../components/Layout";
import Recorder from "../components/Recorder";
import Loader from "../components/Loader";
import { SessionAPI } from "../api/sessionApi";
import { motion, AnimatePresence } from "framer-motion";

export default function VideoQuestion({ data, sessionId, onNext }) {
  const [submitting, setSubmitting] = useState(false);

  const questionText = data?.question?.text || "";
  const questionId = data?.question?.id;

  async function handleSubmit(file) {
    if (submitting) return;

    setSubmitting(true);

    try {
      await SessionAPI.submitVideo(
        sessionId,
        questionId,
        file
      );
      await onNext();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <Layout
        title="Video Interview"
        subtitle="Please answer the question clearly and honestly"
      >
        {/* ===== Question Header ===== */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 16,
            flexWrap: "wrap",
            gap: 10
          }}
        >
          {questionId && (
            <span className="badge info">
              Question {questionId}
            </span>
          )}

          <span
            style={{
              fontSize: 14,
              color: "var(--muted)"
            }}
          >
            🎥 Video Response Required
          </span>
        </div>

        {/* ===== Question Text ===== */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          style={{
            padding: "20px 22px",
            borderRadius: 16,
            background: "var(--primary-soft)",
            marginBottom: 28
          }}
        >
          <p
            style={{
              fontSize: 18,
              fontWeight: 600,
              color: "var(--text)"
            }}
          >
            {questionText}
          </p>
        </motion.div>

        {/* ===== Recorder ===== */}
        <Recorder onSubmit={handleSubmit} />

        {/* ===== Info Text ===== */}
        <p
          style={{
            fontSize: 13,
            marginTop: 14,
            color: "var(--muted)"
          }}
        >
          ⓘ Your response will be uploaded automatically once recording stops.
        </p>
      </Layout>

      {/* ===== Background Loader Overlay ===== */}
      <AnimatePresence>
        {submitting && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(255,255,255,0.7)",
              backdropFilter: "blur(4px)",
              zIndex: 999
            }}
          >
            <Loader text="Processing your response…" />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
