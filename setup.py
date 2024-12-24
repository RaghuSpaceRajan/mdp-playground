from setuptools import setup

packages = [
    "mdp_playground",
    "mdp_playground.analysis",
    "mdp_playground.config_processor",
    "mdp_playground.envs",
    "mdp_playground.scripts",
    "mdp_playground.spaces",
]

package_data = {"": ["*"]}

extras_require = [
    "ray[default,rllib]>=1.0.0",
    "tensorflow>=2.5.0",
    "pillow>=6.1.0",
    "requests>=2.22.0",
    "configspace>=0.4.10",
    "scipy>=1.7.0",
    "pandas>=0.25.0",
    "gym[atari]<=0.25",
    "matplotlib",
    "opencv-python>=4.2.0.34",  # due to https://stackoverflow.com/questions/72706073/attributeerror-partially-initialized-module-cv2-has-no-attribute-gapi-wip-gs
    "opencv-python-headless>=4.2.0.34", # and https://stackoverflow.com/questions/70537488/cannot-import-name-registermattype-from-cv2-cv2
]

extras_require_disc = [
    "ray[rllib,debug]==0.7.3",
    "tensorflow==1.13.1",
    "pillow>=6.1.0",
    "requests==2.22.0",
    "configspace==0.4.10",
    "scipy==1.3.0",
    "pandas==0.25.0",
    "gym[atari]==0.14",
    "atari-py==0.2.5",  # https://github.com/openai/atari-py/issues/81 #TODO Remove
    "matplotlib==3.2.1",  # #TODO Remove?
    "pillow==9.3.0",
]

extras_require_cont = [
    # 'ray[rllib,debug]==0.9.0',
    "tensorflow==2.2.0",
    "tensorflow-probability==0.9.0",
    "requests==2.22.0",
    "mujoco-py==2.0.2.13",  # with mujoco 2.0
    "configspace>=0.4.10",
    "scipy>=1.3.0",
    "pandas==0.25.0",
    "gym[atari]==0.14",
    "atari-py==0.2.5",  # https://github.com/openai/atari-py/issues/81 #TODO Remove
    "matplotlib==3.2.1",  # #TODO Remove?
    "pillow==9.3.0",
]

hpo_analysis_require = [
    "cave>=1.4.0",
]

AUTHORS = (
    ", ".join(
        [
            "Raghu Rajan",
            "Jessica Borja",
            "Suresh Guttikonda",
            "Fabio Ferreira",
            "Jan Ole von Hartz",
            "André Biedenkapp",
            "Frank Hutter",
        ]
    ),
)

AUTHOR_EMAIL = "rajanr@cs.uni-freiburg.de"

LICENSE = "Apache License, Version 2.0"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mdp-playground",
    version="1.0.0",
    author=AUTHORS,
    author_email=AUTHOR_EMAIL,
    description="A python package to design and debug RL agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url="https://github.com/automl/mdp-playground",
    project_urls={
        "Bug Tracker": "https://github.com/automl/mdp-playground/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        # 'Topic :: Scientific/Engineering :: Machine Learning',
        # 'Topic :: Scientific/Engineering :: Reinforcement Learning', invalid classifiers on Pypi
    ],
    # package_dir={"": "src"},
    py_modules=[],
    python_requires=">=3.6",
    setup_requires=["numpy"],
    install_requires=["dill", "numpy", "scipy", "pillow", "gymnasium"],
    extras_require={
        "extras": extras_require,
        "extras_disc": extras_require_disc,
        "extras_cont": extras_require_cont,
        "hpo_analysis": hpo_analysis_require,
    },
    entry_points={
        "console_scripts": """
            run-mdpp-experiments = mdp_playground.scripts.run_experiments:cli
        """
    },
)
