import math
import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import bbtreemap
import json

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
        self.smoothness.setMaximum(200)
        self.smoothness.setValue(1)
        self.smoothness.setSingleStep(1)
        self.smoothness.setOrientation(QtCore.Qt.Horizontal)

        self.padding_label = QLabel()
        self.padding_label.setObjectName('padding')
        self.padding_label.setText('================= PADDING =================')
        self.padding_label.setAlignment(QtCore.Qt.AlignCenter)
        self.padding = QSlider()
        self.padding.setMinimum(1)
        self.padding.setMaximum(200)
        self.padding.setValue(1)
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

    def plot(self):
        contour = self.getTree()
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


        maxlimx = 0
        minlimx = 0
        maxlimy = 0
        minlimy = 0
        for c in self.b.hierarchyRoot.leaves():
            x, y, r = c.x, c.y, c.r
            maxlimx = max(maxlimx, x + r)
            maxlimy = max(maxlimy, y + r)
            minlimx = min(minlimx, x - r)
            minlimy = min(minlimy, y - r)
            color = c.color
            ax.add_patch(plt.Circle((x, y), r, linewidth=2, edgecolor='black', facecolor=color))

        ax.relim()
        ax.autoscale_view()
        # plt.xlim(minlimx, maxlimx)
        # plt.ylim(minlimy, maxlimy)
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
        return self.b.contours

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.resize(800, 1000)
    main.show()
    sys.exit(app.exec_())
