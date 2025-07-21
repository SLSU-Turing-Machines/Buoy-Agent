import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

class GradientBoostingModel:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def run(self, x_input):
        # convert to numpy array if not already
        if not isinstance(x_input, np.ndarray):
            x_input = np.array(x_input)
        probs = self.model.predict_proba(x_input)[0]
        prediction = int(probs[1] > 0.5)
        print(f"Gradient Boosting Model Prediction: {prediction}, Probabilities: {probs}")
        return {
            "verdict": "phishing" if prediction else "legit",
            "probabilities": {
                "phishing": float(probs[1]),
                "legit": float(probs[0])
            }
        }

if __name__ == "__main__":
    model = GradientBoostingModel("model/gradientboosting_model.pkl")
    # Example input
    x_input = np.array([[0, 1, 0, 0, 1, 0, 1, 0, 1,0,1]])  # Replace with actual feature values
    result = model.run(x_input)
    print(result)