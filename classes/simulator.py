import torch
import numpy as np
import pandas as pd
import networkx as nx
import warnings
import random
import time
import re
from tqdm import tqdm

from .detector import detector 
from .pipeline import Pipeline
from .prompt import Prompt
from .user import User


class Simulator():

    def __init__(self, 
                 model_path, 
                 profiles, 
                 moderate_template, 
                 topics, 
                 thr, 
                 thread_prob=0.5, 
                 comment_prob=0.5, 
                 tau=3): 
        
        self.pipeline = Pipeline(model_path, device='cuda')
        self.topics = topics
        self.attributes = list(profiles[0].keys()) 
        self.moderate_prompt = Prompt(moderate_template, self.attributes)
        self.thread_prob = thread_prob 
        self.comment_prob = comment_prob
        self.tau = tau
        self.thr=thr
        self.n_users = len(profiles)
        self.profiles = profiles
    
    def _interact(self):
        '''Make users undertake actions.'''
        
        random.seed(self.seeds.pop())
        random.shuffle(self.users)
        for user in tqdm(self.users, 
                         desc=f'Time {self.current_iter}: user interactions'):
            data = {'user_id':user.id,
                    'memory':user.interventions[-self.memory_size:],
                    'time':self.current_iter,
                    'seed':self.seeds.pop()
                   }
            action_data = self._action(user=user, seed=data['seed'])
            data.update(action_data)
            self._add_to_feed(thread_id = data['thread_id'],
                              parent_id = data['parent_id'],
                              **{'username':user.profile['username'],
                              'b_content':data['b_content'],
                              'a_content':data['a_content']}) 
            self.history[self.current_iter].append(data)
    
    def _add_to_feed(self, thread_id=None, parent_id=None, **attributes):
        '''Add a new node in the news feed.'''
        
        if parent_id == None: 
            thread = nx.DiGraph() 
            thread.add_node(self.n_nodes, **attributes) 
            self.feed.append(thread) 
        else:
            self.feed[thread_id].add_node(self.n_nodes, **attributes) 
            self.feed[thread_id].add_edge(parent_id, self.n_nodes) 
        self.n_nodes +=1
        
    def _action(self, user, seed): 
        '''Executes action.'''
        
        data = {k: None for k in ['topic', 'root_id', 'thread_id', 'parent_id', 'node_id', 'b_prompt', 'a_prompt', 
                                 'b_output', 'a_output', 'b_tags', 'a_tags', 'b_content', 'a_content', 
                                 'b_toxicity', 'a_toxicity']} 
        data.update({'banned': user.banned, 'censored': user.banned}) 
        if self.current_iter == 0 and user == self.users[0]: # first user at first timestep is forced to post
            action = 'post'
        else:
            weights = [self.thread_prob, self.comment_prob, (1 - self.thread_prob - self.comment_prob)]
            random.seed(self.seeds.pop())
            action = random.choices(['post', 'comment', None], weights=weights, k=1)[0]
        if action == 'post':
            random.seed(self.seeds.pop()) 
            data['topic'] = random.choice(self.topics) # select topic 
            seed = self.seeds.pop() 
            data.update(user.generate(topic=data['topic'], 
                                      generation_config=self.generation_config, 
                                      #active_stream=active_stream, censored always false
                                      seed=seed))
            data['b_toxicity'], data['a_toxicity'] = self._get_toxic_rates(data)
            data['thread_id'] = len(self.feed)
            data['node_id'] = self.n_nodes
            data['root_id'] = data['node_id']
        elif action == 'comment':
            if len(self.feed) > 0:
                data['thread_id'], data['parent_id'], censored = self._sample_content(user)
                if censored: 
                    data['censored'] = True 
                    censored = True
                parent = self.feed[data['thread_id']].nodes[data['parent_id']] 
                data['root_id'], root = self._get_root(data['thread_id'])
                seed = self.seeds.pop()
                data.update(user.generate(parent=parent, 
                                          root=root, 
                                          generation_config=self.generation_config, 
                                          censored = censored,
                                          seed=seed))
                data['b_toxicity'], data['a_toxicity'] = self._get_toxic_rates(data)
                data['node_id'] = self.n_nodes
        return data
    
    def _get_toxic_rates(self, data):
        '''Returns toxic rates for a node.'''
        
        l_t = detector(data['b_content'])
        a_t = l_t if data['b_content'] == data['a_content'] else detector(data['a_content'])
        return l_t, a_t
    
    def _sample_content(self, user):
        '''Gets a node from a time-adaptive probability distribution.'''
        
        time_distribution = {(node['thread_id'], node['node_id'], node['user_id'], node['b_content'], node['a_content'], node['censored']): self.history.index(timestep)
        for timestep in self.history for node in timestep if node['node_id'] is not None}
        for info in time_distribution:
            is_author_of_child = self._is_author_of_child(info[0], info[1], user)
            if info[2] == user.id or is_author_of_child: 
                time_distribution[info] = np.NINF
            if info[3] is None:
                time_distribution[info] = np.NINF
        probs = self._softmax(list(time_distribution.values()))
        prob_distribution = {info:prob for info, prob in zip(time_distribution, probs)}
        random.seed(self.seeds.pop())
        selected_info = random.choices(list(prob_distribution.keys()), 
                                       weights=list(prob_distribution.values()), 
                                       k=1)[0]
        return selected_info[0], selected_info[1], selected_info[5] # thread_id, node_id, censored

    def _softmax(self, logits):
        '''Softmax function.'''
        
        logits = np.array(logits)
        max_logits = np.max(logits, axis=-1, keepdims=True)
        logits = (logits - max_logits) / self.tau
        exp_logits = np.exp(logits)
        probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
        return probs
        
    def _is_author_of_child(self, thread_id, node_id, user):
        '''Checks if user is the author of a node.'''
        thread = self.feed[thread_id]
        children = list(thread.successors(node_id))
        for child in children:
            if thread.nodes[child].get('user_id') == user.id: 
                return True
        return False
    
    def _moderate(self):
        '''Executes moderation (interventions and/or bans).'''      
        for i, node in enumerate(tqdm(self.history[self.current_iter], desc=f'Time {self.current_iter}: moderation')):
            if node['a_content'] is not None:
                user = self.get_user_by_id(node['user_id'])
                if node['a_toxicity'] is not None and node['a_toxicity'] > self.thr:
                    user.n_toxic_actions +=1
                    if self.exante:
                        self._exante(user, i, node)
                    if self.ban: 
                        self._ban(user)
    
    def _exante(self, user, i, node):
        '''Implements ex ante moderation.'''
        
        if self.osfa:
            message = self.default
            moderate_prompt = None
        else:
            node = self.feed[node['thread_id']].nodes[node['node_id']]
            if self.func == None:
                moderate_prompt = self.moderate_prompt(content=node['a_content'], 
                                                       **user.profile)
                output, correct_tags, message = self.pipeline.inference(moderate_prompt, 
                                                                             seed=self.moderate_seeds.pop(0))
            else:
                message = self.func(node['a_content']) # wrapper
        user.interventions.append(message)
        self.history[self.current_iter][i]['intervention'] = message
        self.history[self.current_iter][i]['moderate_prompt'] = moderate_prompt
    
    def _ban(self, user):   
        '''Executes ban.'''
        
        if not user.banned:
            if user.n_toxic_actions >= self.tolerance:
                user.banned = True
                self.active_users.remove(user)
                
    def _get_root(self, thread_id):
        'Returns the root of a tree.'
        
        roots_ids = [node_id for node_id, degree in self.feed[thread_id].in_degree() if degree==0] 
        if len(roots_ids) > 1:
            raise IndexError('Found more than one root')
        return roots_ids[0], self.feed[thread_id].nodes[roots_ids[0]]

    def get_user_by_id(self, id):
        '''Returns the user with id.'''
        
        for user in self.users:
            if user.id == id:
                return user    
    
    def _step(self):
        '''Executes timestep'''
        
        self.history.append(list())
        self._interact() 
        if self.current_iter < self.n_iter - 1:
            self._moderate()
                
    def run(self, 
            n_iter, 
            post_no_memory, 
            post_memory, 
            comment_no_memory, 
            comment_memory, 
            export_path, 
            exante=True, 
            func=None, 
            ban=False, 
            memory_size=1, 
            osfa=False, 
            default=None, 
            tolerance=None, 
            generation_config=None, 
            active_stream=None,
            seed=None
           ):
        '''Runs the simulation.'''
        
        self.n_iter = n_iter
        self.exante = exante
        self.func = func
        self.ban = ban
        self.memory_size = memory_size
        self.osfa = osfa
        self.default = default
        self.tolerance = tolerance
        self.generation_config = generation_config
        self.seed = random.randint(0, 2**32 - 1) if seed == None else seed
        self.feed = list() 
        self.history = list() 
        self.users = [User(self.pipeline, id, profile, post_no_memory, post_memory, comment_no_memory, comment_memory, memory_size=self.memory_size) for id, profile in enumerate(self.profiles)] 
        self.active_users = [user for user in self.users]
        self.current_iter = -1
        self.n_nodes = 0
        
        max_seeds =  self.n_users*2 + 1 + 4*(self.n_users-1) + self.n_iter*(self.n_users*6) # number of seeds needed in the worst case scenario
        
        random.seed(self.seed)
        self.seeds = [random.randint(0, 2**32 - 1) for _ in range(max_seeds)]
        
        random.seed(self.seed)
        self.moderate_seeds = [random.randint(0, 2**32 - 1) for _ in range(self.n_users*50)]
        
        try:       
            for i in tqdm(range(self.n_iter), desc=f'Simulation'):
                self.current_iter += 1
                if len(self.active_users): 
                    self._step() 
                else:
                    warnings.warn('All users have been banned.')
                    break
                self.export(export_path)
        except KeyboardInterrupt:
            raise
    
    def export(self, 
               path=None):
        '''Exports data of experiment as JSON.'''
        
        if not self.history:
            raise TypeError('simulation data not found: execute run() before exporting data')
        
        data = list()
        
        for time in self.history:
            for record in time:
                example = record
                example.update({
                                'simulate_seed':self.seed,
                                'thread_prob':self.thread_prob,
                                'comment_prob':self.comment_prob,
                                'exante':self.exante,
                                'ban':self.ban,
                                'memory_size':self.memory_size,
                                'osfa':self.osfa,
                                'tolerance':self.tolerance,
                                'generation_config':self.generation_config, 
                               })
                example.update(self.get_user_by_id(example['user_id']).profile)
                data.append(example)
                
        data = pd.DataFrame(data)
        if path is None:
            raise TypeError('you must enter a valid path for dowloading json file')
        else:
            data.to_json(path, orient='table', index=False)
    
