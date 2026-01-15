import { motion } from "framer-motion";

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        width: "100%",
        padding: "14px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        borderBottom: "1px solid var(--border)",
        background: "rgba(255,255,255,0.85)",
        backdropFilter: "blur(6px)",
        position: "sticky",
        top: 0,
        zIndex: 100
      }}
    >
      {/* LEFT: LOGO + NAME */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12
        }}
      >
        {/* LOGO PLACEHOLDER */}
        <div
          style={{
            width: 38,
            height: 38,
            borderRadius: 10,
            background: "var(--primary-soft)",
            display: "grid",
            placeItems: "center",
            fontWeight: 700,
            color: "var(--primary)"
          }}
        >
          A
        </div>

        <div>
          <h3 style={{ fontSize: 18 }}>AIMS-DS</h3>
          {/* <p style={{ fontSize: 12 }}>
            AI-based Interview & Mental State Detection System
          </p> */}
        </div>
      </div>

      {/* RIGHT: TAG */}
      <span
        className="badge info"
        style={{ fontSize: 13 }}
      >
        SET Conference
      </span>
    </motion.header>
  );
}
