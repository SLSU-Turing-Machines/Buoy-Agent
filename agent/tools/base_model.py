import dill
import numpy as np
import xgboost as xgb

class BaseModel:
    def __init__(self, model_path="./model/ttm_phishing_pipeline.pkl"):
        """
        Loads a serialized model pipeline from the given path.
        """
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        """
        Loads a model using dill.
        """
        try:
            with open(model_path, "rb") as f:
                model = dill.load(f)
            print("Model loaded successfully.")
            return model
        except FileNotFoundError:
            print(f"Error: Model file not found at {model_path}.")
            raise
        except dill.UnpicklingError:
            print("Error: Failed to load the model. The file may be corrupted or incompatible.")
            raise
        except Exception as e:
            print(f"Unexpected error while loading the model: {e}")
            raise

    def run(self, x_xgb_sample, x_html_sample):
        try:
            prediction, confidence = self.model.predict(x_xgb_sample, x_html_sample)
            result = {
                "verdict": "phishing" if prediction[0] == 1 else "legit",
                "probabilities": {
                    "phishing": float(confidence.get("phishing", 0.0)),
                    "legit": float(confidence.get("legit", 0.0)),
                }
            }
            print(f"Prediction: {result}")
            return result
        except Exception as e:
            print(f"Error occurred while running the model: {e}")
            raise

