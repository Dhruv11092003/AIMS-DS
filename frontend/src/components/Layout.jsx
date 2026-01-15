import { motion } from "framer-motion";

export default function Layout({ children, title, subtitle }) {
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
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        style={{
          width: "100%",
          maxWidth: 760
        }}
      >
        <div className="card">
          {title && (
            <div style={{ marginBottom: 18 }}>
              <h1 style={{ fontSize: 26 }}>{title}</h1>
              {subtitle && (
                <p style={{ marginTop: 6 }}>{subtitle}</p>
              )}
            </div>
          )}

          {children}
        </div>
      </motion.div>
    </div>
  );
}
