---
permalink: /
title: "About Wei-Hsuan"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

<!-- Centered profile picture -->
<!-- <p align="center">
  <img 
    src="/images/profile/whcheng_profile.jpg" 
    alt="Wei-Hsuan Cheng" 
    width="200"
  />
</p> -->

<!-- **Looking for PhD position in robotics!!** -->

Hi, this is Wei-Hsuan Cheng (he/him). I am a robotics researcher (Associate Researcher) at **[Delta Robotics Innovation Center (DRIC)][DRIC]**, where I focus primarily on **model predictive control (MPC)**, together with other model-based control and estimation methods (e.g. force control, KF-family), across various robotic embodiments, including dual-arm systems, dexterous hands, mobile manipulators, and integrated combinations of these platforms.

## Model predictive control

I build MPC controllers that run in `ros2_control`, from robotic arms to humanoids and wheeled-legged robots:

<table align="center">
  <tr>
    <td align="center" width="25%">
      <a href="/project/2026-10-legged-robot-mpc"><img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/legged_robot_mpc_controller/h2_mpc_future_robot_visualization.gif?raw=true" style="width: 100%; height: auto;" alt="Unitree H2 walking with the MPC's future robot trajectory" /></a>
    </td>
    <td align="center" width="75%">
      <a href="/project/2026-06-robotic-arm-dynamics-mpc"><img src="https://github.com/wei-hsuan-cheng/gifs/blob/main/dynamics_mpc_controller/ur5_moving_obstacles.gif?raw=true" style="width: 100%; height: auto;" alt="UR5 inverse-dynamics MPC among moving obstacles" /></a>
    </td>
  </tr>
  <tr>
    <td align="center"><b><a href="/project/2026-10-legged-robot-mpc">Legged Robot MPC</a></b><br />Whole-body inverse-dynamics MPC for humanoids and wheeled bipeds</td>
    <td align="center"><b><a href="/project/2026-06-robotic-arm-dynamics-mpc">Robotic Arm Dynamics MPC</a></b><br />Inverse- and forward-dynamics MPC for robotic arms</td>
  </tr>
</table>

