import requests
from tqdm import tqdm
import time

class PerspectiveAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = f'https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={self.api_key}'
        self.counter = 0
    
    def analyze(self, text, languages=["en"], attributes=None):
        if attributes is None:
            attributes = ["TOXICITY", "SEVERE_TOXICITY", "IDENTITY_ATTACK", 
                          "INSULT", "PROFANITY", "THREAT", "SEXUALLY_EXPLICIT", "FLIRTATION", "OBSCENE"]

        data = {
            "comment": {
                "text": text
            },
            "requestedAttributes": {attribute: {} for attribute in attributes},
            "languages": languages
        }

        response = requests.post(self.url, json=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    def extract_scores(self, result):
        scores = {}
        for attribute, score_data in result["attributeScores"].items():
            scores[attribute] = score_data["summaryScore"]["value"]
        return scores
    
    def __call__(self, text, delay=False, return_all=False):
        if delay:
            start_time = time.time()
        try:
            result = self.analyze(text)
        except:
            return None
        if delay:
            elapsed_time = time.time() - start_time
            if elapsed_time < 1:
                time.sleep(1 - elapsed_time)
        scores = self.extract_scores(result)
        if not return_all:
            return scores['TOXICITY']
        else:
            return scores
        
    def annotate(self, texts, return_all=False): 
        scores = list()
        for text in tqdm(texts):
            scores.append(self.__call__(text, return_all=return_all))
            self.counter += 1
            if self.counter == 160: # query limit /s
                time.sleep(1)
                self.counter = 0
        return scores
            
        
API_KEY = None # your API key
detector = PerspectiveAPI(API_KEY)
        
    

                                         
        
