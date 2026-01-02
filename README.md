# AIMS-DS 

# AIMS-DS Backend

**Adaptive Interview & Mental State Detection System (Backend)**

---

## 1. Overview

AIMS-DS is a **session-based multimodal assessment backend** designed to:

* Collect **video responses** from users
* Extract **audio, video, and text features**
* Perform **multimodal fusion inference** for mental health classification
* Ask **baseline MCQs (PHQ-style)**
* Adaptively ask **additional MCQs or video questions using Reinforcement Learning (RL)**
* Produce a **final confidence-aware classification**:

  * **Low**
  * **Moderate**
  * **High**

The backend is **fully API-driven** and intended to be used with a frontend (web/mobile).
The final output classes (Low, Moderate, High) represent **depression severity levels**,
derived from multimodal behavioral analysis and standardized self-assessment scores.

---

## 2. High-Level System Flow

```
Session Created
      ↓
Baseline Video Questions (3–5)
      ↓
Baseline MCQs (PHQ-style)
      ↓
Multimodal Fusion Inference
      ↓
Confidence Check
      ↓
IF confidence ≥ threshold (0.65)
      → Finalize
ELSE
      → Reinforcement Learning (Adaptive Questions)
            ↓
        Video OR MCQ (chosen by RL)
            ↓
        Recompute confidence
            ↓
        Stop when confident OR exhausted
      ↓
Final Decision
```

---

## 3. Project Structure (Backend)

```
AIMS-DS/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │   # FastAPI application entry point
│   │   │   # Starts the server and loads all API routers
│   │
│   │   ├── api/
│   │   │   ├── api_router.py
│   │   │   │   # Central router that registers all API modules
│   │   │
│   │   │   └── routes/
│   │   │       ├── session.py
│   │   │       │   # Core orchestration logic:
│   │   │       │   # session creation, next-question logic,
│   │   │       │   # video submission, MCQ submission, finalize
│   │   │       │
│   │   │       ├── media.py
│   │   │       │   # API routes for uploading and managing video/audio files
│   │   │       │
│   │   │       ├── transcript.py
│   │   │       │   # API for generating text transcripts from audio
│   │   │       │
│   │   │       ├── audio_features.py
│   │   │       │   # API endpoint wrapper for audio feature extraction
│   │   │       │
│   │   │       ├── text_features.py
│   │   │       │   # API endpoint wrapper for text feature extraction
│   │   │       │
│   │   │       ├── mcq.py
│   │   │       │   # API routes for fetching and submitting MCQs
│   │   │       │
│   │   │       └── full_assessment.py
│   │   │           # Optional demo route that runs full pipeline in one call
│   │   │
│   │   ├── services/
│   │   │   ├── media/
│   │   │   │   ├── video_service.py
│   │   │   │   │   # Saves video files, extracts audio track for inference
│   │   │   │
│   │   │   │   └── audio_service.py
│   │   │   │       # Audio loading, resampling, preprocessing utilities
│   │   │
│   │   │   ├── transcript/
│   │   │   │   └── transcript_service.py
│   │   │   │       # Converts audio to text (ASR pipeline)
│   │   │
│   │   │   ├── features/
│   │   │   │   ├── audio_feature_service.py
│   │   │   │   │   # Extracts low-level & statistical audio features
│   │   │   │
│   │   │   │   ├── video_features.py
│   │   │   │   │   # Extracts facial keypoints, gaze & pose (MediaPipe)
│   │   │   │
│   │   │   │   ├── text_embedding_service.py
│   │   │   │   │   # Generates sentence-level embeddings from transcript
│   │   │   │
│   │   │   │   └── text_feature_service.py
│   │   │   │       # Optional wrapper around text embeddings
│   │   │
│   │   │   ├── scoring/
│   │   │   │   ├── fusion_inference_service.py
│   │   │   │   │   # Loads fusion_model.pkl and performs prediction
│   │   │   │   │   # Produces class probabilities + behavioral confidence
│   │   │   │
│   │   │   │   ├── runtime_feature_builder.py
│   │   │   │   │   # Converts runtime-extracted features into 2288-D vector
│   │   │   │
│   │   │   │   ├── final_decision_service.py
│   │   │   │   │   # Combines fusion confidence + MCQ score
│   │   │   │   │   # Produces final class decision
│   │   │   │
│   │   │   │   └── confidence_service.py
│   │   │   │       # Helper utilities for confidence aggregation
│   │   │
│   │   │   ├── mcq/
│   │   │   │   ├── question_bank.py
│   │   │   │   │   # Static PHQ-style MCQ questions & options
│   │   │   │
│   │   │   │   ├── mcq_selector.py
│   │   │   │   │   # Selects MCQs (baseline or RL-based, avoids repetition)
│   │   │   │
│   │   │   │   ├── mcq_scoring_service.py
│   │   │   │   │   # Computes MCQ scores and severity mapping
│   │   │   │
│   │   │   │   └── mcq_evaluator.py
│   │   │   │       # Evaluation logic for MCQ correctness & scoring
│   │   │
│   │   │   ├── rl/
│   │   │   │   ├── rl_env.py
│   │   │   │   │   # Custom Gymnasium environment for adaptive interviews
│   │   │   │
│   │   │   │   ├── rl_agent.py
│   │   │   │   │   # RL agent definition (policy usage & training hook)
│   │   │   │
│   │   │   │   ├── rl_reward.py
│   │   │   │   │   # Reward function based on confidence improvement
│   │   │   │
│   │   │   │   ├── rl_state_builder.py
│   │   │   │   │   # Converts session state into RL observation vector
│   │   │   │
│   │   │   │   ├── rl_action_mapper.py
│   │   │   │   │   # Maps RL actions → {video/mcq, difficulty}
│   │   │   │
│   │   │   │   └── rl_policy_loader.py
│   │   │   │       # Loads trained RL policy (if available)
│   │   │
│   │   │   └── session/
│   │   │       ├── session_store.py
│   │   │       │   # MongoDB access layer for session persistence
│   │   │       │
│   │   │       └── session_service.py
│   │   │           # Session-level helper utilities
│   │   │
│   ├── ml_training/
│   │   ├── preprocess.py
│   │   │   # Preprocesses offline dataset into fused features
│   │   │
│   │   ├── train_fusion_model.py
│   │   │   # Trains the multimodal fusion classifier
│   │   │
│   │   ├── artifacts/
│   │   │   ├── feature_order.json
│   │   │   │   # Defines exact feature concatenation order (LOCKED)
│   │   │   │
│   │   │   └── scaler.joblib
│   │   │       # Feature scaler used during training & inference
│   │   │
│   │   └── models/
│   │       └── fusion_model.pkl
│   │           # Trained multimodal fusion classifier
│   │
│   └── storage/
│       # Saved videos, audio files, intermediate artifacts
│
├── requirements.txt
└── README.md

```

