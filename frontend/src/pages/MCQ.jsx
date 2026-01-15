import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import Loader from "../components/Loader";
import { SessionAPI } from "../api/sessionApi";
import { motion } from "framer-motion";

export default function MCQ({ sessionId, onNext }) {
  const [questions, setQuestions] = useState([]);
  const [options, setOptions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      const res = await SessionAPI.getMcqs();
      setQuestions(res.questions || []);
      setOptions(res.options || []);
      setLoading(false);
    }
    load();
  }, []);

  function selectAnswer(qid, value) {
    setAnswers((prev) => ({
      ...prev,
      [qid]: value
    }));
  }

  async function submit() {
    setSubmitting(true);
    await SessionAPI.submitMcqs(sessionId, answers);
    await onNext();
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
        {questions.map((q, index) => (
          <motion.div
            key={q.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="card"
            style={{ marginBottom: 24 }}
          >
            {/* Question Header */}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 14,
                flexWrap: "wrap",
                gap: 8
              }}
            >
              <span className="badge info">
                Question {q.id}
              </span>

              <span
                style={{
                  fontSize: 13,
                  color: "var(--muted)"
                }}
              >
                Difficulty: {q.difficulty}
              </span>
            </div>

            {/* Question Text */}
            <p
              style={{
                fontSize: 17,
                fontWeight: 600,
                marginBottom: 18
              }}
            >
              {q.question}
            </p>

            {/* Options */}
            <div
              style={{
                display: "grid",
                gap: 12
              }}
            >
              {options.map((opt) => {
                const selected = answers[q.id] === opt.value;

                return (
                  <motion.label
                    key={opt.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      padding: "14px 16px",
                      borderRadius: 14,
                      border: `1px solid ${
                        selected
                          ? "var(--primary)"
                          : "var(--border)"
                      }`,
                      background: selected
                        ? "var(--primary-soft)"
                        : "#fff",
                      cursor: "pointer"
                    }}
                  >
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      checked={selected}
                      onChange={() =>
                        selectAnswer(q.id, opt.value)
                      }
                    />

                    <span style={{ fontSize: 15 }}>
                      {opt.label}
                    </span>
                  </motion.label>
                );
              })}
            </div>
          </motion.div>
        ))}

        {/* Submit Button */}
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          disabled={
            Object.keys(answers).length !== questions.length ||
            submitting
          }
          onClick={submit}
          className="primary"
          style={{
            width: "100%",
            marginTop: 12
          }}
        >
          Submit Responses
        </motion.button>

        <p
          style={{
            fontSize: 13,
            textAlign: "center",
            marginTop: 10,
            color: "var(--muted)"
          }}
        >
          ⓘ All questions must be answered before submission.
        </p>
      </Layout>

      {/* Background Loader */}
      {submitting && <Loader text="Analyzing your responses…" />}
    </>
  );
}
