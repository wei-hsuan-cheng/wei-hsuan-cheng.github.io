---
title: "Kendo Robot: Combining Robotics Technologies with Martial Art"
collection: projects
permalink: /project/2023-12-kendo-robot
# excerpt: "Short description of project item number 1<br/><img src='/images/500x300.png'>"
excerpt: "A supervisory teleoperation kendo robot system. The robot is able to track the opponent’s pose and wait for the operator’s command to attack. *Robotics competition winner as a team leader in the course project of [CSIE5074](https://nol.ntu.edu.tw/nol/coursesearch/print_table.php?course_id=922%20U1070&class=&dpt_code=9210&ser_no=62682&semester=112-1&lang=CH) Robotics, offered by [Prof. Li-Chen Fu](https://www.ntueeacl.com/25351235662594525480-advisor.html) @ NTU EE*. <a href='https://github.com/wei-hsuan-cheng/kendo_robot' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>kendo_robot</span></a>"
date: 2023-12-01
# slidesurl: 'http://academicpages.github.io/files/slides1.pdf'
# paperurl: '/files/pdfs/projects/kendo_robot.pdf'
---

# Project overview

We built a supervisory teleoperation kendo robot system. The robot is able to track the opponent’s pose and wait for the operator’s command to attack.

<iframe width="560" height="315" 
        src="https://www.youtube.com/embed/9ygvFLr1BNQ" 
        frameborder="0" 
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen>
</iframe>


The kendo robot system is implemented in both  ``ROS 1 Python`` and ``JavaScript`` and can be found in <a href='https://github.com/wei-hsuan-cheng/kendo_robot' target='_blank' style='text-decoration: none;'><i class='fab fa-github' style=''></i><span style='margin-left: 0.13cm'>kendo_robot</span></a>.
{: .notice}

To detect and track the human body, we utilised a deep-learning-based human pose estimation algorithm ([LOGO-CAP, CVPR 2022](https://github.com/cherubicXN/logocap)). By aligning the RGB and DEPTH images from the RealSense D435, we obtained the 3D coordinates of the human body.

An [interactive GUI] was created using `JavaScript` for visualisation and real-time implementation. With just one click on the GUI button, the operator can send an attack command to ROS (via a WebSocket), which controls the robot arm. The GUI is handcrafted based on `ganja.js`, a web-programmable platform developed by the geometric algebra community.

**Drag the mouse cursor to change viewpoints and modify the codes to change parameters through the [interactive GUI]!**
{: .notice}

<iframe src="https://enkimute.github.io/ganja.js/examples/coffeeshop.html#ZAxvNkQ7x" width="100%" height="600px" frameborder="0"></iframe>


Visualisation, inverse kinematics, and trajectory planning are all handled using **conformal geometric algebra (CGA)**, a powerful mathematical framework for representing geometry. CGA provides numerous geometric insights into the robot that are nearly impossible to achieve using traditional matrix methods.

- Team members
  - **Wei-Hsuan Cheng** (Team Leader): <a href="mailto:johnathancheng0125@gmail.com">johnathancheng0125@gmail.com</a> / <a href="mailto:r11631045@ntu.edu.tw">r11631045@ntu.edu.tw</a>
  - **Wen Perng**: <a href="mailto:b10901042@ntu.edu.tw">b10901042@ntu.edu.tw</a>
  - **Che-Jung Chuang**: <a href="mailto:r12021008@ntu.edu.tw">r12021008@ntu.edu.tw</a>
  - **Cheng-Yen Yu**: <a href="mailto:r12922135@ntu.edu.tw">r12922135@ntu.edu.tw</a>


# Resources

- [YouTube Demo Video](https://www.youtube.com/watch?v=9ygvFLr1BNQ)
- [Interactive GUI of Kendo Robot System](https://enkimute.github.io/ganja.js/examples/coffeeshop.html#ZAxvNkQ7x)
- [LOGO-CAP Human Pose Estimation Algorithm](https://github.com/cherubicXN/logocap)
- [The Geometric Algebra Community - biVector.net](https://bivector.net/)
- [ganja.js](https://github.com/enkimute/ganja.js?files=1)


# Project report in PDF

<embed src="/files/pdfs/projects/kendo_robot.pdf" type="application/pdf" width="100%" height="600px" />

[kendo_robot]: https://github.com/wei-hsuan-cheng/kendo_robot
[interactive GUI]: https://enkimute.github.io/ganja.js/examples/coffeeshop.html#ZAxvNkQ7x

