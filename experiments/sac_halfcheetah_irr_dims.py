"""
"""
from ray import tune
from collections import OrderedDict
from mdp_playground.config_processor import *
num_seeds = 5
timesteps_total = 3000000


var_env_configs = OrderedDict(
    {
        "irr_state_space_dim": [
            2,
            4,
            8,
            16,
            32,
        ],
        "dummy_seed": [i for i in range(num_seeds)],
    }
)

var_configs = OrderedDict({"env": var_env_configs})

env_config = {
    "env": "HalfCheetahWrapper-v3",
    "horizon": 1000,
    "soft_horizon": False,
    "env_config": {
        "irrelevant_features": {
            # "target_point": [0, 0],
            # "target_radius": 0.5,
            "state_space_max": 10,
            "action_space_max": 1,
            "action_loss_weight": 0.0,
            "time_unit": 1.0,
            "transition_dynamics_order": 1,
            "state_space_type": "continuous",
            "reward_function": "move_to_a_point",
            "dtype": np.float64,
            },
        "seed": 0,  # seed
        "state_space_type": "continuous",
        "action_space_type": "continuous",
        "MujocoEnv": {},
    },
}

algorithm = "SAC"
agent_config = {
    "optimization": {
        "actor_learning_rate": 3e-4,
        "critic_learning_rate": 3e-4,
        "entropy_learning_rate": 3e-4,
    },
    # Update the target by \tau * policy + (1-\tau) * target_policy
    "tau": 0.005,
    # How many steps of the model to sample before learning starts.
    "learning_starts": 10000,
    # N-step Q learning
    "n_step": 1,
    # Update the target network every `target_network_update_freq` steps.
    "target_network_update_freq": 1,
    "target_entropy": "auto",
    "no_done_at_end": True,
    # If True prioritized replay buffer will be used.
    "prioritized_replay": True,
    # "schedule_max_timesteps": 20000,
    "timesteps_per_iteration": 1000,
    # Update the replay buffer with this many samples at once. Note that this
    # setting applies per-worker if num_workers > 1.
    # "rollout_fragment_length": 1,
    "rollout_fragment_length": 1,  # Renamed from sample_batch_size in some Ray version
    "train_batch_size": 256,
    "min_iter_time_s": 0,
    "num_workers": 0,
    "num_gpus": 0,
    "clip_actions": False,
    "normalize_actions": True,
    #    "evaluation_interval": 1,
    "metrics_smoothing_episodes": 5,
}


model_config = {
    "Q_model": {
        "fcnet_activation": "relu",
        "fcnet_hiddens": [256, 256],
    },
    "policy_model": {
        "fcnet_activation": "relu",
        "fcnet_hiddens": [256, 256],
    },
}


eval_config = {
    "evaluation_interval": 1,  # I think this means every x training_iterations
    "evaluation_config": {
        "explore": False,
        "exploration_fraction": 0,
        "exploration_final_eps": 0,
        "evaluation_num_episodes": 10,
        "horizon": 100,
        "env_config": {
            "dummy_eval": True,  # hack Used to check if we are in evaluation mode or training mode inside Ray callback on_episode_end() to be able to write eval stats
            "transition_noise": 0
            if "state_space_type" in env_config["env_config"]
            and env_config["env_config"]["state_space_type"] == "discrete"
            else tune.function(lambda a: a.normal(0, 0)),
            "reward_noise": tune.function(lambda a: a.normal(0, 0)),
            "action_loss_weight": 0.0,
        },
    },
}
