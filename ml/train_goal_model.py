# ml/train_goal_model.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Example schema: tdee, avg_net_7d, current_goal, target_goal
df = pd.read_csv("goal_training_data.csv")

X = df[["tdee", "avg_net_7d", "current_goal"]]
y = df["target_goal"]

model = LinearRegression()
model.fit(X, y)

with open("goal_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Saved goal_model.pkl")
