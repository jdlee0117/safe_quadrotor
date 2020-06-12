import numpy as np

from mpccbfs.quadrotor import Quadrotor
from mpccbfs.simulator import SimulationEnvironment
from mpccbfs.controllers import MultirateQuadController, PDQuadController
from mpccbfs.obstacles import Obstacle, SphereObstacle
import matplotlib.pyplot as plt


"""
CURRENT USAGE
-------------
[1] To see obstacle CBF, just run with an obstacle list
[2] To see speed constraint, just make obstacle list None

The only reason [2] works is because right now the slow controller is hard-coded
to just always input a vertical thrust no matter what. There's no additional
complex controller being composed with the low-level safe controller.


TODO
----
- Finish designing the slow update in the multirate controller
- Test disturbances
- Make a safe PD controller as a comparative baseline for the safe MPC

- Maybe: look for niche 3d aspect ratio workaround so spheres look proper
"""

# QUADROTOR #
m = 1.                     # mass
I = np.array([1., 1., 1.]) # principal moments of inertia
kf = 1.                    # thrust factor
km = 1.                    # drag factor
l = 0.1                    # rotor arm length
Jtp = None                  # Optional: total rot moment about prop axes (gyro)

quad = Quadrotor(m, I, kf, km, l, Jtp)


# CONTROLLERS #

# multirate controller - TODO: write the slow update
slow_rate = 10.       # slow controller rate
fast_rate = 100.      # fast controller rate
lv_func = lambda x: 0.0001 * x # class-K function for relative degree 1 constraints
c1 = 0.005               # limits for ECBF pole placement
c2 = 0.01
safe_dist = 0.05      # safe distance from obstacles
safe_rot = 0.2      # safe rotation angle (rad)
safe_vel = 100.        # safe linear velocity
mpc_T = 5             # MPC planning steps
mpc_P = np.eye(12)          # terminal cost - None means DARE solution
mpc_P[0:3, 0:3] *= 5
mpc_Q = np.eye(12)    # state cost
mpc_Q[0:3, 0:3] *= 5
mpc_R = 0.01 * np.eye(4)     # control cost
ref = lambda t: np.array([
    1., 0., 0.,
    0., 0., 0.,
    0., 0., 0.,
    0., 0., 0.
])
# def ref_func(t, quad):
#     _ref = np.zeros(12)
#     _ref[0:2] = np.array([0.3 * np.cos(0.1*t), 0.3 * np.sin(0.1*t)])
#     _ref[6:9] = quad._Rwb(np.zeros(3)).T @ np.array([-0.03 * np.sin(t), 0.03 * np.cos(t), 0.])
#     return _ref
# ref = lambda t: ref_func(t, quad)

mrc = MultirateQuadController(
    quad,
    slow_rate,
    fast_rate,
    lv_func,
    c1,
    c2,
    safe_dist,  
    safe_rot, 
    safe_vel,
    mpc_T,
    mpc_P,
    mpc_Q,
    mpc_R,
    ref,
)

# pd controller
sim_dt = 0.01 # dt for simulation
kp_xyz = 0.02 # gains for Cartesian position control
kd_xyz = 0.04
kp_a = 10     # gains for attitude control
kd_a = 5
ref = lambda t: np.array([0.3 * np.cos(t/10), 0.3 * np.sin(t/10), 0, 0]) # reference

pdc = PDQuadController(
    quad,
    sim_dt,
    kp_xyz,
    kd_xyz,
    kp_a,
    kd_a,
    ref,
)


# OBSTACLES #
obs1 = SphereObstacle(
    np.array([0., 0., 0.3]), # position
    0.1                      # radius
)
obs_list = [obs1]
obs_list = None


# SIMULATOR #
controller = mrc
simulator = SimulationEnvironment(
    quad,     # quadcopter
    controller,      # controller
    obs_list, # obstacle list
    (-2, 2),  # xyz limits
    (-2, 2),
    (-2, 2)
)



if __name__ == "__main__":
    s0 = np.zeros(12) # initial state
    tsim = np.linspace(0, 5, 51) # query times
    sim_data = simulator.simulate(
        s0,
        tsim,
        dfunc=None,    # disturbance function
        animate=True,
        anim_name='meh1.mp4' # 'NAME.mp4' to save the run
    )

    states = np.array(controller.debug_dict["true_state"])
    refs = np.array(controller.debug_dict["ref_state"])
    times = np.array(controller.debug_dict["time"])
    fig, axs = plt.subplots(states.shape[1])
    for i, (state, ref) in enumerate(zip(states.T, refs.T)):
        axs[i].plot(times, state)
        axs[i].plot(times, ref)
    axs[0].set_title("states")
    plt.show()

    inputs = np.array(controller.debug_dict["input"])
    fig, axs = plt.subplots(inputs.shape[1])
    for i, u_i in enumerate(inputs.T):
        axs[i].plot(times, u_i)
    axs[0].set_title("inputs")
    plt.show()
    if isinstance(controller, MultirateQuadController):
        inputs_slow = np.array(controller.debug_dict["input_slow"])
        inputs_fast = np.array(controller.debug_dict["input_fast"])
        fig, axs = plt.subplots(inputs_slow.shape[1])
        for i, (u_i_slow, u_i_fast) in enumerate(zip(inputs_slow.T, inputs_fast.T)):
            axs[i].plot(times, u_i_slow)
            axs[i].plot(times, u_i_fast)
        axs[0].set_title("slow and fast input")
        plt.show()
