import { useRef } from "react";
import { motion } from "framer-motion";
import useRecorder from "../hooks/useRecorder";

export default function Recorder({ onSubmit }) {
  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  const { recording, startRecording, stopRecording } = useRecorder();

  async function handleStop() {
    const blob = await stopRecording();
    onSubmit(blob);
  }

  function handleFileUpload(e) {
    const file = e.target.files[0];
    if (file) onSubmit(file);
  }

  return (
    <div style={{ width: "100%" }}>
      {/* ===== Video Preview ===== */}
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        style={{
          width: "100%",
          borderRadius: 16,
          border: "1px solid var(--border)",
          background: "#000",
          marginBottom: 16
        }}
      />

      {/* ===== Controls ===== */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 14,
          justifyContent: "center"
        }}
      >
        {/* RECORD / STOP BUTTON */}
        {!recording ? (
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => startRecording(videoRef.current)}
            style={{
              padding: "12px 22px",
              borderRadius: 999,
              background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
              color: "#fff",
              fontSize: 15,
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: 10
            }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: "#fff"
              }}
            />
            Start Recording
          </motion.button>
        ) : (
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleStop}
            style={{
              padding: "12px 22px",
              borderRadius: 999,
              background: "linear-gradient(135deg, #dc2626, #b91c1c)",
              color: "#fff",
              fontSize: 15,
              fontWeight: 600,
              display: "flex",
              alignItems: "center",
              gap: 10
            }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: "#fff",
                animation: "pulse 1.2s infinite"
              }}
            />
            Stop & Submit
          </motion.button>
        )}

        {/* UPLOAD BUTTON */}
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => fileInputRef.current.click()}
          style={{
            padding: "12px 22px",
            borderRadius: 999,
            background: "#ffffff",
            border: "1px solid var(--border)",
            color: "var(--text)",
            fontSize: 15,
            fontWeight: 500
          }}
        >
          Upload Video Instead
        </motion.button>

        <input
          type="file"
          accept="video/*"
          hidden
          ref={fileInputRef}
          onChange={handleFileUpload}
        />
      </div>

      {/* ===== Recording Hint ===== */}
      {recording && (
        <p
          style={{
            marginTop: 14,
            fontSize: 13,
            textAlign: "center",
            color: "var(--danger)"
          }}
        >
          ● Recording in progress…
        </p>
      )}

      {/* Pulse animation */}
      <style>
        {`
          @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
}
