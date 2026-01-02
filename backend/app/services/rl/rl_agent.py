from stable_baselines3 import PPO
from rl_env import InterviewEnv

def train_rl_agent(total_steps: int = 50000):
    env = InterviewEnv()
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        batch_size=64,
        learning_rate=3e-4
    )

    model.learn(total_timesteps=total_steps)
    model.save("backend/ml_training/models/rl_policy")

    return model
