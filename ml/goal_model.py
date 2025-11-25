# ml/goal_model.py
import os
import pickle

_model = None

def load_goal_model():
    global _model
    if _model is not None:
        return _model

    path = os.path.join(os.path.dirname(__file__), "goal_model.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            _model = pickle.load(f)
    else:
        _model = None
    return _model


def recommend_goal(tdee, avg_net_7d, current_goal=None):
    """
    tdee: maintenance calories
    avg_net_7d: average net calories over the last 7 days
    current_goal: previous daily goal (can be None)
    """
    model = load_goal_model()

    # If no ML model yet, use a simple rule-based fallback.
    if model is None:
        diff = avg_net_7d - tdee  # positive if overeating
        if diff > 300:
            return tdee - 400
        elif diff < -300:
            return tdee - 100
        else:
            return tdee - 250

    if current_goal is None:
        current_goal = tdee - 250

    import numpy as np
    X = np.array([[tdee, avg_net_7d, current_goal]])
    pred = model.predict(X)[0]
    return float(pred)
