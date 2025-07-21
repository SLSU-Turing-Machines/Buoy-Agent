
import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler

class LoadScaler:
    def __init__(self, scaler_path):
        self.scaler = joblib.load(scaler_path)

    def run(self, x_input):
        if not isinstance(x_input, np.ndarray):
            raise ValueError("Input must be a numpy array")
        
        x_scaled = self.scaler.transform(x_input)
        return x_scaled
    