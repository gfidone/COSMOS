from .prompt import Prompt
import random
import warnings

class User():
    
    def __init__(self, 
                 pipeline, 
                 id, 
                 profile, 
                 post_no_memory, 
                 post_memory, 
                 comment_no_memory, 
                 comment_memory, 
                 memory_size=None):
        
        self.id = id
        self.profile = profile
        self.pipeline = pipeline
        self.interventions = list()
        self.banned = False
        self.n_toxic_actions = 0
        self.memory_size = memory_size
        
        attributes = list(profile.keys())
        self.post_no_memory = Prompt(post_no_memory, attributes)
        self.post_memory = Prompt(post_memory, attributes)
        self.comment_no_memory = Prompt(comment_no_memory, attributes)
        self.comment_memory = Prompt(comment_memory, attributes)

    def generate(self, 
                 topic=None, 
                 parent=None, 
                 root=None, 
                 censored=False, 
                 generation_config=None, 
                 seed=None):
        if topic:
            result = {'b_prompt': self.post_no_memory(**self.profile, 
                                                      topic=topic)
                     }
            result['a_prompt'] = self.post_memory(**self.profile, 
                                                  topic=topic, 
                                                  intervention=self._format_interventions()) if self.interventions else result['b_prompt']
        else:
            a_root_content = root['a_content'] if root['a_content'] is not None else root['b_content']
            a_parent_content = parent['a_content'] if parent['a_content'] is not None else parent['b_content']
            l_thread = f'Post by {root["username"]}: "{root["b_content"]}"\n' if parent == root else f'Post by {root["username"]}: "{root["b_content"]}"\nComment by {parent["username"]}: "{parent["b_content"]}"'
            a_thread = f'Post by {root["username"]}: {a_root_content}\n' if parent == root else f'Post by {root["username"]}: "{a_root_content}"\nComment by {parent["username"]}: "{a_parent_content}"'
            result = {'b_prompt': self.comment_no_memory(**self.profile, thread=l_thread)}

            sensory_changed = a_root_content != root['b_content'] or a_parent_content != parent['b_content']

            if len(self.interventions) > 0: 
                result['a_prompt'] = self.comment_memory(**self.profile, 
                                                         thread=a_thread, 
                                                         intervention=self._format_interventions())
            elif len(self.interventions) == 0:
                if sensory_changed: 
                    result['a_prompt'] = self.comment_no_memory(**self.profile, 
                                                                thread=a_thread)
                else:
                    result['a_prompt'] = result['b_prompt'] 

        result['b_output'], result['b_tags'], result['b_content'] = self.pipeline.inference(result['b_prompt'], 
                                                                                            generation_config, 
                                                                                            seed=seed)

        if not self.banned and not censored: 
            if result['b_prompt'] == result['a_prompt']: 
                result['a_output'], result['a_tags'], result['a_content'] = result['b_output'], result['b_tags'], result['b_content']
            else:
                result['a_output'], result['a_tags'], result['a_content'] = self.pipeline.inference(result['a_prompt'], 
                                                                                                    generation_config, 
                                                                                                    seed=seed)
       
        return result

    def _format_interventions(self):
        result_string = str()
        if self.memory_size is None:
            memory = self.interventions
        else:
            memory = self.interventions[-self.memory_size:]
        if self.memory_size == 1:
            result_string += f'{memory[0]}'
        else:
            for i, intervention in enumerate(memory):
                intervention = intervention.replace('\n', '') 
                result_string += f'Intervention {i}: {intervention}\n'
        return result_string