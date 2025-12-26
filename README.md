# AIMS-DS

## Adaptive Interview Monitoring System for Depression Screening

AIMS-DS is a multimodal intelligent screening framework developed as part of the SET Conference project. The system conducts an automated interview and assessment process to perform **depression screening** by analyzing behavioral, speech, and cognitive indicators using video responses and adaptive questionnaires.

The system is designed strictly for **screening and early risk indication**, and does not claim to perform medical diagnosis.

---

## Project Objectives

- To simulate an automated interview-based screening environment
- To analyze behavioral and speech patterns from video responses
- To assess cognitive indicators using adaptive MCQs
- To compute a structured confidence and depression risk score
- To adaptively control questioning strategy using reinforcement learning

---

## System Workflow

1. User answers predefined interview questions via recorded video
2. The system extracts multimodal features:
   - Video features (facial behavior, movement patterns)
   - Audio features (speech rate, pauses, energy)
   - Text features (linguistic hesitation and affect indicators)
3. An initial screening score is generated
4. Adaptive MCQs are presented to assess cognitive responses
5. Scores are fused to compute final depression screening confidence
6. A reinforcement learning agent determines the next action:
   - Additional MCQs
   - Follow-up interview questions
   - Termination of the screening session

---

## Technology Stack

### Backend
- Python
- FastAPI
- Pydantic
- NumPy
- Scikit-learn
- Reinforcement Learning modules

### Frontend
- React.js
- MediaRecorder API
- RESTful API integration

---

## Backend Architecture Overview

The backend follows a modular, service-oriented architecture with clear separation of concerns:

- Media handling (video/audio upload)
- Speech transcription
- Multimodal feature extraction
- MCQ selection and evaluation
- Confidence and screening score computation
- Reinforcement learning–based decision making

This structure ensures scalability, explainability, and ease of evaluation during academic review.

---

## Project Structure (High-Level)
backend/
app/
api/
services/
models/
schemas/
frontend/
src/
components/
pages/


---

## Ethical Considerations

- AIMS-DS is intended solely for **depression screening**
- It does not replace professional clinical assessment
- Outputs are presented as risk or confidence indicators, not diagnoses

---

## Current Status

- Project structure finalized
- Backend and frontend scaffolding completed
- Backend implementation in progress

---

## Future Scope

- Integration of advanced facial affect analysis
- Expansion of adaptive questioning strategies
- Validation using benchmark mental health datasets
- Deployment as a web-based screening platform

---

## Author

**Dhruv Kulshrestha**  
SET Conference Project  


