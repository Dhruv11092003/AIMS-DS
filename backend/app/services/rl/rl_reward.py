def compute_reward(prev_state, new_state, action, done):
    """
    Reward shaping for interview control.
    """

    reward = 0.0

    prev_conf = prev_state[0]
    new_conf = new_state[0]

    # Encourage confidence improvement
    reward += 0.1 * (new_conf - prev_conf)

    # Penalize long interviews
    if action in [0, 1, 2]:
        reward -= 0.05

    # Finalization decision
    if action == 4:
        if new_conf >= 0.65:
            reward += 0.6
        else:
            reward -= 0.2

    return reward
