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

- `run(n_timesteps, post_no_memory, post_memory, comment_no_memory, comment_memory, exante=True, func=None, ban=False, memory_size=1, osfa=False, default=None, tolerance=None, generation_config=None, seed=None, active_stream=True)`

    **Runs a simulation.** These parameters are located in the `run` section of `experiments/config.json`.
    - `n_iter` (*int*): number of iterations (timestamps).
    - `post_no_memory` (*str*): prompt template for post action without memory. For correct processing, it must feature `<personal information></personal information>` (profile module) and `{topic}` (sensory module).
    - `post_memory` (*str*): prompt template for post action with memory. For correct processing, it must feature `<personal information></personal information>` (profile module), `<intervention>{intervention}</intervention>` (memory module) and `{topic}` (sensory module).
    - `comment_no_memory` (*str*): prompt template for comment action without memory. For correct processing, it must feature `<personal information></personal information>` (profile module) and `<thread>{thread}</thread>` (sensory module).
    - `comment_memory` (*str*): prompt template for comment action with memory. For correct processing, it must feature `<personal information></personal information>` (profile module), `<thread>{thread}</thread>` (sensory module) and `<intervention>{intervention}</intervention>` (memory module).
    - `exante` (*bool*, default `True`): use *ex ante* moderation or not.
    - `func` (*callable | None*, default `None`): wrapper for external *ex ante* function. Requires `exante=True`.
    - `ban` (*bool*, default `False`): use ban or not.
    - `tolerance` (*int | None*, default `None`): maximum number of infractions before the user is banned. Requires `ban=True`.
    - `memory_size` (default 1): maximum number of interventions stored in memory.
    - `osfa` (*bool*, default `False`): use OFSA strategy. Requires `exante=True`.
    - `default` (*str | None*, default `None`): default message for OFSA. Requires `osfa=True`.
    - `generation_config` (*dict | None*, default `None`): configuration for LLM generation as a dictionary of parameters. `max_new_tokens` is mandatory.
    - `seed` (*int | None*, default `None`): random seed for reproducibility.
    - `active_stream`(*bool*, default `True`): generate counterfactual or not.
    - `path` (*str*): path to JSON file with simulation results.
     
### Attributes
- `feed` (*list[networkx.DiGraph]*): array of threads as directed graphs (`networkx`).
- `history` (*list[list[dict]*): array of timestamps, where each timestamp is an array containing dictionaries for storing information about each action.

## Output JSON fields

- `user_id`: id of the user  
- `memory`: content of the memory module  
- `time`: timestamp  
- `seed`: random seed used at inference time  
- `topic`: topic to populate the sensory module (only for posts)  
- `thread_id`: id of the thread  
- `node_id`: id of the node  
- `root_id`: `node_id` of the root  
- `parent_id`: `node_id` of the parent (if `None`, the submission is a post)  
- `b_prompt`: prompt before moderation  
- `a_prompt`: prompt after moderation  
- `b_output`: output before moderation  
- `a_output`: output after moderation  
- `b_tags`: flag for XML tags correctly formatted in `b_output`  
- `a_tags`: flag for XML tags correctly formatted in `a_output`  
- `b_content`: text within XML tags in `b_output`  
- `a_content`: text within XML tags in `a_output`  
- `b_toxicity`: toxicity of `b_content` (Perspective API)  
- `a_toxicity`: toxicity of `a_content` (Perspective API)  
- `censored`: flag for submission censored as an indirect effect of ban  
- `banned`: flag for submission censored as a direct effect of ban  
- `out_degree`: out-degree of node  
- `simulate_seed`: COSMOS random seed  
- `thread_prob`: probability to post  
- `comment_prob`: probability to comment  
- `exante`: flag for ex-ante interventions  
- `ban`: flag for ban  
- `osfa`: flag for one-size-fits-all strategy (if `False` and `intervene` is `True`, strategy is PMI)  
- `tolerance`: ban tolerance (*e*)  
- `moderate_prompt`: prompt for generating PMI about `a_content`  
- `intervention`: PMI generated about `a_content`  
- `do_sample`: `do_sample` parameter (see `transformers.GenerationConfig`)  
- `temperature`: `temperature` parameter (see `transformers.GenerationConfig`)  
- `max_new_tokens`: `max_new_tokens` parameter (see `transformers.GenerationConfig`)
- `username`: user's username

Beyond `username`, output JSON fields also include all the attributes used for profile modules.

