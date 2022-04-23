# importing various libraries
import math
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Arc
import bbtreemap
import json

# main window
# which inherits QDialog
class Window(QDialog):

    # constructor
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.b = None
        self.data = None

        self.figure = plt.figure(figsize=(5,16))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.smoothness_label = QLabel()
        self.smoothness_label.setObjectName('smoothness')
        self.smoothness_label.setText('================= SMOOTHNESS =================')
        self.smoothness_label.setAlignment(QtCore.Qt.AlignCenter)
        self.smoothness = QSlider()
        self.smoothness.setMinimum(1)
        self.smoothness.setMaximum(3000)
        self.smoothness.setValue(1)
        self.smoothness.setSingleStep(50)
        self.smoothness.setOrientation(QtCore.Qt.Horizontal)

        self.padding_label = QLabel()
        self.padding_label.setObjectName('padding')
        self.padding_label.setText('================= PADDING =================')
        self.padding_label.setAlignment(QtCore.Qt.AlignCenter)
        self.padding = QSlider()
        self.padding.setMinimum(1)
        self.padding.setMaximum(2000)
        self.padding.setValue(50)
        self.padding.setOrientation(QtCore.Qt.Horizontal)

        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        self.padding.sliderMoved.connect(self.plot)
        self.smoothness.sliderMoved.connect(self.plot)

        self.upload = QPushButton('upload')
        self.filepath = QTextEdit()
        self.upload.clicked.connect(lambda: self.filepath.setText(QtWidgets.QFileDialog.getOpenFileName(self, './')[0]))

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.smoothness_label)
        layout.addWidget(self.smoothness)
        layout.addWidget(self.padding_label)
        layout.addWidget(self.padding)
        layout.addWidget(self.button)
        layout.addWidget(self.upload)
        layout.addWidget(self.filepath)
        self.setLayout(layout)

    # action called by the push button
    def plot(self):
        contour = self.getTree()

        # clearing old figure
        self.figure.clear()

        ax = self.figure.subplots()


        for c in contour:
            x = c['x']
            y = c['y']
            startAng = (c['d'].startAngle / (2 * math.pi)) * 360
            endAng = (c['d'].endAngle / (2 * math.pi)) * 360
            r = c['d'].outerRadius * 2
            linewidth = c['strokeWidth']
            ax.add_patch(Arc((x, y), r, r, 270, theta1=startAng, theta2=endAng, linewidth=linewidth, color='black'))

        for c in self.b.hierarchyRoot.leaves():
            x, y, r = c.x, c.y, c.r
            color = c.color
            ax.add_patch(plt.Circle((x, y), r, linewidth=2, edgecolor='black', facecolor=color))

        ax.relim()
        ax.autoscale_view()
        # minlim = min(min(ax.get_xlim()), min(ax.get_ylim()))
        # maxlim = max(max(ax.get_xlim()), max(ax.get_ylim()))
        # plt.xlim(minlim, maxlim)
        # plt.ylim(minlim, maxlim)
        self.canvas.draw()

    def getTree(self):
        self.b = bbtreemap.BubbleTreeMap(json.loads(open(self.filepath.toPlainText()).read())) \
            .set_padding(self.padding.value()) \
            .set_curvature(self.smoothness.value()) \
            .set_width(800) \
            .set_height(800) \
            .set_colormap(
            ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9",
             "#bc80bd", "#ccebc5", "#ffed6f"])
        self.b.doLayout().getContour()
        # if self.b is not None:
        #     self.b.set_padding(self.padding.value()).set_curvature(self.smoothness.value())
        #     self.b.doLayout().getContour()
        # else:
        #     self.b = bbtreemap.BubbleTreeMap(json.loads(open(self.filepath.toPlainText()).read())) \
        #         .set_padding(self.padding.value()) \
        #         .set_curvature(self.smoothness.value()) \
        #         .set_width(800) \
        #         .set_height(800) \
        #         .set_colormap(
        #         ["#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9",
        #          "#bc80bd", "#ccebc5", "#ffed6f"])
        #     self.b.doLayout().getContour()
        return self.b.contours

# driver code
if __name__ == '__main__':
    # creating apyqt5 application
    app = QApplication(sys.argv)

    # creating a window object
    main = Window()
    main.resize(600, 800)
    # showing the window
    main.show()

    # loop
    sys.exit(app.exec_())
