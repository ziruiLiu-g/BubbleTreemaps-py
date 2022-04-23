# BubbleTreemaps-py

This is an rewrite of Bubble Treemaps in Python and not the original code.

The original paper please review: http://graphics.uni-konstanz.de/publikationen/Goertler2018BubbleTreemapsUncertainty/index.html

The JavaScript implementation please review: https://github.com/grtlr/bubble-treemaps


## SmartyPants

/data: stores files that will be used in the project

Hierarcy.py: Used to generate the HierarcyRoot of the map. In the JavaScript Version, it is implemented by **d3.hierarchy**

tool_classes.py: Rewrite some useful Classes(Circle, Arc, Vec) which will be used in the project

bbtreemap.py: the implementation of BubbleTreeMap

main.py: The visualization of the project, include the GUI code


## Package

Some important package that will be used in the project

|                |Github                     |
|----------------|-------------------------------|
|Box2D|https://github.com/erincatto/box2d|
|Circlify|https://github.com/elmotec/circlify|


## Installation

Make sure you have all the required package installed.

Install **pyinstaller** in your computer.

Use the command below to install the .exe, make sure you execute the command under the project document.

     pyinstaller -F -w main.py -p bbtreemap.py -p Hierarcy.py -p tool_classes.py


## How to use
1. Once you got the .exe, open it and upload your data(.json)

![](https://github.com/ziruiLau/BubbleTreemaps-py/blob/master/pic/1650694419(1).jpg)

2. Plot the result 

![](https://github.com/ziruiLau/BubbleTreemaps-py/blob/master/pic/1650694563(1).jpg)

3. Now you can drag the parameter bars and have fun!!
