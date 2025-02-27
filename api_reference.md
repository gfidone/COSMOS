<img src="docs/circle.png" alt="Descrizione" width="150" align="left">

# API Reference
</br>
</br>
</br>

## Class `Simulator`
### Methods
- `__init__(model_path, thread_prob, comment_prob, tau, thr, topics, moderate_template, profiles)`
  
  **Inizializes a COSMOS object.** These parameters are located in the `init` section of `experiments/config.json`.
   
    - `model_path` (*str*): path to the LLM (HuggingFace Hub).
    - `thread_prob` (*float*): probability to generate a post.
    - `comment_prob` (*float*): probability to generate a comment.
    - `tau` (*float*): temperature of the softmax function for selecting a node of the news feed.
    - `thr` (*float*): toxicity threshold for moderator activation.
    - `topics` (*list[str]*): array of topics for generating a post.
    - `moderate_template` (*str*): prompt template for moderator in PMI mode. For correct processing, it must feature `<personal information></personal information>` (profile module) and `<user submission>{content}</user submission>` (user submission).
    - `profiles` (*list[dict]*): profile modules (as a list of dictionaries). `username` is mandatory.

- `run(n_timesteps, post_no_memory, post_memory, comment_no_memory, comment_memory, intervene=True, intervene_func=None, ban=False, memory_size=1, one_size_fits_all=False, intervention=None, tolerance=None, generation_config=None, seed=None, active_stream=True)`

    **Runs a simulation.** These parameters are located in the `run` section of `experiments/config.json`.
    - `n_timesteps` (*int*): number of timestamps.
    - `post_no_memory` (*str*): prompt template for post action without memory. For correct processing, it must feature `<personal information></personal information>` (profile module) and `{topic}` (sensory module).
    - `post_memory` (*str*): prompt template for post action with memory. For correct processing, it must feature `<personal information></personal information>` (profile module), `<intervention>{intervention}</intervention>` (memory module) and `{topic}` (sensory module).
    - `comment_no_memory` (*str*): prompt template for comment action without memory. For correct processing, it must feature `<personal information></personal information>` (profile module) and `<thread>{thread}</thread>` (sensory module).
    - `comment_memory` (*str*): prompt template for comment action with memory. For correct processing, it must feature `<personal information></personal information>` (profile module), `<thread>{thread}</thread>` (sensory module) and `<intervention>{intervention}</intervention>` (memory module).
    - `intervene` (*bool*, default `True`): use *ex ante* interventions or not.
    - `intervene_func` (*callable | None*, default `None`): wrapper for external *ex ante* function. Requires `intervene=True`.
    - `ban` (*bool*, default `False`): use ban or not.
    - `tolerance` (*int | None*, default `None`): maximum number of infractions before the user is banned. Requires `ban=True`.
    - `memory_size` (default 1): maximum number of interventions stored in memory.
    - `one_size_fits_all` (*bool*, default `False`): use OFSA strategy. Requires `intervene=True`.
    - `intervention` (*str | None*, default `None`): message of OFSA strategy. Requires `one_size_fits_all=True`.
    - `generation_config` (*dict | None*, default `None`): configuration for LLM generation as a dictionary of parameters. `max_new_tokens` is mandatory.
    - `seed` (*int | None*, default `None`): random seed for reproducibility.
    - `active_stream`(*bool*, default `True`): generate counterfactual or not.
- `export(path)`
  
  **Exports results in JSON format.** These parameters are located in the `export` section of `experiments/config.json`.
   - `path` (*str*): path to JSON file with simulation results.
     
### Attributes
- `feed` (*list[networkx.DiGraph]*): array of threads as directed graphs (`networkx`).
- `history` (*list[list[dict]*): array of timestamps, where each timestamp is an array containing dictionaries for storing information about each action.

## Output JSON fields

- `user_id`: ID of the user  
- `memory`: Content of the memory module  
- `time`: Timestamp  
- `seed`: Random seed used at inference time  
- `topic`: Topic to populate the sensory module (only for posts)  
- `thread_id`: ID of the thread 
- `node_id`: ID of the node 
- `root_id`: `node_id` of the root  
- `parent_id`: `node_id` of the parent (if `None`, the submission is a post)  
- `b_prompt`: Prompt before moderation  
- `a_prompt`: Prompt after moderation  
- `b_output`: Output before moderation  
- `a_output`: Output after moderation  
- `b_tags`: Flag for XML tags correctly formatted in `b_output`  
- `a_tags`: Flag for XML tags correctly formatted in `a_output`  
- `b_content`: Text within XML tags in `b_output`  
- `a_content`: Text within XML tags in `a_output`  
- `b_toxicity`: Toxicity of `b_content` (Perspective API)  
- `a_toxicity`: Toxicity of `a_content` (Perspective API)  
- `censored`: Flag for submission censored as an indirect effect of ban  
- `banned`: Flag for submission censored as a direct effect of ban  
- `out_degree`: Out-degree of node  
- `simulate_seed`: COSMOS random seed 
- `thread_prob`: Probability to post  
- `comment_prob`: Probability to comment  
- `intervene`: Flag for ex-ante interventions  
- `ban`: Flag for ban  
- `ofsa`: Flag for one-size-fits-all strategy (if `False` and `intervene` is `True`, strategy is PMI)  
- `tolerance`: Ban tolerance (*e*)  
- `moderate_prompt`: Prompt for generating PMI about `a_content`  
- `intervention`: PMI generated about `a_content`  
- `username`: User's username  
- `age`: User's age  
- `gender`: User's gender  
- `race`: User's race  
- `income`: User's income  
- `education`: User's education  
- `sex orientation`: User's sex orientation  
- `political leaning`: User's political leaning  
- `religion`: User's religion  
- `agreeableness`: User's agreeableness (OCEAN)  
- `openness`: User's openness (OCEAN)  
- `conscientiousness`: User's conscientiousness (OCEAN)  
- `extraversion`: User's extraversion (OCEAN)  
- `neuroticism`: User's neuroticism (OCEAN)  
- `do_sample`: `do_sample` parameter (see transformers.GenerationConfig)  
- `temperature`: `temperature` parameter (see transformers.GenerationConfig)  
- `max_new_tokens`: `max_new_tokens` parameter (see transformers.GenerationConfig)
