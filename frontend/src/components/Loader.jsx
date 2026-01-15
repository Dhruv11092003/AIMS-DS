import { motion } from "framer-motion";

export default function Loader({ text = "Processing, please wait…" }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        padding: 24
      }}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="card"
        style={{
          width: 320,
          textAlign: "center"
        }}
      >
        <div
          style={{
            width: 44,
            height: 44,
            border: "4px solid var(--primary-soft)",
            borderTop: "4px solid var(--primary)",
            borderRadius: "50%",
            margin: "0 auto 16px",
            animation: "spin 1s linear infinite"
          }}
        />

        <p style={{ fontSize: 15 }}>{text}</p>

        <style>
          {`
            @keyframes spin {
              to {
                transform: rotate(360deg);
              }
            }
          `}
        </style>
      </motion.div>
    </div>
  );
}
