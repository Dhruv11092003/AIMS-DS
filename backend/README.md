# AIMS-DS — Adaptive Interview Monitoring System for Depression Screening

A FastAPI backend that runs a mixed video + PHQ-8 questionnaire interview,
fuses behavioral (audio/video/text) evidence with the questionnaire answers,
and uses a trained RL policy to decide whether to ask follow-up questions
before finalizing a Low / Moderate / High severity estimate.

## 1. High-level flow

```
1. POST /session/create                 -> creates a session
2. GET  /session/{id}/next-question      -> loop:
        a. 4 baseline video questions (always asked first)
        b. 8 baseline PHQ-8 questions (always asked next)
        c. Bayesian fusion of video + PHQ-8 evidence -> entropy check
        d. if uncertain and budget remains -> RL picks: another video
           question, another MCQ, or finalize
3. POST /session/{id}/question/{qid}/submit  -> upload video answer
4. POST /session/{id}/mcq/submit             -> submit MCQ answer(s)
5. POST /session/{id}/finalize               -> persist + return final result
```

The frontend just keeps calling `next-question` and submitting whatever it
returns (`type: "video"` or `type: "mcq"`) until it gets `type: "finalize"`.

## 2. Why the RL step wasn't triggering (the main bug)

`compute_mcq_score()` combined every PHQ-8 answer into a running probability
distribution over `{Low, Moderate, High}` using a standard Bayesian update:
multiply the running distribution by each answer's likelihood, renormalize.

That's mathematically correct, but the per-answer likelihood table is quite
informative on its own (e.g. answering "Not at all" already favors Low
7:1 over High). Multiplying 8 of those together in full compounds fast —
in testing, even a genuinely mixed/contradictory set of 8 answers collapsed
to normalized entropy ~0.3, which was already under the 0.45 threshold used
to decide `needs_rl_refinement`. In practice this meant the system reached
false confidence almost every time, regardless of how uncertain the case
actually was, so RL essentially never fired.

**Fix**: each answer's likelihood is now raised to a fractional exponent
(`EVIDENCE_STRENGTH = 0.35`) before being multiplied in — a damped/partial
Bayesian update. Consistent, unambiguous answers (e.g. all "Not at all")
still converge to high confidence; genuinely mixed, contradictory, or
worsening answer patterns now correctly stay above the entropy threshold
and route to RL. This one change is what fixes "shows 8 questions, never
moves to RL."

## 3. Worked calculation example

Assume behavioral confidence and psychometric (MCQ) evidence disagree —
this is the case that should trigger RL.

**Step 1 — MCQ (psychometric) evidence.**
Each of the 8 PHQ-8 answers votes softly for a severity class:

| Answer | Low | Moderate | High |
|---|---|---|---|
| 0 - Not at all | 0.70 | 0.20 | 0.10 |
| 1 - Several days | 0.45 | 0.40 | 0.15 |
| 2 - More than half the days | 0.20 | 0.50 | 0.30 |
| 3 - Nearly every day | 0.10 | 0.30 | 0.60 |

Starting from a uniform prior `{Low: 1/3, Moderate: 1/3, High: 1/3}`, each
answer updates the running distribution as:

```
probs[class] = probs[class] * (likelihood[class] ** 0.35)
probs = normalize(probs)
```

For example, one "2" (More than half the days) answer:

```
Low:      0.333 * (0.20 ** 0.35) = 0.333 * 0.569 = 0.190
Moderate: 0.333 * (0.50 ** 0.35) = 0.333 * 0.785 = 0.261
High:     0.333 * (0.30 ** 0.35) = 0.333 * 0.656 = 0.219
normalize -> Low: 0.28, Moderate: 0.39, High: 0.33
```

Repeat for all 8 answers, renormalizing each time. For a mixed pattern
like `[1, 2, 1, 2, 0, 2, 1, 1]`, this converges to
`Low: 0.38, Moderate: 0.55, High: 0.06` on the MCQ evidence alone -
clearly leaning Moderate, but with real residual uncertainty (its own
normalized entropy is about 0.79, well above where a confident answer
pattern like all-zeros would land, around 0.15).

**Step 2 - Behavioral (video/audio/text) evidence.**
Each answered video question runs through the fusion model
(`fusion_model.pkl`, an XGBoost classifier trained on pooled audio + facial
keypoint + gaze + pose + text-embedding features) which outputs a
temperature-scaled softmax over the same 3 classes. These are averaged
across all answered video questions to get `behavioral_probabilities`, e.g.
`Low: 0.45, Moderate: 0.35, High: 0.20`.

**Step 3 - Bayesian fusion of the two evidence sources.**

```
alpha (behavioral weight) = clip(0.4 + 0.2 * behavioral_confidence, 0.3, 0.6)
beta  (psychometric weight) = 1 - alpha

final[class] = normalize(alpha * behavioral[class] + beta * mcq[class])
```

