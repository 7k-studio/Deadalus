# Deadalus v0.3.3-beta
---

## Bugfixing

### Wing Designer

#### Input value
*Input value* function which was suppoesd to allow data from user input rather than arrows has been repaired. The input area now accepts and saves the values.

#### Scaling of a segment
There was an issue with scaling of a segment in Wing Designer. The airfoil was supposed to only scale down in a 2D plane (XY) but it also scaled in Z direction. Now when scaling down or up the Z position is preserved.