---

## 4. How to Start the Backend

### 4.1 Create Environment

```bash
conda create -n v_gpu python=3.10
conda activate v_gpu (conda virtual environment)
pip install -r requirements.txt

---

### 4.2 Start Server

From **project root**:

```bash
cd backend
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## 5. Core APIs (IN ORDER OF USAGE)

---

## 5.1 Create Session

**POST** `/session/create`

### Purpose

* Initializes a new interview session
* Allocates DB storage
* Tracks video, MCQ, RL state

### Request

```
Form Data:
username: string
```

### Response

```json
{
  "session_id": "uuid",
  "username": "user"
}
```

---

## 5.2 Get Next Question (MAIN ORCHESTRATOR)

**GET** `/session/{session_id}/next-question`

### Purpose

* Central decision engine
* Decides WHAT the user should answer next

### Possible Responses

#### Video Question

```json
{
  "type": "video",
  "question": {
    "id": 3,
    "question": "Describe a recent stressful situation..."
  }
}
```

#### MCQ (Baseline)

```json
{
  "type": "mcq",
  "mode": "baseline"
}
```

#### MCQ (RL)

```json
{
  "type": "mcq",
  "question": {
    "id": 6,
    "question": "Feeling bad about yourself?",
    "difficulty": "hard"
  }
}
```

#### Finalize

```json
{
  "type": "finalize"
}
```

---

## 5.3 Submit Video Answer

**POST**
`/session/{session_id}/question/{question_id}/submit`

### Purpose

* Upload video response
* Extract features
* Run fusion inference
* Store confidence

### Request

```
multipart/form-data
video: .mp4
```

### Processing Pipeline

