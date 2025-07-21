import numpy as np
from pytorch_tabnet.tab_model import TabNetClassifier

class TabNetModel:
    def __init__(self, model_path):
        self.model = TabNetClassifier()
        self.model.load_model(model_path)

    def run(self, x_input):
        preds = self.model.predict_proba(x_input)[0]
        prediction = int(preds[1] > 0.5)
        print(f"TabNet Model Prediction: {prediction}, Probabilities: {preds}")
        return {
            "verdict": "phishing" if prediction else "legit",
            "probabilities": {
                "phishing": float(preds[1]),
                "legit": float(preds[0])
            }
        }
