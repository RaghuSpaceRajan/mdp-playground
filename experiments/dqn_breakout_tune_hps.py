import itertools
from ray import tune
from collections import OrderedDict
num_seeds = 3
timesteps_total = 3_000_000

var_env_configs = OrderedDict(
    {
        "dummy_seed": [i for i in range(num_seeds)],
    }
)

var_agent_configs = OrderedDict(
    {
        # Learning rate
        # "lr": [1e-3, 1e-4], #
        "exploration_config": [
            {"epsilon_timesteps": 200000, "final_epsilon": 0.01},
            {"epsilon_timesteps": 200000, "final_epsilon": 0.05},
        ],
        # 'learning_starts': [10000, 20000],
        # 'hiddens': [[512]],
        "target_network_update_freq": [2000, 4000, 8000, 16000],
    }
)

var_configs = OrderedDict(
    {
        "env": var_env_configs,
        "agent": var_agent_configs,
    }
)

env_config = {
    "env": "GymEnvWrapper-Atari",
    "env_config": {
        "AtariEnv": {
            "game": "breakout",
            "obs_type": "image",
            "frameskip": 1,
        },
        # "GymEnvWrapper": {
        "atari_preprocessing": True,
        "frame_skip": 4,
        "grayscale_obs": False,
        "state_space_type": "discrete",
        "action_space_type": "discrete",
        "seed": 0,
        # },
        # 'seed': 0, #seed
    },
}

algorithm = "DQN"
agent_config = {  # Taken from Ray tuned_examples
    "adam_epsilon": 0.00015,
    "buffer_size": 500000,
    "double_q": False,
    "dueling": False,
    # 'exploration_config': {   'epsilon_timesteps': 200000,
    # 'final_epsilon': 0.01},
    "final_prioritized_replay_beta": 1.0,
    "hiddens": [512],
    "learning_starts": 20000,
    "lr": 6.25e-05,
    "n_step": 1,
    "noisy": False,
    "num_atoms": 1,
    "num_gpus": 0,
    "num_workers": 3,
    "prioritized_replay": False,
    "prioritized_replay_alpha": 0.5,
    "prioritized_replay_beta_annealing_timesteps": 2000000,
    "rollout_fragment_length": 4,
    # 'target_network_update_freq': 8000,
    "timesteps_per_iteration": 10000,
    "train_batch_size": 32,
    "tf_session_args": {
        # note: overriden by `local_tf_session_args`
        "intra_op_parallelism_threads": 4,
        "inter_op_parallelism_threads": 4,
        # "gpu_options": {
        #     "allow_growth": True,
        # },
        # "log_device_placement": False,
        "device_count": {"CPU": 2},
        # "allow_soft_placement": True,  # required by PPO multi-gpu
    },
    # Override the following tf session args on the local worker
    "local_tf_session_args": {
        "intra_op_parallelism_threads": 4,
        "inter_op_parallelism_threads": 4,
    },
}


model_config = {
    # "model": {
    #     "fcnet_hiddens": [256, 256],
    #     "fcnet_activation": "tanh",
    #     "use_lstm": False,
    #     "max_seq_len": 20,
    #     "lstm_cell_size": 256,
    #     "lstm_use_prev_action_reward": False,
    # },
}


eval_config = {
    "evaluation_interval": None,  # I think this means every x training_iterations
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
value_tuples = []
for config_type, config_dict in var_configs.items():
    for key in config_dict:
        assert (
            isinstance(var_configs[config_type][key], list)
        ), "var_config should be a dict of dicts with lists as the leaf values to allow each configuration option to take multiple possible values"
        value_tuples.append(var_configs[config_type][key])


cartesian_product_configs = list(itertools.product(*value_tuples))
print("Total number of configs. to run:", len(cartesian_product_configs))
