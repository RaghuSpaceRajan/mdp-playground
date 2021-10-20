import itertools
from ray import tune
from collections import OrderedDict
num_seeds = 5
timesteps_total = 10_000_000

var_env_configs = OrderedDict(
    {
        "image_transforms": [
            "shift",
            # "scale",
            # "flip",
            # "rotate",
            # "shift,scale,rotate,flip",
        ],  # image_transforms,
        "image_sh_quant": [2, 4, 8, 16],
        "dummy_seed": [i for i in range(num_seeds)],
    }
)

var_configs = OrderedDict({"env": var_env_configs})

env_config = {
    "env": "GymEnvWrapper-Atari",
    "env_config": {
        "AtariEnv": {
            "game": "space_invaders",
            "obs_type": "image",
            "frameskip": 1,
        },
        # "GymEnvWrapper": {
        "atari_preprocessing": True,
        "frame_skip": 4,
        "grayscale_obs": False,  # grayscale_obs gives a 2-D observation tensor.
        "image_width": 40,
        "image_padding": 30,
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
    "buffer_size": 150000,
    "double_q": True,
    "dueling": True,
    "exploration_config": {"epsilon_timesteps": 200000, "final_epsilon": 0.01},
    "final_prioritized_replay_beta": 1.0,
    "hiddens": [512],
    "learning_starts": 20000,
    "lr": 6.25e-05,
    # 'lr': 0.0001,
    # 'model': {   'dim': 42,
    #              'grayscale': True,
    #              'zero_mean': False},
    "n_step": 4,
    "noisy": False,
    "num_atoms": 51,
    "num_gpus": 0,
    "num_workers": 3,
    # "num_cpus_for_driver": 2,
    # 'gpu': False, #deprecated
    "prioritized_replay": True,
    "prioritized_replay_alpha": 0.5,
    "prioritized_replay_beta_annealing_timesteps": 2000000,
    "rollout_fragment_length": 4,
    "timesteps_per_iteration": 10000,
    "target_network_update_freq": 8000,
    # 'target_network_update_freq': 500,
    "train_batch_size": 32,
    "tf_session_args": {
        # note: overriden by `local_tf_session_args`
        "intra_op_parallelism_threads": 4,
        "inter_op_parallelism_threads": 4,
        # "gpu_options": {
        #     "allow_growth": True,
        # },
        # "log_device_placement": False,
        "device_count": {
            "CPU": 2,
            # "GPU": 0,
        },
        # "allow_soft_placement": True,  # required by PPO multi-gpu
    },
    # Override the following tf session args on the local worker
    "local_tf_session_args": {
        "intra_op_parallelism_threads": 4,
        "inter_op_parallelism_threads": 4,
    },
}

# formula [(W−K+2P)/S]+1; for padding=same: P = ((S-1)*W - S + K)/2
filters_124x124 = [
    [
        16,
        [8, 8],
        4,
    ],  # changes from 84x84x1 with padding 4 to 22x22x16 (or 32x32x16 for 124x124x1)
    [32, [4, 4], 2],  # changes to 11x11x32 with padding 2 (or 16x16x32 for 124x124x1)
    [
        256,
        [16, 16],
        1,
    ],  # changes to 1x1x256 with padding 0 (for 124x124x1??); this is the only layer with "valid" padding in Ray!
]

filters_100x100 = [
    [
        16,
        [8, 8],
        4,
    ],  # changes from 42x42x1 with padding 2 to 22x22x16 (or 52x52x16 for 102x102x1)
    [32, [4, 4], 2],
    [
        128,
        [13, 13],
        1,
    ],
]



model_config = {
    "model": {
        "fcnet_hiddens": [256, 256],
        # "custom_preprocessor": "ohe",
        "custom_options": {},  # extra options to pass to your preprocessor
        "conv_activation": "relu",
        "conv_filters": filters_100x100,
        # "fcnet_hiddens": [256, 256],
        # "fcnet_activation": "tanh",
        "use_lstm": False,
        "max_seq_len": 20,
        "lstm_cell_size": 256,
        "lstm_use_prev_action_reward": False,
    },
}


eval_config = {
    "evaluation_interval": None,  # I think this means every x training_iterations
    "evaluation_config": {
        "explore": False,
        "exploration_fraction": 0,
        "exploration_final_eps": 0,
        "evaluation_num_episodes": 10,
        # "horizon": 100,
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
