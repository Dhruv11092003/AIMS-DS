import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import Loader from "../components/Loader";
import { SessionAPI } from "../api/sessionApi";
import { motion } from "framer-motion";

/**
 * MCQ Component
 *
 * Supports:
 * - Baseline MCQs (all at once)
 * - RL MCQs (single adaptive question)
 */

// Authoritative PHQ options
const PHQ_OPTIONS = [
  { value: 0, label: "Not at all" },
  { value: 1, label: "Several days" },
  { value: 2, label: "More than half the days" },
  { value: 3, label: "Nearly every day" }
];

export default function MCQ({ sessionId, onNext, data }) {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setAnswers({});

      // -----------------------------
      // RL MCQ (single question)
      // -----------------------------
      if (data?.question) {
        setQuestions([data.question]);
        setLoading(false);
        return;
      }

      // -----------------------------
      // BASELINE MCQs (fetch once)
      // -----------------------------
      if (data?.mode === "baseline") {
        const res = await SessionAPI.getMcqs();
        setQuestions(res.questions || []);
        setLoading(false);
        return;
      }

      setQuestions([]);
      setLoading(false);
    }

    load();
  }, [data]);

  function selectAnswer(questionId, value) {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value
    }));
  }

  async function submit() {
    setSubmitting(true);
    await SessionAPI.submitMcqs(sessionId, answers);
    await onNext(); // calls /next-question
    setSubmitting(false);
  }

  if (loading) {
    return <Loader text="Loading questions…" />;
  }

  return (
    <>
      <Layout
        title="Psychometric Assessment"
        subtitle="Please answer the following questions honestly"
      >
        {questions.map((q, index) => {
          const questionId = q.id;
          const questionText = q.question;

          // Normalize options
          const options = Array.isArray(q.options)
            ? q.options.map((v) =>
                PHQ_OPTIONS.find((o) => o.value === v)
              )
            : PHQ_OPTIONS;

          return (
            <motion.div
              key={`mcq-${questionId}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="card"
              style={{ marginBottom: 24 }}
            >
              <span className="badge info">
                Question {questionId}
              </span>

              <p
                style={{
                  fontSize: 17,
                  fontWeight: 600,
                  margin: "16px 0"
                }}
              >
                {questionText}
              </p>

              <div style={{ display: "grid", gap: 12 }}>
                {options.map((opt) => {
                  const selected =
                    answers[questionId] === opt.value;

                  return (
                    <motion.label
                      key={`opt-${questionId}-${opt.value}`}
                      whileHover={{ scale: 1.02 }}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        padding: 12,
                        borderRadius: 10,
                        border: "1px solid var(--border)",
                        cursor: "pointer",
                        background: selected
                          ? "rgba(99,102,241,0.08)"
                          : "transparent"
                      }}
                    >
                      <input
                        type="radio"
                        name={`q-${questionId}`}
                        checked={selected}
                        onChange={() =>
                          selectAnswer(questionId, opt.value)
                        }
                      />
                      {opt.label}
                    </motion.label>
                  );
                })}
              </div>
            </motion.div>
          );
        })}

        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          disabled={
            Object.keys(answers).length !== questions.length ||
            submitting
          }
          onClick={submit}
          className="primary"
          style={{ width: "100%", marginTop: 16 }}
        >
          Submit Responses
        </motion.button>
      </Layout>

      {submitting && <Loader text="Analyzing your responses…" />}
    </>
  );
}
