import joblib
import numpy as np
from sklearn.svm import SVC

class SVMModel:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def run(self, x_input):
        probs = self.model.predict_proba(x_input)[0]
        prediction = int(probs[1] > 0.5)
        print(f"SVM Model Prediction: {prediction}, Probabilities: {probs}")
        return {
            "verdict": "phishing" if prediction else "legit",
            "probabilities": {
                "phishing": float(probs[1]),
                "legit": float(probs[0])
            }
        }
