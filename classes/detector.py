import torch
from detoxify import Detoxify

class Detector(Detoxify):
    def __init__(self, model_type, device):
        super().__init__(model_type, device=device)
        self.counter = 0
    
    def __call__(self, text, return_all=False):
        if text is None or text=='':
            return None
        scores = self.predict(text)
        if not return_all:
            return scores['toxicity']
        else:
            return scores

device = 'cuda' if torch.cuda.is_available() else 'cpu'
detector = Detector('original', device=device)
        
    

                                         
        
