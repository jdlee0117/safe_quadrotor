# Safe Quadrotor Control and Simulation

## Overview
This repository houses a simulator and controller for a quadcopter with a multi-rate controller running a slow MPC linearization-based controller for high-level planning composed with a fast CBF nonlinear controller for low-level safe corrections. The implementation details are based on the work "Multi-Rate Control Design Leveraging Control Barrier Functions and Model Predictive Control Policies" by Rosolia and Ames. It fulfilled a project requirement for the course AA203 at Stanford University.

## Environmental Management
Make sure you run the project in a conda virtual environment. To make an environment,
```
conda create --name <env_name> python=3.8
```
Anytime after initializing the environment, activate before using project files:
```
conda activate <env_name>
```
To install the dependencies in the project, after activating the environment for the first time, run
```
pip install -r requirements.txt
```

## Implementations
There are two controllers on master. The first is a simple PD controller and the second is the safe multirate MPC controller. You can adjust the rates at which the CBF is applied and the MPC discretization. The logic for generating the CBFs and their Lie derivatives is located in proj/extra as a MATLAB script. There is currently only support for spherical obstacles.

To run the code, change the settings in ```proj_script.py``` and run it. There is currently no argparse support.

## Citing
If this work is at all useful for you, please use the following citation.
```
@misc{Li2020_safe_quad,
  author = {Albert Li, Daniel Sotsaikich, Brent Yi},
  title = {Safe Quadrotor Control and Simulation},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/alberthli/safe_quadrotor}},
}
```
