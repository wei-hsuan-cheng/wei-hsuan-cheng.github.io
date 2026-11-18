---
title: "Legged Robot MPC: Whole-Body Inverse-Dynamics MPC for Humanoids and Wheeled-Bipeds"
collection: projects
permalink: /project/2026-10-legged-robot-mpc
# excerpt: "Short description of project item number 1<br/><img src='/images/500x300.png'>"
date: 2026-10-01
excerpt: "Whole-body inverse-dynamics MPC in <code>ros2_control</code> for the Unitree G1 and H2 humanoids and the Upkie wheeled biped, closed on proprioceptive state estimation and tested in MuJoCo. <a href='https://github.com/wei-hsuan-cheng/legged_robot_mpc_controller' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>legged_robot_mpc_controller</span></a>"
# slidesurl: ''
# paperurl: ''
---

# Project overview

A `ros2_control` implementation of **whole-body inverse-dynamics model predictive control (WB-ID MPC)** for legged and wheeled-legged robots, built on [`ocs2_ros2`](https://github.com/wei-hsuan-cheng/ocs2_ros2) and [`pinocchio`](https://github.com/stack-of-tasks/pinocchio), and tested in ROS 2 Jazzy with MuJoCo simulation.

Every control cycle, the MPC optimises the robot's full configuration and velocity together with the **contact wrenches, generalised accelerations and joint torques** over a 1 s horizon, subject to the full rigid-body dynamics in inverse-dynamics form [1, 2]. The optimal control problem is solved with multiple-shooting SQP and HPIPM [3, 4] at 100 to 200 Hz, the policy is evaluated at 1 kHz, and a joint servo executes it.

The same controller runs on three robots:

- **Unitree G1 and H2 humanoids**: walking, running, stopping and recovering, and uneven terrain with proprioception only.
- **Upkie wheeled biped** [11]: rolling contacts at the tyres (no-slip and contact-gap equalities instead of planted feet), a planned stand-up from kneeling, and driving over ramps, steps and uneven ground.

The floating base comes from proprioceptive state estimation (IMU, joint encoders and the contact schedule; no ground truth in the loop): a contact-aided invariant EKF [9] or a two-stage linear Kalman filter [7], which for the wheeled biped measures the rolling tyres instead of planted feet [8].

The controllers are implemented in `ROS 2 C++` and can be found in <a href='https://github.com/wei-hsuan-cheng/legged_robot_mpc_controller' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>legged_robot_mpc_controller</span></a>, with the solver in <a href='https://github.com/wei-hsuan-cheng/ocs2_ros2' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>ocs2_ros2</span></a>.
{: .notice}


# Demos

<table align="center">
  <tr>
    <td align="center" width="50%">
      <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/g1.gif?raw=true" width="400" alt="Unitree G1 velocity and base-height control" />
    </td>
    <td align="center" width="50%">
      <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/h2_mpc_future_robot_visualization.gif?raw=true" width="400" alt="Unitree H2 MPC future robot visualization" />
    </td>
  </tr>
  <tr>
    <td align="center"><b>Unitree G1</b><br />Velocity and base-height control</td>
    <td align="center"><b>Unitree H2</b><br />Visualization of MPC future robot trajectory</td>
  </tr>
</table>

<p align="center">
  <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/h2_run.gif?raw=true" width="800" alt="H2 runs, stops, stumbles, and regains balance" />
  <br />
  <b>Unitree H2</b><br />Runs, stops, stumbles, and regains balance
</p>

<p align="center">
  <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/h2_uneven_terrain.gif?raw=true" width="700" alt="H2 walking on uneven terrain with proprioception only" />
  <br />
  <b>Unitree H2</b><br />Uneven terrain locomotion with proprioception only
</p>

<p align="center">
  <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/upkie_standup_course.gif?raw=true" width="500" alt="Upkie swings itself up, balances, and drives through uneven terrain with steps and ramps" />
  <br />
  <b>Wheeled-Biped <a href="https://github.com/upkie/upkie">Upkie</a> (with rolling-contact conditions)</b><br />Swings itself up, balances, and drives through uneven terrains with steps and ramps
</p>


# Whole-body inverse-dynamics MPC

## State and input

The floating base uses ZYX Euler angles $$\eta = [\psi, \theta, \phi]^\top$$, so the configuration and velocity have the same dimension $$n_v = 6 + n_j$$:

$$
q = \begin{bmatrix} p_{WB}^{W} \\ \eta \\ q_j \end{bmatrix}, \qquad
v = \dot q, \qquad
x = \begin{bmatrix} q \\ v \end{bmatrix} \in \mathbb{R}^{2 n_v}, \qquad
u = \begin{bmatrix} W_1 \\ \vdots \\ W_{n_c} \\ a \\ \tau_j \end{bmatrix}, \qquad a = \dot v .
$$

Each contact wrench $$W_c = [f_c^\top, m_c^\top]^\top$$ is expressed in world-aligned axes. For the 23-joint G1 model, $$n_v = 29$$, $$\dim x = 58$$ and $$\dim u = 64$$. The initial state $$x(t_0)$$ comes from the state estimator (base pose and twist) and the joint encoders.

## Dynamics: a double integrator plus inverse-dynamics equalities

The state propagates as a double integrator, and the rigid-body physics enters as **state-input equality constraints** through the recursive Newton-Euler algorithm (RNEA) [5], not through forward dynamics:

$$
\dot x = \begin{bmatrix} v \\ a \end{bmatrix}, \qquad
r(q, v, a, W) = \operatorname{RNEA}(q, v, a) - \sum_c J_c(q)^\top W_c = M(q)\, a + b(q, v) - \sum_c J_c(q)^\top W_c .
$$

The six unactuated (floating-base) rows hold over the whole horizon; the actuated rows tie the torque input to the dynamics inside a short torque window $$T_\tau$$ at the start of the horizon:

$$
S_b\, r = 0, \qquad S_j\, r - \tau_j = 0 \quad (t < t_0 + T_\tau).
$$

## Optimal control problem

$$
\min_{x(\cdot),\, u(\cdot)} \; \Phi\big(x(t_f)\big) + \int_{t_0}^{t_f} \Big( \ell_{\mathrm{generic}} + \ell_{\mathrm{base}} + \ell_{\mathrm{task}} + \ell_{\mathrm{soft}} \Big)\, dt
$$

subject to the initial state, the dynamics above, the contact equalities below, and soft inequality constraints. The horizon is 1 s with 0.02 s nodes, solved by multiple-shooting SQP with HPIPM and one SQP iteration per update (a real-time iteration), with OCS2 [3, 4] and CppAD-generated derivatives.

**Costs.** A quadratic regularisation keeps the robot near a nominal posture and spreads the weight $$mg$$ over the $$N_s$$ scheduled stance contacts:

$$
\ell_{\mathrm{generic}} = \tfrac12 \lVert x - x_{\mathrm{nom}} \rVert_Q^2 + \tfrac12 \lVert u - u_{\mathrm{nom}} \rVert_R^2, \qquad
f_{c,\mathrm{nom}} = \begin{cases} [0, 0, mg / N_s]^\top, & c \text{ in stance} \\ 0, & c \text{ in swing} \end{cases}
$$

The base is tracked relative to the commanded twist, so horizontal position and yaw carry no weight (they are unobservable to the estimator and are never fed back):

$$
e_{\mathrm{pose}} = \begin{bmatrix} 0 & 0 & z - z_d & 0 & \theta - \theta_d & \phi - \phi_d \end{bmatrix}^\top, \qquad
e_{v,xy} = R_2(\psi)^\top v_{B,xy}^{W} - R_2(\psi_d)^\top v_{B,d,xy}^{W},
$$

$$
\ell_{\mathrm{base}} = \tfrac12 \left\lVert \begin{bmatrix} e_{\mathrm{pose}} \\ e_{v,xy} \\ v_z - v_{z,d} \\ \dot\eta - \dot\eta_d \end{bmatrix} \right\rVert_{Q_B}^2 .
$$

**Contacts.** The gait prescribes contact flags. A swinging contact carries no wrench, $$W_c = 0$$. A stance foot must not slip or sink, written at acceleration level with Baumgarte-style feedback [10] on the contact velocity $$v_c$$, acceleration $$a_c$$ and height error:

$$
k_a\, a_{c,xy} + k_d\, v_{c,xy} = 0, \qquad
k_a\, a_{c,z} + k_d\, v_{c,z} + k_p\, (z_c - z_{c,d}) = 0, \qquad
k_a\, \dot\omega_c + k_d\, \omega_c + k_p\, d(R_c, n) = 0 .
$$

A swing foot follows the planned vertical spline:

$$
k_a (a_{c,z} - \ddot z_{c,d}) + k_d (v_{c,z} - \dot z_{c,d}) + k_p (z_c - z_{c,d}) = 0 .
$$

**Inequalities.** Friction cone, centre of pressure inside the sole, and joint position, velocity and torque bounds are written as $$h \ge 0$$, for example

$$
h_{\mathrm{fric}} = \mu f_z - \sqrt{f_x^2 + f_y^2 + \varepsilon} \ge 0, \qquad
\bar\tau_j \pm \tau_j \ge 0, \qquad q_j - q_{j,\min} \ge 0,
$$

and enter the cost through a relaxed logarithmic barrier, which stays finite when a margin is violated:

$$
p_{\mu, \delta}(h) = \mu \begin{cases} -\ln h, & h > \delta \\ -\ln \delta + \tfrac12 \left( \dfrac{h - 2\delta}{\delta} \right)^2 - \tfrac12, & h \le \delta . \end{cases}
$$

**Execution.** The policy is evaluated at 1 kHz and executed by a joint servo around the planned trajectory, with the planned torque as feedforward:

$$
\tau_{\mathrm{cmd}} = \tau_{j}^{*} + K_p (q_j^{*} - q_j) + K_d (\dot q_j^{*} - \dot q_j).
$$


# Rolling contact for the wheeled biped

On a wheel, the contact point moves with the robot, so a planted-foot model does not apply. With the axle direction $$e_i = R_i e_{\mathrm{local}}$$, ground normal $$n$$ and tyre radius $$r$$, the contact is the lowest point of the tyre circle [6]:

$$
w_i = n - (e_i^\top n)\, e_i, \qquad
\rho_i = -r \frac{w_i}{\lVert w_i \rVert}, \qquad
p_{c,i} = p_{h,i} + \rho_i ,
$$

where $$p_{h,i}$$ is the tyre centre. What stays at rest under pure rolling is the **tread material** at the contact, not the contact point itself, so the constraints act on its velocity and acceleration (wheel spin included in $$\omega_i$$):

$$
v_{c,i} = v_{h,i} + \omega_i \times \rho_i, \qquad
a_{c,i} = a_{h,i} + \alpha_i \times \rho_i + \omega_i \times \dot\rho_i .
$$

With the rolling direction $$t_i$$ and the contact gap $$g_i = n^\top p_{c,i} - z_i^d$$, each supporting wheel adds five equalities, two for slip and gap and three that reduce its wrench to a point force at the contact:

$$
\begin{aligned}
0 &= k_{a,t} \big( t_i^\top a_{c,i} + \dot t_i^\top v_{c,i} \big) + k_{v,t}\, t_i^\top v_{c,i}, \\
0 &= k_{a,n}\, n^\top a_{c,i} + k_{v,n}\, n^\top v_{c,i} + k_{p,n}\, g_i, \\
0_3 &= m_i - \rho_i \times f_i ,
\end{aligned}
$$

plus one shared row on the mean lateral slip of the supporting wheels. A lifted wheel (in `jump`, `walk` and `trot`) has zero wrench and follows a vertical swing reference instead [12]. The ground-force cone and the joint and torque bounds are the same soft constraints as for the humanoids.


# Proprioceptive state estimation: linear Kalman filter

The MPC needs the base pose and twist, which come from the IMU, the joint encoders and the contact schedule only. The two-stage linear Kalman filter follows MIT Cheetah 3 [7].

**Stage 1, attitude.** The attitude is the IMU's own orientation, with the IMU mounting $$(R_{BI}, r_{BI})$$ removed:

$$
R_{WB} = R_{WI} R_{BI}^\top, \qquad
\omega_B = R_{BI}\, \omega_I, \qquad
a_B = R_{BI}\, a_I - \omega_B \times (\omega_B \times r_{BI}).
$$

**Stage 2, position and velocity.** With attitude fixed, the rest is linear. The measured acceleration (not the commanded torque) drives the prediction:

$$
x_{k+1}^- = A x_k + B u_k, \qquad u_k = R_{WB}\, a_B + g, \qquad
A = \begin{bmatrix} I & \Delta t\, I \\ 0 & I \end{bmatrix}, \qquad
B = \begin{bmatrix} \tfrac12 \Delta t^2 I \\ \Delta t\, I \end{bmatrix}, \qquad
P^- = A P A^\top + Q .
$$

Forward kinematics is evaluated with the base at the origin (attitude, base rate and encoders only), so the measurements never depend on the state they correct. Superscript rel marks these base-relative quantities.

- **Legged (point contacts).** The state $$x = [p;\, v;\, c_1, \dots, c_N]$$ also holds the contact points, which a planted foot keeps fixed ($$c_i^+ = c_i$$). Each contact gives its position relative to the base, the base velocity (the foot is at rest) and its height on the ground:

$$
p - c_i = -p_i^{\mathrm{rel}}, \qquad v = -v_i^{\mathrm{rel}}, \qquad c_{i,z} = 0 .
$$

- **Wheeled (rolling contacts).** A rolling contact is no landmark, so the state is $$x = [p;\, v]$$. Each wheel measures the base velocity from the tread at rest (legs and wheel spin together) and the base height from its contact on the ground plane:

$$
v = -\big( v_{h,i}^{\mathrm{rel}} + \omega_i \times \rho_i \big), \qquad
p_z = z_g - \big( p_{h,i}^{\mathrm{rel}} + \rho_i \big)_z .
$$

A contact scheduled off the ground keeps its rows with 100 times the noise, so the matrix sizes never change. The correction is the standard one:

$$
\nu = y - C x^-, \qquad S = C P^- C^\top + R, \qquad K = P^- C^\top S^{-1}, \qquad
x = x^- + K \nu, \qquad P = (I - K C)\, P^- .
$$

With the shipped noise values the filter acts as a complementary filter with a crossover near 2 Hz: the integrated IMU carries fast motion, and the kinematics anchor the slow motion. The height it reports is the height above the ground under the robot, not world height, so the robot does not crouch on high ground or stretch on low ground. Because the prediction uses the measured acceleration rather than the commanded input, the control never enters the estimation error, unlike an LQG observer. In noise-free simulation, the wheeled filter tracks the base height to 0.2 mm RMS and the forward velocity to 1 mm/s RMS while rolling at 0.3 m/s.


# Resources

- [legged_robot_mpc_controller](https://github.com/wei-hsuan-cheng/legged_robot_mpc_controller): controllers, configurations, tests and formulation notes
- [ocs2_ros2](https://github.com/wei-hsuan-cheng/ocs2_ros2): OCS2 for ROS 2 with the SQP and HPIPM solver used here
- [legged_state_estimator](https://github.com/wei-hsuan-cheng/legged_state_estimator): contact-aided invariant EKF library
- [mujoco_ros2_control](https://github.com/wei-hsuan-cheng/mujoco_ros2_control): MuJoCo simulation for `ros2_control`
- [Demo GIFs](https://github.com/wei-hsuan-cheng/gifs/tree/main/legged_robot_mpc_controller)


# References

1. L. Molnar et al., "Whole-Body Inverse Dynamics MPC for Legged Loco-Manipulation," 2025. [arXiv:2511.19709](https://arxiv.org/abs/2511.19709)
2. C. Khazoom et al., "Tailoring Solution Accuracy for Fast Whole-body Model Predictive Control of Legged Robots," 2024. [arXiv:2407.10789](https://arxiv.org/abs/2407.10789)
3. F. Farshidian et al., "OCS2: An open source library for Optimal Control of Switched Systems." [GitHub](https://github.com/leggedrobotics/ocs2)
4. G. Frison and M. Diehl, "HPIPM: a high-performance quadratic programming framework for model predictive control," IFAC-PapersOnLine, 2020. [arXiv:2003.02547](https://arxiv.org/abs/2003.02547)
5. J. Carpentier et al., "The Pinocchio C++ library: A fast and flexible implementation of rigid body dynamics algorithms and their analytical derivatives," IEEE/SICE SII, 2019. [GitHub](https://github.com/stack-of-tasks/pinocchio)
6. S. Xin and S. Vijayakumar, "Online Dynamic Motion Planning and Control for Wheeled Biped Robots," IEEE/RSJ IROS, 2020. [arXiv:2003.03678](https://arxiv.org/abs/2003.03678)
7. G. Bledt et al., "MIT Cheetah 3: Design and Control of a Robust, Dynamic Quadruped Robot," IEEE/RSJ IROS, 2018. [DOI](https://doi.org/10.1109/IROS.2018.8593885)
8. M. Hosseini, D. Rodriguez and S. Behnke, "State Estimation for Hybrid Locomotion of Driving-Stepping Quadrupeds," IEEE IRC, 2022. [arXiv:2211.11390](https://arxiv.org/abs/2211.11390)
9. R. Hartley et al., "Contact-Aided Invariant Extended Kalman Filtering for Legged Robot State Estimation," RSS, 2018. [arXiv:1805.10410](https://arxiv.org/abs/1805.10410)
10. J. Baumgarte, "Stabilization of constraints and integrals of motion in dynamical systems," Computer Methods in Applied Mechanics and Engineering, 1972. [DOI](https://doi.org/10.1016/0045-7825(72)90018-7)
11. Upkie wheeled biped, open-source robot by S. Caron et al. [GitHub](https://github.com/upkie/upkie)
12. M. Bjelonic et al., "Whole-Body MPC and Online Gait Sequence Generation for Wheeled-Legged Robots," IEEE/RSJ IROS, 2021. [arXiv:2010.06322](https://arxiv.org/abs/2010.06322)
