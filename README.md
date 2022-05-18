# JutsuLock
  A Convenient and Secure Keyless Entry System using Unique Hand Signs  

Abstract: This paper introduces a novel home automation security mechanism as part of a smart nation initiative. The device employs hand-gestures to secure and unlock a hostel room door, combining the personal touch of a thumbprint with the portability of an access card.The idea was inspired from the Jutsu hand-signs used in the anime, Naruto. The product uses a Raspberry Pi camera to capture the hand-gesture, then processors the image on an Intel Movidius Stick, before transferring a bluetooth signal to an Arduino board. The Arduino Board then controls a motor secured using a custom-made motor mount, to lock or unlock the door. The Intel Movidius Stick is trained on a Caffe model on Ubuntu 16.04, based on a dataset created using the hand-gestures of our own team members. Experiments show that our design is able to recognise gestures with high accuracy.

Keywords: Component, Smart Nation, Security, Raspberry Pi, Movidius Stick, Jutsu, IoT, Deep Learning, Ubuntu, Smart Campus, Naruto, Home Automation. 
