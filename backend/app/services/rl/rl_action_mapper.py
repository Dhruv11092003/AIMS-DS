def map_action(action: int) -> dict:
    if action == 0:
        return {"type": "video", "difficulty": "easy"}
    if action == 1:
        return {"type": "video", "difficulty": "medium"}
    if action == 2:
        return {"type": "video", "difficulty": "hard"}
    if action == 3:
        return {"type": "mcq"}
    if action == 4:
        return {"type": "finalize"}

    raise ValueError("Invalid RL action")
