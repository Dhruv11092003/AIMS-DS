import { http } from "./http";

const BASE = import.meta.env.VITE_API_BASE_URL;

export const SessionAPI = {
  createSession(username) {
    return http(`${BASE}/create`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username })
    });
  },

  nextQuestion(sessionId) {
    return http(`${BASE}/session/${sessionId}/next-question`);
  },

  submitVideo(sessionId, questionId, file) {
    const form = new FormData();
    form.append("video", file);

    return fetch(`${BASE}/session/${sessionId}/question/${questionId}/submit`, {
      method: "POST",
      body: form
    });
  },

  getMcqs() {
    return http(`${BASE}/session/questions`);
  },

  submitMcqs(sessionId, mcqAnswers) {
    return http(`${BASE}/session/${sessionId}/mcq/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        mcq_answers: JSON.stringify(mcqAnswers)
      })
    });
  },

  finalize(sessionId) {
    return http(`${BASE}/session/${sessionId}/finalize`, {
      method: "POST"
    });
  }
};