**Step 4 - Uncertainty (normalized Shannon entropy).**

```
H = -sum(p * ln(p) for p in final.values()) / ln(3)
```

`H` ranges 0 (fully confident) to 1 (uniform / maximally uncertain).

**Step 5 - Decide.**

```
needs_rl_refinement = H >= 0.45
```

For the mixed example above, combined with the sample behavioral evidence
from Step 2, `H` comes out to about 0.92 - well above 0.45, so RL is
triggered and the trained policy (`rl_policy.zip`, a Stable-Baselines3 PPO
agent) picks one of: another easy/medium/hard video question, another
adaptive MCQ, or finalize - based on a 5-value state vector
`[entropy, entropy_delta, disagreement_kl, progress_ratio, p_high]`.

By contrast, if both evidence sources strongly agree (e.g. both clearly
indicate Low), `H` typically lands around 0.35-0.45 and the session
finalizes immediately without spending any RL budget.

## 4. RL details

- **Action space** (`Discrete(5)`): 0/1/2 = ask another video question at
  easy/medium/hard difficulty, 3 = ask another adaptive MCQ, 4 = finalize.
- **State space** (`Box(5,)`, values in [0,1]): current entropy, entropy
  delta since the previous step, normalized KL disagreement between the two
  evidence sources, progress ratio (`rl_steps / MAX_RL_STEPS`), and `p_high`.
- **Budget**: at most `MAX_RL_STEPS = 5` additional questions per session.
- Previously, `map_action()` correctly produced `{"type": "video", ...}`,
  but `session.py`'s handshake only had a branch for `{"type": "mcq"}` -
  any video action silently fell through to `finalize`. This is now
  handled (`select_rl_video_question`), with a fallback across difficulty
  pools if the requested one is exhausted.
- The RL policy path was hardcoded to a Windows path
  (`D:/Repos/AIMS-DS/...`) that only existed on the original developer's
  machine. It now resolves relative to the backend folder, so it works on
  any machine/OS. The same fix was applied to the fusion model path.
- The RL policy file itself was trained and saved under NumPy 2.x, so its
  pickled data references `numpy._core.*` module paths that only exist in
  NumPy 2.x. This project pins NumPy `<2.0` (required by
  torch/whisper/mediapipe compatibility - see section 5), so loading it
  used to fail with `ModuleNotFoundError: No module named
  'numpy._core.numeric'`. `rl_policy_loader.py` now registers a small
  compatibility shim (aliasing the already-imported `numpy.core.*`
  modules under their `numpy._core.*` names) before loading the policy,
  which resolves this without needing NumPy 2.x installed. Verified
  end-to-end against the actual `rl_policy.zip` file, including a full
  RL loop using the real trained policy's predictions (not mocked).
- If the RL policy fails to load or predict for any reason, the session
  now degrades to `finalize` instead of returning a 500 error. This is
  now surfaced in the response itself (`debug.reason`), not just the
  server log - see section 4a.

## 4a. Diagnosing an early/unexpected finalize

Every time `next-question` (or `finalize`) ends a session, the response
includes a `debug` field explaining why:

| `debug.reason` | Meaning |
|---|---|
| `confident_no_rl_needed` | Both evidence sources agreed - genuinely confident, no RL needed. |
| `rl_budget_exhausted` | `MAX_RL_STEPS` follow-up questions were used without dropping below the entropy threshold. |
| `rl_step_failed` | The RL policy itself errored (load or predict) - `debug.error` has the exception message. This is the one to look for if you see high uncertainty but no follow-up questions were asked. |
| `no_adaptive_video_available` / `no_adaptive_mcq_available` | The RL policy picked an action but the corresponding question pool was exhausted. |
| `rl_chose_finalize` | The RL policy explicitly chose the finalize action. |

The frontend's report screen displays this under the uncertainty banner.

## 5. What else was fixed

- `requirements.txt` was missing several packages that are actually
  imported (`mediapipe`, `opencv-python`, `sentence-transformers`,
  `joblib`, `pandas`, `xgboost`, `tqdm`), and listed `gym` instead of the
  `gymnasium` package the code actually uses. It also left `numpy`
  unpinned, which let pip install NumPy 2.x - but the installed builds of
  `torch`/`whisper`/`mediapipe` in this project were built against NumPy
  1.x's ABI, which crashes at import time under NumPy 2.x
  (`RuntimeError: Numpy is not available` from inside whisper's model
  loading). Pinned `numpy<2.0` to fix this.
