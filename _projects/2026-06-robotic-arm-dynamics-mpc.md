---
title: "Robotic Arm Dynamics MPC: Inverse- and Forward-Dynamics MPC"
collection: projects
permalink: /project/2026-06-robotic-arm-dynamics-mpc
# excerpt: "Short description of project item number 1<br/><img src='/images/500x300.png'>"
date: 2026-06-01
excerpt: "Joint-space inverse- and forward-dynamics MPC in <code>ros2_control</code> for robotic arms, with end-effector wrench optimisation, self-collision and moving-obstacle avoidance, and momentum-observer wrench estimation, with single- and dual-UR5 examples in MuJoCo. <a href='https://github.com/wei-hsuan-cheng/dynamics_mpc_controller' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>dynamics_mpc_controller</span></a>"
# slidesurl: ''
# paperurl: ''
---

# Project overview

A `ros2_control` implementation of **joint-space dynamics model predictive control** for fixed-base robotic arms, built on [`ocs2_ros2`](https://github.com/wei-hsuan-cheng/ocs2_ros2) and [`pinocchio`](https://github.com/stack-of-tasks/pinocchio), and tested in ROS 2 Jazzy with MuJoCo simulation, with single- and dual-UR5 examples.

Two formulations share the same costs, constraints and controller:

- **Inverse-dynamics MPC**: the MPC optimises joint accelerations, joint torques and the end-effector wrench, and the rigid-body dynamics enters as a recursive Newton-Euler (RNEA) equality constraint [1, 2].
- **Forward-dynamics MPC**: the MPC optimises joint torques, and the articulated-body algorithm (ABA) [1, 2] propagates the state.

Every control cycle, the optimal control problem over a 1 s horizon is solved by multiple-shooting SQP with HPIPM [3, 4] at 100 Hz with one SQP iteration per update (a real-time iteration [5]), the policy is evaluated at 1 kHz, and the planned torque is sent to the joints with a low-gain PD correction. The arm tracks joint or end-effector pose and twist targets, keeps away from itself, from fixed obstacles and from **tracked moving obstacles**, and estimates the external wrench at the end effector with a momentum observer [8, 9].

The controllers are implemented in `ROS 2 C++` and can be found in <a href='https://github.com/wei-hsuan-cheng/dynamics_mpc_controller' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>dynamics_mpc_controller</span></a>, with the solver in <a href='https://github.com/wei-hsuan-cheng/ocs2_ros2' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>ocs2_ros2</span></a>.
{: .notice}


# Demos

<p align="center">
  <img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/dynamics_mpc_controller/ur5_moving_obstacles.gif?raw=true" width="800" alt="UR5 inverse-dynamics MPC tracking joint targets among moving obstacles" />
  <br />
  <b>UR5 inverse-dynamics MPC</b><br />Joint target tracking while avoiding tracked moving obstacles (left: RViz with the MPC plan, future ghosts and obstacle predictions; right: MuJoCo)
</p>


# Inverse-dynamics MPC

## State and input

For an arm with $$n$$ joints, the state holds the joint positions and velocities, and the input holds the joint accelerations, the joint torques and, optionally, the spatial wrench $$F_{\mathrm{ee}} = [f_{\mathrm{ee}}^\top, m_{\mathrm{ee}}^\top]^\top$$ the environment applies at the end effector:

$$
x = \begin{bmatrix} q \\ v \end{bmatrix} \in \mathbb{R}^{2n}, \qquad
u = \begin{bmatrix} a \\ \tau \\ F_{\mathrm{ee}} \end{bmatrix} \in \mathbb{R}^{2n + 6}, \qquad v = \dot q, \quad a = \dot v .
$$

For the UR5, $$\dim x = 12$$ and $$\dim u = 18$$. The initial state $$x(t_0)$$ comes from the joint encoders.

## Dynamics: a double integrator plus an inverse-dynamics equality

The state propagates as a double integrator, and the rigid-body physics enters as a **state-input equality constraint** through RNEA [1, 2], not through forward dynamics:

$$
\dot x = \begin{bmatrix} v \\ a \end{bmatrix}, \qquad
h_{\mathrm{RNEA}}(x, u) = \operatorname{RNEA}(q, v, a) - J_{\mathrm{ee}}(q)^\top F_{\mathrm{ee}} - \tau = 0,
$$

with $$\operatorname{RNEA}(q, v, a) = M(q)\, a + b(q, v)$$ and $$J_{\mathrm{ee}}$$ the end-effector Jacobian. The optimised wrench can track a reference, $$F_{\mathrm{ee}} - F_{\mathrm{ee},d}(t) = 0$$, for contact and force tasks. The equality is generated with CppAD and projected out of the SQP subproblem, so the dynamics is satisfied without adding variables to the QP.

## Optimal control problem

$$
\min_{x(\cdot),\, u(\cdot)} \int_{t_0}^{t_0 + T} \Big( \ell_{\mathrm{joint}} + \ell_{\mathrm{ee}} + \ell_{u} + \ell_{\mathrm{soft}} \Big)\, dt
\quad \text{s.t.} \quad x(t_0) = x_0, \quad \dot x = \begin{bmatrix} v \\ a \end{bmatrix}, \quad h_{\mathrm{RNEA}} = 0,
$$

with $$T$$ = 1 s and 0.02 s nodes.

**Costs.** Joint targets, end-effector pose and twist targets, and the input are tracked with quadratic costs:

$$
\ell_{\mathrm{joint}} = \tfrac12 \lVert x - x_d \rVert_{Q}^2, \qquad
\ell_{\mathrm{ee}} = \tfrac12 \left\lVert \begin{bmatrix} p_{\mathrm{ee}} - p_d \\ \operatorname{qd}(Q_{\mathrm{ee}}, Q_d) \\ V_{\mathrm{ee}} - V_d \end{bmatrix} \right\rVert_{W}^2, \qquad
\ell_{u} = \tfrac12 \lVert u - u_d \rVert_{R}^2,
$$

where $$\operatorname{qd}$$ is the quaternion distance between the end-effector orientation and its target, and the twist $$V_{\mathrm{ee}} = J_{\mathrm{ee}}(q)\, v$$ is expressed in the end-effector or the base frame.

**Inequalities.** Joint position, velocity, acceleration, torque and wrench bounds, self-collision (including fixed obstacles in the URDF), and moving obstacles are written as $$h \ge 0$$, for example

$$
\overline{q} - q \ge 0, \qquad \overline{\tau} \pm \tau \ge 0, \qquad d_{ab}(q) - d_{\min} \ge 0,
$$

with $$d_{ab}$$ the distance between the collision geometries of links $$a$$ and $$b$$ [6]. They enter the cost through a relaxed logarithmic barrier [7], which stays finite when a margin is violated:

$$
\ell_{\mathrm{soft}} = \sum_i p_{\mu, \delta}(h_i), \qquad
p_{\mu, \delta}(h) = \mu \begin{cases} -\ln h, & h > \delta \\ -\ln \delta + \tfrac12 \left( \dfrac{h - 2\delta}{\delta} \right)^2 - \tfrac12, & h \le \delta . \end{cases}
$$

**Execution.** The policy is evaluated at 1 kHz, and the planned torque is executed with a low-gain PD correction around the planned state, then clamped to the torque bounds:

$$
\tau_{\mathrm{cmd}} = \operatorname{clamp}\!\big( \tau^{*} + K_p (q^{*} - q) + K_d (v^{*} - v),\ \underline{\tau},\ \overline{\tau} \big).
$$


# Moving-obstacle avoidance

A tracker (here, a stand-in publisher) reports each moving obstacle $$j$$ as spheres with centres $$c_{jk}$$ in its own frame and radii $$r_{jk}$$, with its pose $$(p_j, R_j)$$ at the message time $$t_s$$, its twist $$(\nu_j, \omega_j)$$ and a position uncertainty $$\sigma_j$$. Over the horizon, each obstacle moves on at constant velocity, and its radius grows with the uncertainty:

$$
s_{jk}(t) = p_j + \Delta t\, \nu_j + \exp\!\big( [\omega_j]_\times \Delta t \big) R_j\, c_{jk}, \qquad
\rho_{jk} = r_{jk} + \kappa\, \sigma_j ,
$$

with $$\Delta t = \operatorname{clamp}(t - t_s,\ 0,\ \Delta t_{\max})$$.

For every collision primitive $$g$$ of the arm links and every obstacle sphere $$i$$, the clearance is the signed distance between the posed primitive and the ball, computed with coal [6], and it enters the cost through the same relaxed barrier:

$$
h_{gi}(q, t) = d\big( g(q),\ \mathcal{B}(s_i(t), \rho_i) \big) - d_{\min}, \qquad
\ell_{\mathrm{obs}} = \sum_{g} \sum_{i} w_i\, p_{\mu, \delta}\big( h_{gi}(q, t) \big).
$$

With $$p_g$$ the witness point on the primitive and $$n_g$$ the unit normal from the primitive to the ball, moving the primitive by $$\delta p_g$$ changes the distance by $$-n_g^\top \delta p_g$$, also when the two penetrate. The gradient comes from the Jacobian of the witness point as a point fixed to the link, and the Hessian is the Gauss-Newton one:

$$
\frac{\partial h_{gi}}{\partial q} = -\, n_g^\top \big( J_v - [p_g - o_g]_\times J_\omega \big), \qquad
\nabla^2_q \ell_{\mathrm{obs}} \approx \sum_{g, i} w_i\, p''_{\mu, \delta}(h_{gi})\, \frac{\partial h_{gi}}{\partial q}^{\!\top} \frac{\partial h_{gi}}{\partial q},
$$

where $$[J_v; J_\omega]$$ is the world-aligned Jacobian of the link's joint at its origin $$o_g$$. A newly seen obstacle's weight $$w_i$$ ramps from 0 to 1 over 0.2 s, so the plan does not jump when it appears. The obstacles change between solves but never during one: right before every solve, the latest message is turned into a snapshot at the MPC start time, which the cost on every solver thread reads.

In the demo above, the arm tracks a joint-space sine while three obstacles move around it (a circling sphere, a bobbing sphere and a spinning dumbbell). Over the 30 s shown, the arm's collision primitives never enter an obstacle (the closest approach is 4 mm), while in the same test with the obstacle term off they pass up to 86 mm into the spheres, 18 % of the time. The term adds about 1.2 ms to each MPC update (3.5 ms instead of 2.3 ms).


# Forward-dynamics MPC

The forward-dynamics MPC optimises the joint torques directly, and the articulated-body algorithm [1, 2] gives the state derivative:

$$
u = \tau \in \mathbb{R}^{n}, \qquad
\dot x = \begin{bmatrix} v \\ \operatorname{ABA}(q, v, \tau) \end{bmatrix} = \begin{bmatrix} v \\ M(q)^{-1} \big( \tau - b(q, v) \big) \end{bmatrix},
$$

with the same tracking costs, input regularisation $$\tfrac12 \lVert \tau - \tau_d \rVert_{R_\tau}^2$$, box constraints and self-collision avoidance; the moving obstacles are in the inverse-dynamics MPC only. There is no equality constraint: the dynamics is integrated (RK4) between the shooting nodes.


# External wrench estimation: momentum observer

The external wrench at the end effector is estimated from the measured joint torques with a generalised-momentum observer [8, 9]. With $$p = M(q)\, v$$ and $$\beta(q, v) = g(q) - C(q, v)^\top v$$, the residual

$$
r(t) = K_O \left( p(t) - \int_0^t \big( \tau_m - \tau_{\mathrm{bias}} - \beta(q, v) + r \big)\, ds \right), \qquad
\dot r = K_O \big( \tau_{\mathrm{ext}} - r \big)
$$

is a first-order filtered estimate of the external joint torque $$\tau_{\mathrm{ext}} = J_{\mathrm{ee}}^\top F_{\mathrm{ext}}$$, with bandwidth $$K_O$$ and no joint acceleration needed. The wrench follows from a weighted, damped least-squares fit, weighted by the joint-torque noise $$\Sigma_\tau$$ and damped more strongly near singular configurations:

$$
\hat F_{\mathrm{ext}} = \big( J_{\mathrm{ee}} \Sigma_\tau^{-1} J_{\mathrm{ee}}^\top + \lambda^2 I \big)^{-1} J_{\mathrm{ee}} \Sigma_\tau^{-1}\, r, \qquad
\lambda = \begin{cases} \lambda_{\mathrm{high}}, & \sigma_{\min}(J_{\mathrm{ee}}) < \sigma_{\mathrm{th}} \\ \lambda_{\min}, & \text{otherwise.} \end{cases}
$$


# Resources

- [dynamics_mpc_controller](https://github.com/wei-hsuan-cheng/dynamics_mpc_controller): controllers, configurations, examples and formulation notes
- [ocs2_ros2](https://github.com/wei-hsuan-cheng/ocs2_ros2): OCS2 for ROS 2 with the SQP and HPIPM solver used here
- [mujoco_ros2_control](https://github.com/wei-hsuan-cheng/mujoco_ros2_control): MuJoCo simulation for `ros2_control`
- [Demo GIFs](https://github.com/wei-hsuan-cheng/gifs/tree/main/dynamics_mpc_controller)


# References

1. R. Featherstone, *Rigid Body Dynamics Algorithms*, Springer, 2008.
2. J. Carpentier et al., "The Pinocchio C++ library: A fast and flexible implementation of rigid body dynamics algorithms and their analytical derivatives," IEEE/SICE SII, 2019. [GitHub](https://github.com/stack-of-tasks/pinocchio)
3. F. Farshidian et al., "OCS2: An open source library for Optimal Control of Switched Systems." [GitHub](https://github.com/leggedrobotics/ocs2)
4. G. Frison and M. Diehl, "HPIPM: a high-performance quadratic programming framework for model predictive control," IFAC-PapersOnLine, 2020. [arXiv:2003.02547](https://arxiv.org/abs/2003.02547)
5. M. Diehl et al., "Real-time optimization and nonlinear model predictive control of processes governed by differential-algebraic equations," Journal of Process Control, 2002.
6. Coal (formerly HPP-FCL), collision detection and distance computation library. [GitHub](https://github.com/coal-library/coal)
7. C. Feller and C. Ebenbauer, "Relaxed logarithmic barrier function based model predictive control of linear systems," IEEE Transactions on Automatic Control, 2017.
8. A. De Luca, A. Albu-Schäffer, S. Haddadin and G. Hirzinger, "Collision detection and safe reaction with the DLR-III lightweight manipulator arm," IEEE/RSJ IROS, 2006.
9. S. Haddadin, A. De Luca and A. Albu-Schäffer, "Robot collisions: A survey on detection, isolation, and identification," IEEE Transactions on Robotics, 2017.
