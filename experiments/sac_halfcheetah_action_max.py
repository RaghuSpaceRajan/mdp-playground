'''###IMP dummy_seed should always be last in the order in the OrderedDict below!!!
'''
num_seeds = 10

from collections import OrderedDict
var_env_configs = OrderedDict({
    "action_space_max": [0.25, 0.5, 1.0, 2.0, 4.0],
})

var_configs = OrderedDict({
"env": var_env_configs
})

env_config = {
    "env": "HopperWrapper-v3",
    "horizon": 1000,
    "env_config": {
    },
}

algorithm = "SAC"
agent_config = {
    # Initial value to use for the entropy weight alpha.
    "initial_alpha": 0.1,
    "optimization": {
        "actor_learning_rate": 3e-4,
        "critic_learning_rate": 3e-4,
        "entropy_learning_rate": 3e-4,
    },
    # Update the target by \tau * policy + (1-\tau) * target_policy
    "tau": 0.005,
    # How many steps of the model to sample before learning starts.
    "learning_starts": 10000,

    # Apply a state preprocessor with spec given by the "model" config option
    # (like other RL algorithms). This is mostly useful if you have a weird
    # observation shape, like an image. Disabled by default.
    "use_state_preprocessor": False,
    # N-step Q learning
    "n_step": 1,
    # Update the target network every `target_network_update_freq` steps.
    "target_network_update_freq": 1,

    "no_done_at_end": True,

    "buffer_size": 50000,
    # If True prioritized replay buffer will be used.
    "prioritized_replay": True,
    # Alpha parameter for prioritized replay buffer.
    "prioritized_replay_alpha": 0.6,
    # Beta parameter for sampling from prioritized replay buffer.
    "prioritized_replay_beta": 0.4,
    # Time steps over which the beta parameter is annealed.
    # "prioritized_replay_beta_annealing_timesteps": 20000,
    # Final value of beta
    "final_prioritized_replay_beta": 0.4,
    # Epsilon to add to the TD errors when updating priorities.
    "prioritized_replay_eps": 1e-6,

    # "schedule_max_timesteps": 20000,
    "timesteps_per_iteration": 1000,
    # Update the replay buffer with this many samples at once. Note that this
    # setting applies per-worker if num_workers > 1.
    # "rollout_fragment_length": 1,
    "rollout_fragment_length": 1, # Renamed from sample_batch_size in some Ray version
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

    "model": {
        # "custom_preprocessor": "ohe",
        "custom_options": {},  # extra options to pass to your preprocessor
        # "no_final_linear": False,
        # "vf_share_layers": True,
        # "fcnet_activation": "tanh",
        "use_lstm": False,
    },
}
