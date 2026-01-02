from stable_baselines3 import PPO
from pathlib import Path

MODEL_PATH = Path(r"D:/Repos/AIMS-DS/backend/ml_training/models/rl_policy")

_rl_model = None

def get_rl_policy():
    global _rl_model
    if _rl_model is None:
        _rl_model = PPO.load(MODEL_PATH)
    return _rl_model