- `mediapipe` was also unpinned. Google quietly dropped the legacy
  `mp.solutions` API (used by `video_features.py` for face mesh
  extraction) starting somewhere around mediapipe 0.10.30 - installing an
  unpinned `mediapipe` today pulls a version where
  `mp.solutions.face_mesh` no longer exists at all
  (`AttributeError: module 'mediapipe' has no attribute 'solutions'`).
  I bisected this directly: 0.10.13 through 0.10.21 still have
  `solutions` and work correctly (verified against one of the bundled
  sample videos, extracting real facial-keypoint/gaze/pose data);
  0.10.30 and newer don't. Pinned `mediapipe==0.10.21`, the newest
  version confirmed to still work with this code as written.
- `audio_service.py` used the moviepy 1.x `moviepy.editor` import path and
  a `verbose=` argument that no longer exists in moviepy 2.x. Updated to
  the moviepy 2.x API and pinned `moviepy>=2.0` in requirements.
- The adaptive MCQ bank only had 3 questions per difficulty (easy/medium/
  hard) with no fallback, so a few repeated RL picks could exhaust a
  bucket and prematurely end the session. Expanded to 6 per difficulty
  and added cross-difficulty fallback (same fix applied to RL video
  question selection).
- `full_assessment.py` (the one-shot `/assessment/full-assessment` test
  endpoint) called `run_fusion_inference()` and `compute_final_decision()`
  with keyword arguments that no longer match their actual signatures -
  it would have thrown on every call. Rewired to build the feature vector
  correctly and construct the small session-shaped dict
  `compute_final_decision` expects.
- `/confidence/compute` (`confidence_service.py`) looked sessions up by
  Mongo `ObjectId`, but sessions are created with a UUID string in a
  `session_id` field - this endpoint would 500 on every real session.
  Fixed the lookup. Note: this endpoint reads from `audio_features` /
  `text_features` / `mcq_responses` fields that the current session flow
  doesn't populate (it's a separate, older scoring path from before the
  Bayesian fusion approach) - it's left as-is since fixing that fully is
  a separate feature, not a bug in the reported flow.
- `mcq.py`'s submit endpoint was scoring only the just-submitted answer(s)
  instead of the full accumulated set, so the `mcq_score`/probabilities
  returned to the frontend after each submission didn't match what
  `final_decision_service` would compute. Fixed to score against the full
  accumulated answer set.
- Removed a duplicate `@router.get` decorator on `next-question` and
  wrapped the whole handshake in error handling (previously the only
  endpoint without it).
- Removed a dead, unused duplicate of the RL video question selector.

## 6. Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

You'll also need:
- **MongoDB** running locally (`mongodb://localhost:27017` by default -
  see `app/core/config.py`).
- **ffmpeg** available on PATH (used by moviepy/whisper for audio
  extraction and transcription).

Run the API:

```bash
uvicorn app.main:app --reload
```

## 7. Known non-blocking items

- Loading `fusion_model.pkl` prints an XGBoost `UserWarning` about the
  pickle format predating the installed XGBoost version. It still loads
  and predicts correctly - this is just XGBoost recommending the model be
  re-exported with `Booster.save_model()` at some point; not urgent.
- The RL policy's observation space was trained with bounds `[-1, 1]`,
  but the runtime state vector only ever produces values in `[0, 1]`. This
  doesn't break anything (values are still valid, in-range inputs), it
  just means half the trained input range is never exercised at runtime.
  Worth knowing about if the policy is ever retrained.
- `ml_training/preprocess.py` and `train_fusion_model.py` are one-time
  offline scripts (not used by the running API) and still reference the
  original developer's local dataset path - they're just historical
  records of how `fusion_model.pkl` was produced, not something you need
  to run.
- `mediapipe` is pinned to `0.10.21` because the legacy `mp.solutions`
  API this project uses was removed from later releases (see section 5).
  Google's officially supported path going forward is the newer
  `mediapipe.tasks.python.vision.FaceLandmarker` API, which needs a
  separately downloaded `.task` model file. Migrating `video_features.py`
  to that API would remove this pin, but is a separate piece of work
  (not something needed to fix the reported bugs) since it changes how
  the video feature extraction is called, not just which package version
  is installed.
- `mediapipe==0.10.21` itself declares a hard `numpy<2` requirement (pip
  will refuse/warn on `numpy>=2` alongside it), which is part of why this
  project pins `numpy<2.0` rather than upgrading to NumPy 2.x - the other
  option (upgrading everything to NumPy 2.x-compatible versions) would
  require dropping the legacy mediapipe API entirely per the point above.
- `librosa` is pinned to `0.10.2.post1` rather than left open, because
  the current latest release (`librosa 1.0.0`) declares a `numpy>=2.1.0`
  requirement - directly conflicting with the `numpy<2.0` pin above. In
  practice `librosa 1.0.0`'s audio-feature functions this project
  actually calls still ran fine under NumPy 1.26 in testing, but relying
  on that would be fragile (pip's resolver already flags it as
  incompatible, and a future librosa patch could start enforcing it).
  `0.10.2.post1` is the last pre-1.0 release and has no such conflict.
