---
title: "Attitude and Angular Velocity Estimation of Surgical Robot Using Sensor Fusion with Optical Tracker, IMU, and Quaternion-Based Extended Kalman Filter"
collection: projects
permalink: /project/2023-05-quat-est
# excerpt: "Short description of project item number 1<br/><img src='/images/500x300.png'>"
excerpt: "Quaternion attitude and angular velocity estimation via NDI, IMU, and EKF/UKF. **GitHub repo: [kf_cpp](https://github.com/wei-hsuan-cheng/kf_cpp)**"
date: 2023-05-01
# slidesurl: ''
# paperurl: '/files/pdfs/projects/quat_est.pdf'
---

Project overview
======

For surgical robots that conduct minimally invasive surgeries, robust and precise perception of the robot end-effector is required for tracking and navigation of the surgical probes or needles. In this scenario, single sensor may not be sufficient due to its natural limitation that reduce the sensing robustness. 

This leads to the need for **sensor fusion**, which combines multiple sensory data and generates a better perception of the robot. One of the most common approaches for sensor fusion is the Kalman filter algorithm. 

In this project, a sensor fusion framework is used for estimating the attitude and angular velocity of robot end-effector in constant angular velocity motion. The multi-sensor system consists of an **optical tracker (NDI)** and an **inertial measurement unit (IMU)**, and a mathematical model for **extended Kalman filter (EKF)** is proposed. Experimental results are shown to verify the proposed model and framework.

The quaternion attitude and angular velocity estimation via **EKF**/**UKF** is implemented in ROS 2 C++ and can be found in **[kf_cpp]**.
{: .notice}

Simulate and visualise in ROS 2 RViz2
======
TBD.

Project report in PDF
======
<embed src="/files/pdfs/projects/quat_est.pdf" type="application/pdf" width="100%" height="600px" />



[kf_cpp]: https://github.com/wei-hsuan-cheng/kf_cpp

