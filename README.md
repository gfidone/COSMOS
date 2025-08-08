<p align="center">
  <img src="docs/cosmos4.png" width="350"/>
</p>

# Welcome to COSMOS!
COSMOS (COunterfactual Simulations of MOderation Strategies) is a simulator of Online Social Network (OSN) conversations based on the Agent-Based Modeling (ABM) framework and powered with a Large Language Model (LLM). COSMOS is designed for evaluating the effectiveness of content moderation strategies on the toxic behavior emerging from users' characteristics and social interplay.

### Why COSMOS?
Assessing if a content moderation strategy is successfull or not can be challenging, for at least three reasons: 

1. The API restrictions imposed by private platforms prevent the collection of large amounts of evidence;
2. Toxic behavior is (fortunately) unfrequent;
3. Field observation can be biased by unknown confounders.
   
With COSMOS, we provide a cost-effective, maximally controllable solution for *generating* your evidence rather than *collecting* it from the real world.

### How does COSMOS work?

COSMOS initializes a population of LLM-based agents with custom social, psychological or demographic characteristics. In a simulation run, agents generate posts and comments in a OSN-like environment. Each action is replicated in a *counterfactual* simulation where a chosen moderation strategy is enforced under *ceteris paribus* conditions. In this way, at the end of the simulation you can tell *what would have happened* if that moderation strategy was employed on that population of users.

# Usage

1. Download this repository on your local machine.
2. Initialize your Perspective API key in `classes/perspective_api.py`. If you do not have one, you can submit a request [here](https://support.perspectiveapi.com/s/docs-get-started).
3. Edit the `experiments/config.json` file with your desired configuration. For details, see `api_reference.md`.
4. Run:

   ```bash
    python3 experiments/main.py 
    ```

Simulation data will be progressively stored into a JSON file at the specified `export_path` in `experiments/config.json`. For details about JSON output fields, see `api_reference.md`.

# License
COSMOS is distributed under the GNU General Public License. Refer to LICENSE.txt for details.
