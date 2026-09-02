# What changed and what you need to do

## Round 1 - core RL/entropy bug + environment fixes

- `app/services/mcq/mcq_scoring_service.py` - damped the Bayesian update
  (`EVIDENCE_STRENGTH = 0.35`) so 8 PHQ-8 answers no longer collapse to
  false confidence. This is the fix for "never reaches RL."
- `app/services/rl/rl_policy_loader.py` - removed the hardcoded
  `D:/Repos/AIMS-DS/...` path, now resolves relative to the backend folder.
- `app/services/scoring/fusion_inference_service.py` - same kind of path
  fix, made more robust (was relying on the folder literally being named
  `backend`).
- `app/api/routes/session.py` - added the missing "RL picks another video
  question" branch (previously only "RL picks another MCQ" was handled,
  everything else silently finalized); removed a duplicate route
  decorator; wrapped the handshake in error handling so a broken RL model
  degrades to finalize instead of a 500.
- `app/services/session/question_selector.py` - added a working
  `select_rl_video_question` with cross-difficulty fallback.
- `app/services/mcq/mcq_selector.py` - added cross-difficulty fallback so
  the adaptive MCQ pool doesn't get exhausted mid-session.
- `app/services/mcq/adaptive_mcq_bank.py` - expanded from 3 to 6 questions
  per difficulty (easy/medium/hard).
- `app/services/media/audio_service.py` - updated to the moviepy 2.x API
  (`moviepy.editor` no longer exists in moviepy 2.x).
- `app/api/routes/full_assessment.py` - fixed calls to
  `run_fusion_inference()` / `compute_final_decision()` that used
  arguments that no longer match those functions.
- `app/api/routes/mcq.py` - MCQ submission now scores against the full
  accumulated answer set instead of just the latest submission.
- `app/services/scoring/confidence_service.py` - fixed a session lookup
  that used the wrong ID field (would 500 on every real session).
- `requirements.txt` - added missing packages, fixed `gym` -> `gymnasium`,
  pinned `moviepy>=2.0`, `numpy<2.0` (the NumPy 2.x ABI break with
  torch/whisper/mediapipe), and `mediapipe==0.10.21` (newer mediapipe
  removed the legacy `mp.solutions` face mesh API this project uses -
  confirmed by bisecting versions directly; 0.10.21 is the newest one
  that still works with this code).
- Deleted `app/services/questions/rl_video_selector.py` - unused duplicate
  of the video selector, dead code, not imported anywhere.

## Round 2 - made a silent RL failure visible + frontend bugs

The report screen you saw (high entropy, immediate finalize, no further
questions) is exactly what my Round 1 safety net produces if the RL model
fails to load or predict - it degrades to `finalize` instead of a 500 so
the session can still complete, but until now that reason only showed up
in the server log, not the response.

- `app/api/routes/session.py` - every "finalize early" path (RL failed,
  RL budget exhausted, RL had nothing left to ask, or a genuinely
  confident result) now returns a `debug: {"reason": ...}` field, and the
  reason is persisted on the session so `POST /finalize` echoes it back
  too. Reasons: `confident_no_rl_needed`, `rl_budget_exhausted`,
  `rl_step_failed` (includes the error message), `no_adaptive_video_available`,
  `no_adaptive_mcq_available`, `rl_chose_finalize`.
