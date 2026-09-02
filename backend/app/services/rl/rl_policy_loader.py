import sys
from pathlib import Path

import numpy

from app.core.config import BACKEND_DIR

MODEL_PATH = Path(BACKEND_DIR) / "ml_training" / "models" / "rl_policy"

_rl_model = None


def _register_numpy_core_compat_shim():
    """
    The RL policy was trained and saved under NumPy 2.x, so its pickled
    data references "numpy._core.*" module paths (NumPy 2.0 renamed the
    internal "numpy.core" package to "numpy._core"). This project pins
    NumPy <2.0 for compatibility with mediapipe/torch, so those module
    paths don't exist here and PPO.load() fails with
    ModuleNotFoundError: No module named 'numpy._core.numeric'.

    This aliases the already-imported numpy.core.* modules under their
    numpy._core.* names in sys.modules, so unpickling resolves them
    without needing NumPy 2.x installed. No-op if already NumPy 2.x.
    """
    if numpy.__version__.startswith("2."):
        return

    import numpy.core as _np_core
    import numpy.core.numeric as _np_core_numeric

    sys.modules.setdefault("numpy._core", _np_core)
    sys.modules.setdefault("numpy._core.numeric", _np_core_numeric)
    for name, mod in list(sys.modules.items()):
        if name.startswith("numpy.core."):
            alias = "numpy._core." + name[len("numpy.core."):]
            sys.modules.setdefault(alias, mod)


def get_rl_policy():
    global _rl_model
    if _rl_model is None:
        if not Path(str(MODEL_PATH) + ".zip").exists():
            raise FileNotFoundError(
                f"RL policy not found at: {MODEL_PATH}.zip"
            )
        _register_numpy_core_compat_shim()
        from stable_baselines3 import PPO
        _rl_model = PPO.load(MODEL_PATH)
    return _rl_model