1. Save video + extract audio
2. Generate transcript
3. Extract:

   * Audio features
   * Video features (MediaPipe)
   * Text embeddings
4. Build fusion vector (2288-D)
5. Run fusion model
6. Store behavioral confidence

---

## 5.4 Submit MCQ Answers (Baseline – ALL AT ONCE)

**POST** `/session/{session_id}/mcq/submit`

### Request

```
Form Data:
mcq_answers: JSON string
```

Example:

```json
{
  "1": 2,
  "2": 1,
  "3": 3
}
```

### Purpose

* Scores PHQ-style MCQs
* Stores:

  * mcq_answers
  * mcq_score
  * mcq_result

---

## 5.5 Submit MCQ Answers (Baseline & RL – Unified)

**POST** `/session/{session_id}/mcq/submit`

### Request

Example:
```json
{
  "6": 2
}


### Purpose

* Prevents repetition
* Updates:

  * asked_mcqs
  * mcq_score
  * mcq_answers

---

## 5.6 Finalize Session

**POST** `/session/{session_id}/finalize`

### Purpose

* Computes final decision using:

  * Fusion confidence history
  * MCQ score
* Outputs final classification

### Response

```json
{
  "final_class": "Moderate",
  "confidence": 0.71,
  "explanation": "..."
}
```

---

## 6. ML & Feature Pipeline

### 6.1 Fusion Model

* Trained offline using AVEC-style features
* Input: **2288-dimensional vector**
* Output: probabilities for:

  * Low
  * Moderate
  * High

Loaded in:

```
services/scoring/fusion_inference_service.py
```

Uses:

* `fusion_model.pkl`
* `scaler.joblib`
* `feature_order.json`

---

### 6.2 Feature Types

| Modality | Source                 | File                      |
| -------- | ---------------------- | ------------------------- |
| Audio    | OpenSMILE-style        | audio_feature_service.py  |
| Video    | MediaPipe Face Mesh    | video_features.py         |
| Text     | Transformer embeddings | text_embedding_service.py |

---

## 7. MCQ System

### MCQ Bank

```
services/mcq/question_bank.py
```

* PHQ-style
* Difficulty-aware:

  * easy
  * medium
  * hard
* Used by:

  * baseline MCQs
  * RL MCQs

---

## 8. Reinforcement Learning (Adaptive Layer)

### Purpose

* Triggered ONLY if confidence < 0.65
* Chooses:

  * MCQ vs Video
  * Difficulty level

### RL State Includes:

* Average confidence
* MCQ score
* Confidence variance
* RL step count

### RL Policy

The system includes a fully integrated reinforcement learning (RL) decision layer
used at runtime to adaptively select follow-up questions.

- The RL **environment, state representation, reward function, and action mapping**
  are fully implemented and active.
- The current policy operates in **inference mode**, enabling deterministic
  adaptive behavior during evaluation and demo runs.
- The architecture supports future replacement with a fully trained or
  continuously updated policy without requiring backend changes.

This design ensures stable deployment while remaining extensible for future
learning-based optimization.


## 9. Session Storage (MongoDB)

Each session stores:

```json
{
  "session_id": "...",
  "username": "...",
  "questions": [...],
  "mcq_answers": {...},
  "asked_mcqs": [...],
  "mcq_score": 0.29,
  "confidence_history": [...],
  "rl_active": false,
  "rl_steps": 0,
  "session_result": null
}
```

---

## 10. Testing End-to-End (Quick Checklist)

1. Create session
2. Loop:

   * GET next-question
   * If video → submit video
   * If mcq → submit mcq
3. Stop when `type=finalize`
4. Call `/finalize`

---


## 11. Future Extensions

* **RL Policy Optimization**: Further tuning of the existing RL policy using larger interaction datasets and refined reward design.
* **Adaptive Difficulty Modeling**: Dynamic adjustment of question difficulty based on response uncertainty.
* **Explainability**: Addition of interpretable explanations for model predictions and RL-driven decisions.
* **Longitudinal Analysis**: Extension to multi-session behavioral tracking over time.
* **Clinical Validation**: Refinement of confidence thresholds through clinical evaluation.

---

## 12. Key Design Strengths

* True multimodal fusion
* Confidence-aware adaptivity
* RL-driven questioning
* Session-safe, non-repetitive
* Conference-ready architecture

---

