import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import re
import random
import numpy as np
import warnings

class Pipeline():
    
    def __init__(self, model_path, device, torch_dtype=torch.float16):
        self.model_path = model_path
        self.torch_dtype = torch_dtype
        self.device = device
        self._load_model()
    
    def _load_model(self):
        model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype=self.torch_dtype)
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id == tokenizer.eos_token_id
        self.pipeline = pipeline(model=model, task='text-generation', tokenizer=tokenizer, device=self.device)
    
    def _set_seed(self, seed):
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        transformers.set_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
            
    def inference(self, prompt, generation_config=None, seed=None):
        if isinstance(generation_config, dict):
            if 'max_new_tokens' not in generation_config:
                raise TypeError('generation_config misses a required argument: max_new_tokens')
        else:
            generation_config = {'do_sample':False, 
                                 'max_new_tokens':500}
        if seed is not None:
            self._set_seed(seed)
        try:
            output = self.pipeline(prompt, 
                                   truncation=False, # do not truncate!
                                   pad_token_id=2,
                                   return_full_text=False,
                                   **generation_config)[0]['generated_text']
        except:
            output = None
            correct_tags= False
            content = None
            return output, correct_tags, content
        if '<post>' and '</post>' in output:
            tags = ('<post>', '</post>')
        elif '<comment>' and '</comment>' in output:
            tags = ('<comment>', '</comment>')
        else:
            tags = ('<intervention>', '</intervention>')
        content = re.search(f"{tags[0]}(.*?){tags[1]}", output, re.DOTALL) # search for content inside the tags
        if content is not None:
            correct_tags = True#
            content = content.group(1)
            content = content.replace('\n', '')
        else:
            correct_tags = False
        return output, correct_tags, content