- Frontend (`frontend/src/api/sessionApi.js`) - `createSession` was
  posting to `/create` instead of `/session/create` (every other call in
  the file correctly used the `/session/...` prefix; this one didn't
  match the backend's actual route). `submitVideo` used a raw `fetch()`
  call that never checked the response status, so a failed video upload
  (e.g. a backend 500 from the mediapipe/whisper issues above) was
  silently treated as success and the frontend just moved on to the next
  question. Also, a recorded video Blob has no filename, which could
  reach the backend with no file extension - `submitVideo` now always
  attaches one.
- `frontend/src/App.jsx` - added a visible error screen with a Retry
  button for session creation / next-question failures, instead of an
  infinite silent loading spinner. Passes the `debug` reason through to
  the Finalize screen.
- `frontend/src/pages/VideoQuestion.jsx` / `MCQ.jsx` - failed submissions
  now show an inline error instead of hanging or silently advancing.
- `frontend/src/pages/Finalize.jsx` - shows the `debug` reason under the
  result (e.g. "The adaptive follow-up step failed to run, so the
  session ended on the baseline result alone") so it's visible on the
  report itself, not just in server logs or devtools.

## Round 3 - the actual RL failure, and its real cause

Your server log confirmed the Round 2 diagnosis exactly: `RL policy step
failed for session ...`, with the real error underneath:

```
ModuleNotFoundError: No module named 'numpy._core.numeric'
```

This is a genuine, if obscure, version conflict: `rl_policy.zip` was
trained and saved under NumPy 2.0.1 (visible in the model's own
`system_info.txt`), so its pickled data references `numpy._core.*`
module paths - a layout that only exists in NumPy 2.x (NumPy 2.0 renamed
its internal `numpy.core` package to `numpy._core`). But this project
needs NumPy `<2.0` for `mediapipe==0.10.21` (which hard-requires it) and
for the original torch/whisper crash from Round 1/2. So the RL policy
file and the rest of the stack were pulling in opposite directions on
NumPy's major version.

- `app/services/rl/rl_policy_loader.py` - added a small compatibility
  shim that aliases the already-imported `numpy.core.*` modules under
  their `numpy._core.*` names in `sys.modules` before loading the
  policy, so it unpickles correctly under NumPy `<2.0` without needing
  NumPy 2.x installed. Verified end-to-end: loaded the actual
  `rl_policy.zip`, ran `.predict()` on it, and ran a full simulated
  session where the *real* trained policy (not a mock) picked actions
  and the session correctly used up its RL budget and finalized.
- `requirements.txt` - pinned `librosa==0.10.2.post1`. While testing the
  above, `pip` flagged that the current `librosa` release (1.0.0)
  declares `numpy>=2.1.0`, one more thing pulling against the `numpy<2.0`
  pin. It happened to still run correctly under NumPy 1.26 in testing,
  but that's fragile to rely on, so it's pinned to the last release
  without that conflict.

No numpy/mediapipe/torch pins changed from Round 2 - those were already
correct, which is exactly what let whisper and mediapipe run cleanly in
your log with only benign warnings.

### About the `Gym has been unmaintained...` warning in your log

Harmless, but worth a cleanup: this means the old `gym` package is still
installed in your environment from before this project's `requirements.txt`
was fixed to use `gymnasium` instead (Round 1). `pip install -r
requirements.txt` only installs what's listed - it doesn't remove
packages that were dropped from the file. Run `pip uninstall gym -y` to
clear the warning; it wasn't causing any of the actual failures.

## What you need to do

1. In your existing `aims_ds_env` conda environment, run:
   `pip install "numpy<2.0" "mediapipe==0.10.21" "librosa==0.10.2.post1"`
   `pip uninstall gym -y`
   This fixes every crash you've hit so far: the NumPy 2.x ABI break
   with torch/whisper, mediapipe having dropped the legacy `mp.solutions`
   API, the RL policy's NumPy 2.x-only pickle data, a librosa/numpy
   version conflict, and clears the harmless `gym` deprecation warning.
2. `pip install -r requirements.txt` again as well - several other
   packages changed.
3. Make sure MongoDB is running locally before starting the API
   (`mongodb://localhost:27017`, see `app/core/config.py`).
4. Make sure `ffmpeg` is installed and on your PATH.
5. In the frontend, run `npm install` (unchanged deps, but if you're
   copying these files into your existing project rather than replacing
   the folder, nothing new needs installing) and restart your dev server.
6. Run through the flow again. If you land on the report page with a
   high-uncertainty note again, look at the small text under the
   "High Uncertainty" banner - it will now tell you directly whether it
   was a confident stop, a budget limit, or an actual RL failure (and if
   so, the error message), instead of you having to guess.

## What I deliberately left alone

- The 8-item PHQ-8 baseline questionnaire itself - it's a standard
  clinical instrument, so I expanded the *adaptive* (RL-only) question
  pools instead of altering the baseline.
- `mcq_evaluator.py` and the old `session_service.py` /
  `session_model.py` - these are unused, superseded by the current
  session flow, and nothing imports them. Left as historical dead code
  rather than deleting, in case you're mid-migration away from them.
- `ml_training/preprocess.py` / `train_fusion_model.py` - one-time
  offline scripts, not used by the running API, still reference the
  original dataset path on the original machine. Not something the API
  needs to run.

See `README.md` for the full explanation of how the scoring/entropy/RL
logic works, with a worked calculation example.
