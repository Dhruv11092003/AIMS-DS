import { useState } from "react";
import { motion } from "framer-motion";
import Header from "../components/Header";

export default function Landing({ onStart }) {
  const [username, setUsername] = useState("");

  return (
    <>
    <Header />
    <div style={{ minHeight: "100vh", width: "100%", padding: "48px 20px", display: "flex", flexDirection: "column", gap: 72 }}>
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        padding: "10px 20px",
        display: "flex",
        flexDirection: "column",
        gap: 72
      }}
    >
      {/* ================= HERO ================= */}
      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap:40,
          alignItems: "center"
          // border:"1px solid black"  
        }}
      >
        {/* TEXT */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}

        >
          {/* <span
            style={{
              display: "inline-block",
              padding: "6px 14px",
              borderRadius: 999,
              background: "var(--primary-soft)",
              color: "var(--primary)",
              fontSize: 14,
              fontWeight: 600,
              marginBottom: 16
            }}
          >
            SET Conference Project
          </span> */}

          <h1
            style={{
              fontSize: "clamp(32px, 4.5vw, 42px)",
              marginBottom: 16
            }}
          >
            AIMS-DS: Adaptive Interview & Mental State Detection System
          </h1>

          <p
            style={{
              maxWidth: 560,
              fontSize: 17,
              marginBottom: 24
            }}
          >
            AIMS-DS is a research-oriented system that combines
video-based behavioral analysis, psychometric MCQs,
and reinforcement learning to assess confidence,
emotional stability, and response consistency.

          </p>

          <ul style={{ marginBottom: 28 }}>
            <li>🎥 Multimodal video confidence analysis</li>
            <li>📝 Adaptive psychometric MCQs</li>
            <li>🧠 AI-based fusion with RL</li>
          </ul>

          <div
            style={{
              maxWidth: 360,
              display: "flex",
              flexDirection: "column",
              gap: 14
            }}
          >
            <input
              placeholder="Enter your name to begin"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                padding: 14,
                borderRadius: 12,
                border: "1px solid var(--border)"
              }}
            />

            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="primary"
              disabled={!username}
              onClick={() => onStart(username)}
            >
              Start Interview Session
            </motion.button>

            <p style={{ fontSize: 13 }}>
              ℹ Camera and microphone permission required
            </p>
          </div>
        </motion.div>

        {/* HERO IMAGE */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          style={{
            width: "100%",
            minHeight: 300,
            borderRadius: 28,
            // background:
            //   "linear-gradient(135deg, var(--primary-soft), #eef2ff)",
            display: "grid",
            placeItems: "center"
          }}
        >
      <img src="/1.png" style={{ width: "100%" }} />

        </motion.div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section>
        <h2 style={{ marginBottom: 24 }}>How the System Works</h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 24
          }}
        >
          {[
            {
              title: "Video Interview",
              desc: "Speech patterns, behavioral cues, and confidence metrics are extracted from recorded video responses."
            },
            {
              title: "Psychometric MCQs",
              desc: "Scientifically designed Likert-scale questions assess emotional and cognitive consistency."
            },
            {
              title: "AI Fusion & RL",
              desc: "Multimodal signals are fused using weighted confidence rules and reinforcement learning."
            }
          ].map((item, i) => (
            <motion.div
              key={i}
              whileHover={{ y: -8 }}
              transition={{ type: "spring", stiffness: 180 }}
              className="card"
            >
              <h3 style={{ marginBottom: 10 }}>{item.title}</h3>
              <p>{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ================= METHODOLOGY ================= */}
      <div style={{display:"flex",justifyContent:"center",alignItems:"center"}}>
      <section
        style={{
          background: "var(--primary-soft)",
          borderRadius: 32,
          width:"800px",
          padding: "48px 24px",
          // display:"flex",
          // justifyContent:"center",
          // flexDirection:"column",
          textAlign: "center"
        }}
      >
        <h2 style={{ marginBottom: 14 }}>Methodology Overview</h2>
        <p style={{ maxWidth: 720, margin: "0 auto 28px" }}>
          Multimodal fusion pipeline integrating video analytics,
          psychometric scoring, and reinforcement learning for
          robust behavioral assessment.
        </p>

        <div
          style={{
            width:"100%",
            maxWidth: "400px",
            height: "100%",
            margin: "0 auto",
            background: "#ffffff",
            borderRadius: 20,
            display: "grid",
            alignItems:"center"
            // placeItems: "center"
          }}
        >
         <img src="./methodology.jpg" style={{ width: "400px" }}/>

        </div>
      </section>
    </div>
      {/* ================= CREDITS ================= */}
      <section style={{ textAlign: "center", fontSize: 15 }}>
        <p>
          <strong>Guided By:</strong> Dr. Vanitha M  
          <br />
          Professor Grade 1, VIT Vellore
        </p>

        <p style={{ marginTop: 12 }}>
          <strong>Developed By:</strong>
          <br />
          Dhruv Kulshrestha (25MAG0018)
          <br />
          Shaikh Imran Mustafa Rihana (25MAG0036)
        </p>
      </section>
      
    </div>
    </div>
    </>
  );
  
}