<style>
.mpc-obsession { margin: 1.6em 0 2.2em; }
.mpc-obsession__title { font-size: 1.05em; font-weight: 700; margin: 0 0 0.9em; letter-spacing: 0.01em; }
.mpc-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.9em; }
.mpc-card {
  position: relative; overflow: hidden; padding: 1.05em 1em 1.15em;
  border: 1px solid var(--global-border-color); border-top: 4px solid var(--accent); border-radius: 10px;
  background: linear-gradient(160deg, var(--tint) 0%, rgba(255, 255, 255, 0) 70%);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  animation: mpc-rise 0.6s ease both; animation-delay: var(--delay);
}
.mpc-card:hover { transform: translateY(-5px); box-shadow: 0 10px 22px var(--tint-strong); }
.mpc-card__icon {
  display: inline-flex; align-items: center; justify-content: center; width: 2.3em; height: 2.3em;
  border-radius: 50%; background: var(--accent); color: #fff; font-size: 0.95em; margin-bottom: 0.6em;
  transition: transform 0.4s ease;
}
.mpc-card:hover .mpc-card__icon { transform: rotate(-12deg) scale(1.12); }
.mpc-card__label { display: block; font-size: 0.72em; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.3em; }
.mpc-card__text { margin: 0; font-size: 0.9em; line-height: 1.45; }
.mpc-card--forecast { --accent: #2f7f93; --tint: rgba(47, 127, 147, 0.10); --tint-strong: rgba(47, 127, 147, 0.25); --delay: 0.05s; }
.mpc-card--steer    { --accent: #7a5cc4; --tint: rgba(122, 92, 196, 0.10); --tint-strong: rgba(122, 92, 196, 0.25); --delay: 0.15s; }
.mpc-card--balance  { --accent: #d9822b; --tint: rgba(217, 130, 43, 0.10); --tint-strong: rgba(217, 130, 43, 0.25); --delay: 0.25s; }
.mpc-unified {
  display: flex; align-items: center; justify-content: center; gap: 0.6em; margin-top: 0.9em; padding: 0.85em 1em;
  border-radius: 10px; color: #fff; font-weight: 700; font-size: 1.02em; letter-spacing: 0.02em;
  background: linear-gradient(90deg, #2f7f93, #7a5cc4, #d9822b, #7a5cc4, #2f7f93); background-size: 300% 100%;
  animation: mpc-rise 0.6s ease 0.4s both, mpc-flow 10s linear infinite;
}
@keyframes mpc-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes mpc-flow { from { background-position: 0% 50%; } to { background-position: 300% 50%; } }
@media (max-width: 640px) { .mpc-cards { grid-template-columns: 1fr; } }
@media (prefers-reduced-motion: reduce) {
  .mpc-card, .mpc-unified { animation: none; }
  .mpc-card, .mpc-card__icon { transition: none; }
}
</style>

<div class="mpc-obsession">
  <p class="mpc-obsession__title">What I am obsessed with in MPC</p>
  <div class="mpc-cards">
    <div class="mpc-card mpc-card--forecast">
      <span class="mpc-card__icon"><i class="fas fa-binoculars" aria-hidden="true"></i></span>
      <span class="mpc-card__label">Forecast</span>
      <p class="mpc-card__text">Its forecast to future possibilities over a horizon</p>
    </div>
    <div class="mpc-card mpc-card--steer">
      <span class="mpc-card__icon"><i class="fas fa-sliders" aria-hidden="true"></i></span>
      <span class="mpc-card__label">Steer</span>
      <p class="mpc-card__text">Its flexibility to steer different behaviors with costs</p>
    </div>
    <div class="mpc-card mpc-card--balance">
      <span class="mpc-card__icon"><i class="fas fa-scale-balanced" aria-hidden="true"></i></span>
      <span class="mpc-card__label">Balance</span>
      <p class="mpc-card__text">Its smoothness in handling multiple competing objectives and constraints</p>
    </div>
  </div>
  <div class="mpc-unified"><i class="fas fa-layer-group" aria-hidden="true"></i> All with a unified strategy</div>
</div>

## Background

Previously, I completed my Master's degree at [Robots and Medical Mechatronics Lab (RMML)][RMML], [Department of Biomechatronics Engineering][NTUBME], [National Taiwan University (NTU)][NTU], advised by *[Prof. Ping-Lang Yen]*.

- Master's thesis title: *“Application of Vision- and Force-Based Supervisory Teleoperation for Robotic Dexterous Manipulation Tasks in Industrial Surveillance”*

My research interests lie in ``robotics``, particularly model-based control and estimation for contact-rich/compliant manipulation and legged/wheeled-legged locomotion. I have experience in diverse domains in robotics, including but not limited to
- ``Model predictive control (MPC)`` (kinematics and dynamics MPC, whole-body inverse-dynamics MPC)
- ``Whole-body control (WBC)``
- ``Kalman filtering`` (KF, EKF, UKF, InEKF, etc.)
- ``Teleoperation`` robotic system through ``wireless communication``
- ``Compliance control`` (force, admittance, and impedance control)
- Robotic ``dexterous`` manipulations (contact-rich, physical interactions, compliant motions, etc.)
- Robotic arm ``vision-based control`` (visual servoing, 6D pose estimation and tracking)
- Application of ``geometric algebra`` in robotics

Check out my [projects] and [resume] here. Reach out if you’re intereted in what I’m doing!


[DRIC]: https://www.deltaww.com/en-US/company/innovation
[RMML]: http://rmml.bime.ntu.edu.tw/nturmmle.html
[NTUBME]: https://www.bime.ntu.edu.tw/English/Default.html
[NTU]: https://www.ntu.edu.tw/english/
[Prof. Ping-Lang Yen]: http://rmml.bime.ntu.edu.tw/profe.html
[projects]: /projects/
[resume]: /cv/
