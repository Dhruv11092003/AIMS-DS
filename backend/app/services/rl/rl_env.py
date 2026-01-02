import numpy as np
import gymnasium as gym
from gymnasium import spaces

from rl_reward import compute_reward

# ----------------------------------------
# CONSTANTS
# ----------------------------------------

MAX_QUESTIONS = 5

# ----------------------------------------
# ENVIRONMENT
# ----------------------------------------

class InterviewEnv(gym.Env):
    """
    Gymnasium-compatible environment for interview flow control.

    State vector (5,):
    [avg_confidence,
     last_confidence,
     mcq_score,
     num_questions_norm,
     confidence_delta]
    """

    metadata = {"render_modes": []}

    def __init__(self):
        super().__init__()

        # 5 discrete actions
        self.action_space = spaces.Discrete(5)

        # Continuous state
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(5,),
            dtype=np.float32
        )

        self.state = None
        self.prev_state = None
        self.num_questions = 0

    # ----------------------------------------
    # RESET
    # ----------------------------------------

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)

        self.num_questions = 0

        # Initial neutral state
        self.state = np.array([
            0.3,   # avg_confidence
            0.3,   # last_confidence
            0.0,   # mcq_score
            0.0,   # num_questions_norm
            0.0    # confidence_delta
        ], dtype=np.float32)

        self.prev_state = None

        return self.state, {}

    # ----------------------------------------
    # STEP
    # ----------------------------------------

    def step(self, action: int):
        """
        Simulate one interview decision step.
        """

        self.prev_state = self.state.copy()
        terminated = False
        truncated = False

        avg_conf, last_conf, mcq_score, _, _ = self.state

        # ----------------------------------------
        # ACTION EFFECTS
        # ----------------------------------------

        if action in [0, 1, 2]:  # video question
            self.num_questions += 1

            # Simulate confidence change
            difficulty_factor = {0: 0.03, 1: 0.05, 2: 0.07}[action]
            delta = np.random.uniform(-0.02, difficulty_factor)

            new_conf = np.clip(last_conf + delta, 0.0, 1.0)

            avg_conf = (avg_conf * (self.num_questions - 1) + new_conf) / self.num_questions
            last_conf = new_conf

        elif action == 3:  # MCQ
            mcq_score = np.clip(
                mcq_score + np.random.uniform(0.2, 0.4),
                0.0,
                1.0
            )

        elif action == 4:  # finalize
            terminated = True

        # ----------------------------------------
        # UPDATE STATE
        # ----------------------------------------

        confidence_delta = last_conf - self.prev_state[1]

        self.state = np.array([
            avg_conf,
            last_conf,
            mcq_score,
            min(self.num_questions / MAX_QUESTIONS, 1.0),
            confidence_delta
        ], dtype=np.float32)

        # ----------------------------------------
        # REWARD
        # ----------------------------------------

        reward = compute_reward(
            self.prev_state,
            self.state,
            action,
            terminated
        )

        return self.state, reward, terminated, truncated, {}
