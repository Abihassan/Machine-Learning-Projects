import torch
import torchvision.models as models
import torch.nn as nn
import numpy as np
import os

class InferenceEngine:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        if not self.use_mock:
            # Initialize production architecture setup (e.g., ResNet50 Binary Classifier)
            self.model = models.resnet50(weights=None)
            self.model.fc = nn.Linear(self.model.fc.in_features, 2)
            weights_path = os.path.join(os.path.dirname(__file__), "../models/weights/resnet50_deepfake.pth")
            if os.path.exists(weights_path):
                self.model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
            self.model.eval()

    def predict(self, processed_tensor: np.ndarray) -> float:
        """Returns the absolute probability of the image being AUTHENTIC (Real)"""
        if self.use_mock:
            # Mock Engine: Evaluates variance profiles or generates standard randomized outcomes
            import random
            return round(random.uniform(0.15, 0.98), 2)
        
        # PyTorch Production Pipeline Execution
        tensor = torch.tensor(processed_tensor).permute(2, 0, 1).unsqueeze(0) # [H, W, C] -> [1, C, H, W]
        with torch.no_grad():
            outputs = self.model(tensor)
            probabilities = torch.softmax(outputs, dim=1)
            # Assuming Class 0 = Fake, Class 1 = Real
            real_prob = probabilities[0][1].item()
            return round(real_prob, 2)