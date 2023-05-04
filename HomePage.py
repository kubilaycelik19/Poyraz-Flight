import sys
import cv2
import os
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from HomePage_python import Ui_MainWindow
from flightHistory import historyPage
import time
from folium.plugins import MarkerCluster
from encodings import search_function
from PyQt5 import QtWebEngineWidgets
from folium.plugins import Draw ,MousePosition
import folium, io, sys, json
from folium import plugins
from pymavlink import mavutil
from threading import Thread


#udpin:127.0.0.1:14550
#connection_string="COM14"
vehicle=mavutil.mavlink_connection("COM14", baud=115200, wait_ready=True)
Gpsmsg = vehicle.recv_match()
homeLoc = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)

#############################################################################! ALTTİTUDE START
class AnalogGauge_alt(QLabel):
    valueChanged = pyqtSignal(int) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timerAlt = QTimer(self)
        self.timerAlt.timeout.connect(self.updateAlt)
        self.timerAlt.start(1000) # 1 saniyede bir tekrarla
        
        
    def updateAlt(self):
        altMsg = vehicle.recv_match(type='VFR_HUD', blocking=True)
        gaugeAltitude = int(altMsg.alt)
        self.valueAlt = round(gaugeAltitude)
        #print(self.value)

        
        self.use_timer_event = True

        
        # DEFAULT NEEDLE COLOR
        
        self.setNeedleColor(0, 0, 0, 255)

        
        # DEFAULT NEEDLE WHEN RELEASED
        
        self.NeedleColorReleased = self.NeedleColor

        
        # DEFAULT NEEDLE COLOR ON DRAG
        
        # self.NeedleColorDrag = QColor(255, 0, 00, 255)
        self.setNeedleColorOnDrag(255, 0, 00, 255)

        
        # DEFAULT SCALE TEXT COLOR
        
        self.setScaleValueColor(0, 0, 0, 255)

        
        # DEFAULT VALUE COLOR
        
        self.setDisplayValueColor(0, 0, 0, 255)

        
        # DEFAULT CENTER POINTER COLOR
        
        # self.CenterPointColor = QColor(50, 50, 50, 255)
        self.set_CenterPointColor(0, 0, 0, 255)

        
        # DEFAULT NEEDLE COUNT
        
        self.value_needle_count = 1

        self.value_needle = QObject

        
        # DEFAULT MINIMUM AND MAXIMUM VALUE
        
        self.minValueAlt = 0
        self.maxValueAlt = 500
        
        # DEFAULT START VALUE
        
        #self.value = self.minValue

        
        # DEFAULT OFFSET
        
        self.value_offset = 0

        self.valueNeedleSnapzone = 0.05
        self.last_value = 0

        # self.value2 = 0
        # self.value2Color = QColor(0, 0, 0, 255)

        
        # DEFAULT RADIUS
        
        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        
        # DEFAULT SCALE VALUE
        
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.angle_offset = 0

        self.setScalaCount(10)
        self.scala_subdiv_count = 5

        self.pen = QPen(QColor(0, 0, 0))

        
        # LOAD CUSTOM FONT
        
        QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(
            __file__), 'fonts/Orbitron/Orbitron-VariableFont_wght.ttf'))

        
        # DEFAULT POLYGON COLOR
        
        self.scale_polygon_colors = []

        
        # BIG SCALE COLOR
        
        self.bigScaleMarker = Qt.black

        
        # FINE SCALE COLOR
        
        self.fineScaleColor = Qt.black

        
        # DEFAULT SCALE TEXT STATUS
        
        self.setEnableScaleText(True)
        self.scale_fontname = "Orbitron"
        self.initial_scale_fontsize = 14
        self.scale_fontsize = self.initial_scale_fontsize

        
        # DEFAULT VALUE TEXT STATUS
        
        self.enable_value_text = True
        self.value_fontname = "Orbitron"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.5

        
        # ENABLE BAR GRAPH BY DEFAULT
        
        self.setEnableBarGraph(True)
        
        # FILL POLYGON COLOR BY DEFAULT
        
        self.setEnableScalePolygon(True)
        
        # ENABLE CENTER POINTER BY DEFAULT
        
        self.enable_CenterPoint = True
        
        # ENABLE FINE SCALE BY DEFAULT
        
        self.enable_fine_scaled_marker = True
        
        # ENABLE BIG SCALE BY DEFAULT
        
        self.enable_big_scaled_marker = True

        
        # NEEDLE SCALE FACTOR/LENGTH
        
        self.needle_scale_factor = 0.8
        
        # ENABLE NEEDLE POLYGON BY DEFAULT
        
        self.enable_Needle_Polygon = True

        
        # ENABLE NEEDLE MOUSE TRACKING BY DEFAULT
        
        self.setMouseTracking(True)

        
        # SET GAUGE UNITS
        
        self.units = "m"

        # QTimer sorgt für neu Darstellung alle X ms
        # evtl performance hier verbessern mit self.update() und self.use_timer_event = False
        # todo: self.update als default ohne ueberpruefung, ob self.use_timer_event gesetzt ist oder nicht
        # Timer startet alle 10ms das event paintEvent
        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        
        # SET DEFAULT THEME
        
        self.setGaugeTheme(0)

        
        # RESIZE GAUGE
        
        self.rescale_method()

    # SET SCALE FONT FAMILY
    
    def setScaleFontFamily(self, font):
        self.scale_fontname = str(font)

    
    # SET VALUE FONT FAMILY
    
    def setValueFontFamily(self, font):
        self.value_fontname = str(font)

    
    # SET BIG SCALE COLOR
    
    def setBigScaleColor(self, color):
        self.bigScaleMarker = QColor(color)

    
    # SET FINE SCALE COLOR
    
    def setFineScaleColor(self, color):
        self.fineScaleColor = QColor(color)

    
    # GAUGE THEMES
    
    def setGaugeTheme(self, Theme=1):
        if Theme == 0 or Theme == None:
            self.set_scale_polygon_colors([[.00, Qt.red],
                                           [.1, Qt.yellow],
                                           [.15, Qt.green],
                                           [1, Qt.transparent]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 1:
            self.set_scale_polygon_colors([[.75, Qt.red],
                                           [.5, Qt.yellow],
                                           [.25, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 2:
            self.set_scale_polygon_colors([[.25, Qt.red],
                                           [.5, Qt.yellow],
                                           [.75, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        elif Theme == 3:
            self.set_scale_polygon_colors([[.00, Qt.white]])

            self.needle_center_bg = [
                                    [0, Qt.white],
            ]

            self.outer_circle_bg = [
                [0, Qt.white],
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 4:
            self.set_scale_polygon_colors([[1, Qt.black]])

            self.needle_center_bg = [
                                    [0, Qt.black],
            ]

            self.outer_circle_bg = [
                [0, Qt.black],
            ]

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 5:
            self.set_scale_polygon_colors([[1, QColor("#029CDE")]])

            self.needle_center_bg = [
                                    [0, QColor("#029CDE")],
            ]

            self.outer_circle_bg = [
                [0, QColor("#029CDE")],
            ]

        elif Theme == 6:
            self.set_scale_polygon_colors([[.75, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.25, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 7:
            self.set_scale_polygon_colors([[.25, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.75, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black


    
    # # SET SCALE POLYGON COLOR
    
    def setScalePolygonColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.set_scale_polygon_colors([[.25, QColor(str(colors['color1']))],
                                                   [.5, QColor(
                                                       str(colors['color2']))],
                                                   [.75, QColor(str(colors['color3']))]])

                else:

                    self.set_scale_polygon_colors([[.5, QColor(str(colors['color1']))],
                                                   [1, QColor(str(colors['color2']))]])

            else:

                self.set_scale_polygon_colors(
                    [[1, QColor(str(colors['color1']))]])

        else:
            print("color1 is not defined")

    
    # SET NEEDLE CENTER COLOR
    
    def setNeedleCenterColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color3']))],
                                            [0.322581, QColor(
                                                str(colors['color1']))],
                                            [0.571429, QColor(
                                                str(colors['color2']))],
                                            [1, QColor(str(colors['color3']))]
                    ]

                else:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color2']))],
                                            [1, QColor(str(colors['color1']))]
                    ]

            else:

                self.needle_center_bg = [
                                        [1, QColor(str(colors['color1']))]
                ]
        else:
            print("color1 is not defined")

    
    # SET OUTER CIRCLE COLOR
    
    def setOuterCircleColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.outer_circle_bg = [
                        [0.0645161, QColor(str(colors['color3']))],
                        [0.37788, QColor(
                            str(colors['color1']))],
                        [1, QColor(str(colors['color2']))]
                    ]

                else:

                    self.outer_circle_bg = [
                        [0, QColor(str(colors['color2']))],
                        [1, QColor(str(colors['color2']))]
                    ]

            else:

                self.outer_circle_bg = [
                    [1, QColor(str(colors['color1']))]
                ]

        else:
            print("color1 is not defined")

    
    # RESCALE
    

    def rescale_method(self):
        # print("slotMethod")
        
        # SET WIDTH AND HEIGHT
        
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()

        
        # SET NEEDLE SIZE
        
        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, int(- self.widget_diameter / 2 * self.needle_scale_factor)),
            QPoint(0, int(- self.widget_diameter /
                   2 * self.needle_scale_factor - 6)),
            QPoint(2, int(- self.widget_diameter / 2 * self.needle_scale_factor))
        ])])

        
        # SET FONT SIZE
        
        self.scale_fontsize = int(
            self.initial_scale_fontsize * self.widget_diameter / 400)
        self.value_fontsize = int(
            self.initial_value_fontsize * self.widget_diameter / 400)

    def change_value_needle_style(self, design):
        # prepared for multiple needle instrument
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()

    
    # UPDATE VALUE
    
    # def updateValue(self, value, mouse_controlled=False):

    #     if value <= self.minValue:
    #         self.value = self.minValue
    #     elif value >= self.maxValue:
    #         self.value = self.maxValue
    #     else:
    #         self.value = value
    #     # self.paintEvent("")
    #     self.valueChanged.emit(int(value))
    #     # print(self.value)

    #     # ohne timer: aktiviere self.update()
    #     if not self.use_timer_event:
    #         self.update()

    def updateAngleOffset(self, offset):
        self.angle_offset = offset
        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value
        # print("horizontal: " + str(self.center_horizontal_value))

    def center_vertical(self, value):
        self.center_vertical_value = value
        # print("vertical: " + str(self.center_vertical_value))

    
    # SET NEEDLE COLOR
    
    def setNeedleColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()
    
    # SET NEEDLE COLOR ON DRAG
    

    def setNeedleColorOnDrag(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColorDrag = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE VALUE COLOR
    
    def setScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.ScaleValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET DISPLAY VALUE COLOR
    
    def setDisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.DisplayValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET CENTER POINTER COLOR
    
    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE NEEDLE POLYGON
    
    def setEnableNeedlePolygon(self, enable=True):
        self.enable_Needle_Polygon = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE SCALE TEXT
    
    def setEnableScaleText(self, enable=True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE BAR GRAPH
    
    def setEnableBarGraph(self, enable=True):
        self.enableBarGraph = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE VALUE TEXT
    
    def setEnableValueText(self, enable=True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE CENTER POINTER
    
    def setEnableCenterPoint(self, enable=True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE FILLED POLYGON
    
    def setEnableScalePolygon(self, enable=True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE BIG SCALE
    
    def setEnableBigScaleGrid(self, enable=True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE FINE SCALE
    

    def setEnableFineScaleGrid(self, enable=True):
        self.enable_fine_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE SCALA MAIN CONT
    
    def setScalaCount(self, count):
        if count < 1:
            count = 1
        self.scalaCount = count

        if not self.use_timer_event:
            self.update()

    
    # SET MINIMUM VALUE
    
    def setMinValue(self, min):
        if self.valueAlt < min:
            self.valueAlt = min
        if min >= self.maxValueAlt:
            self.minValueAlt = self.maxValue - 1
        else:
            self.minValue = min

        if not self.use_timer_event:
            self.update()

    
    # SET MAXIMUM VALUE
    
    # def setMaxValue(self, max):
    #     if self.valueAlt > max:
    #         self.valueAlt = max
    #     if max <= self.minValue:
    #         self.maxValue = self.minValue + 1
    #     else:
    #         self.maxValue = max

    #     if not self.use_timer_event:
    #         self.update()

    
    # SET SCALE ANGLE
    
    def setScaleStartAngle(self, value):
        # Value range in DEG: 0 - 360
        self.scale_angle_start_value = value
        # print("startFill: " + str(self.scale_angle_start_value))

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE SIZE
    
    def setTotalScaleAngleSize(self, value):
        self.scale_angle_size = value
        # print("stopFill: " + str(self.scale_angle_size))

        if not self.use_timer_event:
            self.update()

    
    # SET GAUGE COLOR OUTER RADIUS
    
    def setGaugeColorOuterRadiusFactor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000
        # print(self.gauge_color_outer_radius_factor)

        if not self.use_timer_event:
            self.update()

    
    # SET GAUGE COLOR INNER RADIUS
    
    def setGaugeColorInnerRadiusFactor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000
        # print(self.gauge_color_inner_radius_factor)

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE POLYGON COLOR
    
    def set_scale_polygon_colors(self, color_array):
        # print(type(color_array))
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        if not self.use_timer_event:
            self.update()

    
    # GET MAXIMUM VALUE
    
    def get_value_max(self):
        return self.maxValue

    
    # SCALE PAINTER
    

    
    # CREATE PIE
    
    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght, bar_graph=True):
        polygon_pie = QPolygonF()
        # start = self.scale_angle_start_value
        # start = 0
        # lenght = self.scale_angle_size
        # lenght = 180
        # inner_raduis = self.width()/4
        # print(start)
        n = 360     # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n   # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enableBarGraph and bar_graph:
            # float_value = ((lenght / (self.maxValue - self.minValue)) * (self.value - self.minValue))
            lenght = int(
                round((lenght / (self.maxValueAlt - self.minValueAlt)) * (self.valueAlt - self.minValue)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        # add the points of polygon
        for i in range(lenght + 1):
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        # add the points of polygon
        for i in range(lenght + 1):
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        # close outer line
        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            # Koordinatenursprung in die Mitte der Flaeche legen
            painter_filled_polygon.translate(
                self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) *
                self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2))
                 * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(
                int(self.widget_diameter / 2 - 1), int(self.widget_diameter - 1)))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                    self.angle_offset - 1)

            # todo definition scale color as array here
            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            # grad.setColorAt(.00, Qt.red)
            # grad.setColorAt(.1, Qt.yellow)
            # grad.setColorAt(.15, Qt.green)
            # grad.setColorAt(1, Qt.transparent)
            # self.brush = QBrush(QColor(255, 0, 255, 255))
            # grad.setStyle(Qt.Dense6Pattern)
            # painter_filled_polygon.setBrush(self.brush)
            painter_filled_polygon.setBrush(grad)

            painter_filled_polygon.drawPolygon(colored_scale_polygon)
            # return painter_filled_polygon

    def draw_icon_image(self):
        pass

    
    # BIG SCALE MARKERS
    
    def draw_big_scaled_marker(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        # my_painter.setPen(Qt.NoPen)
        self.pen = QPen(self.bigScaleMarker)
        self.pen.setWidth(2)
        # # if outline_pen_with > 0:
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int((self.widget_diameter / 2) -
                                (self.widget_diameter / 20))
        # print(stepszize)
        for i in range(self.scalaCount + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        font = QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter / 2 * text_radius_factor

        scale_per_div = int((self.maxValueAlt - self.minValueAlt) / self.scalaCount)

        angle_distance = (float(self.scale_angle_size) /
                          float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            # text = str(int((self.maxValue - self.minValue) / self.scalaCount * i))
            text = str(int(self.minValueAlt + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname,
                            self.scale_fontsize, QFont.Bold))
            angle = angle_distance * i + \
                float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            # print(w, h, x, y, text)

            painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                             int(h), Qt.AlignCenter, text)
        # painter.restore()

    
    # FINE SCALE MARKERS
    
    def create_fine_scaled_marker(self):
        #  Description_dict = 0
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(self.fineScaleColor)
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) /
                      float(self.scalaCount * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int(
            (self.widget_diameter / 2) - (self.widget_diameter / 40))
        for i in range((self.scalaCount * self.scala_subdiv_count) + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    
    # VALUE TEXT
    
    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        # xShadow = 3.0
        # yShadow = 3.0
        font = QFont(self.value_fontname, self.value_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        # angle_distance = (float(self.scale_angle_size) / float(self.scalaCount))
        # for i in range(self.scalaCount + 1):
        text = str(int(self.valueAlt))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname,
                        self.value_fontsize, QFont.Bold))

        # Mitte zwischen Skalenstart und Skalenende:
        # Skalenende = Skalenanfang - 360 + Skalenlaenge
        # Skalenmitte = (Skalenende - Skalenanfang) / 2 + Skalenanfang
        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    
    # UNITS TEXT
    

    def create_units_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold))

        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size + 180)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    
    # CENTER POINTER
    

    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        # painter.setPen(Qt.NoPen)

        # painter.setBrush(self.CenterPointColor)
        # diameter = diameter # self.widget_diameter/6
        # painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

        # create_polygon_pie(self, outer_radius, inner_raduis, start, lenght)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 8) - (self.pen.width() / 2)),
            0,
            self.scale_angle_start_value, 360, False)

        # 150.0 0.0 131 360

        grad = QConicalGradient(QPointF(0, 0), 0)

        # todo definition scale color as array here
        for eachcolor in self.needle_center_bg:
            grad.setColorAt(eachcolor[0], eachcolor[1])
        # grad.setColorAt(.00, Qt.red)
        # grad.setColorAt(.1, Qt.yellow)
        # grad.setColorAt(.15, Qt.green)
        # grad.setColorAt(1, Qt.transparent)
        painter.setBrush(grad)
        # self.brush = QBrush(QColor(255, 0, 255, 255))
        # painter_filled_polygon.setBrush(self.brush)

        painter.drawPolygon(colored_scale_polygon)
        # return painter_filled_polygon

    
    # CREATE OUTER COVER
    
    def draw_outer_circle(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 2) - (self.pen.width())),
            (self.widget_diameter / 6),
            self.scale_angle_start_value / 10, 360, False)

        radialGradient = QRadialGradient(QPointF(0, 0), self.width())

        for eachcolor in self.outer_circle_bg:
            radialGradient.setColorAt(eachcolor[0], eachcolor[1])

        painter.setBrush(radialGradient)

        painter.drawPolygon(colored_scale_polygon)

    
    # NEEDLE POINTER
    

    def draw_needle(self):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.valueAlt - self.value_offset - self.minValueAlt) * self.scale_angle_size /
                        (self.maxValueAlt - self.minValueAlt)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    
    # EVENTS
    

    
    # ON WINDOW RESIZE
    
    def resizeEvent(self, event):
        self.rescale_method()
    def paintEvent(self, event):

        self.draw_outer_circle()
        self.draw_icon_image()
        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_marker()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()
            self.create_units_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(
                diameter=(self.widget_diameter / 6))


########################################################! ALTTİTUDE END

###############################################! GROUNDSPEED START
class AnalogGauge_ground(QWidget):
    valueChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
        
        self.timerGround = QTimer(self)
        self.timerGround.timeout.connect(self.updateGround)
        self.timerGround.start(1000) # 1 saniyede bir tekrarla
        # DEFAULT TIMER VALUE
        
    def updateGround(self):

        altMsg = vehicle.recv_match(type='VFR_HUD', blocking=True)
        gaugeGround = altMsg.groundspeed
        self.valueGround = round(gaugeGround,2)
        #print(self.value)

        self.use_timer_event = True
        self.setNeedleColor(0, 0, 0, 255)
        self.NeedleColorReleased = self.NeedleColor
        self.setNeedleColorOnDrag(255, 0, 00, 255)
        self.setScaleValueColor(0, 0, 0, 255)
        self.setDisplayValueColor(0, 0, 0, 255)
        self.set_CenterPointColor(0, 0, 0, 255)
        self.value_needle_count = 1
        self.value_needle = QObject
        self.minValueGround = 0
        self.maxValueGround = 50 
        self.value_offset = 0
        

        self.valueNeedleSnapzone = 0.05
        self.last_value = 0
        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.angle_offset = 0

        self.setScalaCount(10)
        self.scala_subdiv_count = 5

        self.pen = QPen(QColor(0, 0, 0))

        QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(
            __file__), 'fonts/Orbitron/Orbitron-VariableFont_wght.ttf'))

        self.scale_polygon_colors = []

        self.bigScaleMarker = Qt.black

        self.fineScaleColor = Qt.black

        self.setEnableScaleText(True)
        self.scale_fontname = "Orbitron"
        self.initial_scale_fontsize = 14
        self.scale_fontsize = self.initial_scale_fontsize
        self.enable_value_text = True
        self.value_fontname = "Orbitron"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.5
        self.setEnableBarGraph(True)
        self.setEnableScalePolygon(True)
        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True
        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        self.setMouseTracking(False)
        self.units = "m/s"

        # QTimer sorgt für neu Darstellung alle X ms
        # evtl performance hier verbessern mit self.update() und self.use_timer_event = False
        # todo: self.update als default ohne ueberpruefung, ob self.use_timer_event gesetzt ist oder nicht
        # Timer startet alle 10ms das event paintEvent
        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        self.setGaugeTheme(0)

        self.rescale_method()

    def setScaleFontFamily(self, font):
        self.scale_fontname = str(font)

    def setValueFontFamily(self, font):
        self.value_fontname = str(font)

    def setBigScaleColor(self, color):
        self.bigScaleMarker = QColor(color)

    def setFineScaleColor(self, color):
        self.fineScaleColor = QColor(color)

    def setGaugeTheme(self, Theme=1):
        if Theme == 0 or Theme == None:
            self.set_scale_polygon_colors([[.00, Qt.red],
                                           [.1, Qt.yellow],
                                           [.15, Qt.green],
                                           [1, Qt.transparent]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 1:
            self.set_scale_polygon_colors([[.75, Qt.red],
                                           [.5, Qt.yellow],
                                           [.25, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 2:
            self.set_scale_polygon_colors([[.25, Qt.red],
                                           [.5, Qt.yellow],
                                           [.75, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        elif Theme == 3:
            self.set_scale_polygon_colors([[.00, Qt.white]])

            self.needle_center_bg = [
                                    [0, Qt.white],
            ]

            self.outer_circle_bg = [
                [0, Qt.white],
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 4:
            self.set_scale_polygon_colors([[1, Qt.black]])

            self.needle_center_bg = [
                                    [0, Qt.black],
            ]

            self.outer_circle_bg = [
                [0, Qt.black],
            ]

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 5:
            self.set_scale_polygon_colors([[1, QColor("#029CDE")]])

            self.needle_center_bg = [
                                    [0, QColor("#029CDE")],
            ]

            self.outer_circle_bg = [
                [0, QColor("#029CDE")],
            ]

        elif Theme == 6:
            self.set_scale_polygon_colors([[.75, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.25, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 7:
            self.set_scale_polygon_colors([[.25, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.75, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

    def rescale_method(self):
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()
        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, int(- self.widget_diameter / 2 * self.needle_scale_factor)),
            QPoint(0, int(- self.widget_diameter /
                   2 * self.needle_scale_factor - 6)),
            QPoint(2, int(- self.widget_diameter / 2 * self.needle_scale_factor))
        ])])

        self.scale_fontsize = int(
            self.initial_scale_fontsize * self.widget_diameter / 400)
        self.value_fontsize = int(
            self.initial_value_fontsize * self.widget_diameter / 400)

    def change_value_needle_style(self, design):
        # prepared for multiple needle instrument
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()

    # def updateValue(self, value, mouse_controlled=False):
    #     # if not mouse_controlled:
    #     #     self.value = value
    #     #
    #     # if mouse_controlled:
    #     #     self.valueChanged.emit(int(value))

    #     if value <= self.minValue:
    #         self.value = self.minValue
    #     elif value >= self.maxValue:
    #         self.value = self.maxValue
    #     else:
    #         self.value = value
    #     # self.paintEvent("")
    #     self.valueChanged.emit(int(value))
    #     # print(self.value)

    #     # ohne timer: aktiviere self.update()
    #     if not self.use_timer_event:
    #         self.update()

    def updateAngleOffset(self, offset):
        self.angle_offset = offset
        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value
        # print("horizontal: " + str(self.center_horizontal_value))

    def center_vertical(self, value):
        self.center_vertical_value = value
        # print("vertical: " + str(self.center_vertical_value))

    def setNeedleColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()

    def setNeedleColorOnDrag(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColorDrag = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.ScaleValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setDisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.DisplayValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setEnableNeedlePolygon(self, enable=True):
        self.enable_Needle_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScaleText(self, enable=True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBarGraph(self, enable=True):
        self.enableBarGraph = enable

        if not self.use_timer_event:
            self.update()

    def setEnableValueText(self, enable=True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableCenterPoint(self, enable=True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScalePolygon(self, enable=True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBigScaleGrid(self, enable=True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def setEnableFineScaleGrid(self, enable=True):
        self.enable_fine_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def setScalaCount(self, count):
        if count < 1:
            count = 1
        self.scalaCount = count

        if not self.use_timer_event:
            self.update()

    def setMinValue(self, min):
        if self.valueGround < min:
            self.valueGround = min
        if min >= self.maxValueGround:
            self.minValueGround = self.maxValueGround - 1
        else:
            self.minValueGround = min

        if not self.use_timer_event:
            self.update()

    def setMaxValue(self, max):
        if self.valueGround > max:
            self.valueGround = max
        if max <= self.minValueGround:
            self.maxValueGround = self.minValueGround + 1
        else:
            self.maxValueGround = max

        if not self.use_timer_event:
            self.update()

    def setScaleStartAngle(self, value):
        # Value range in DEG: 0 - 360
        self.scale_angle_start_value = value
        # print("startFill: " + str(self.scale_angle_start_value))

        if not self.use_timer_event:
            self.update()

    def setTotalScaleAngleSize(self, value):
        self.scale_angle_size = value
        # print("stopFill: " + str(self.scale_angle_size))

        if not self.use_timer_event:
            self.update()

    def setGaugeColorOuterRadiusFactor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000
        # print(self.gauge_color_outer_radius_factor)

        if not self.use_timer_event:
            self.update()

    def setGaugeColorInnerRadiusFactor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000
        # print(self.gauge_color_inner_radius_factor)

        if not self.use_timer_event:
            self.update()

    def set_scale_polygon_colors(self, color_array):
        # print(type(color_array))
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        if not self.use_timer_event:
            self.update()

    
    # GET MAXIMUM VALUE
    
    def get_value_max(self):
        return self.maxValue

    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght, bar_graph=True):
        polygon_pie = QPolygonF()
        # start = self.scale_angle_start_value
        # start = 0
        # lenght = self.scale_angle_size
        # lenght = 180
        # inner_raduis = self.width()/4
        # print(start)
        n = 360     # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n   # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enableBarGraph and bar_graph:
            # float_value = ((lenght / (self.maxValue - self.minValue)) * (self.value - self.minValue))
            lenght = int(
                round((lenght / (self.maxValueGround - self.minValueGround)) * (self.valueGround - self.minValueGround)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        # add the points of polygon
        for i in range(lenght + 1):
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        # add the points of polygon
        for i in range(lenght + 1):
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        # close outer line
        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            # Koordinatenursprung in die Mitte der Flaeche legen
            painter_filled_polygon.translate(
                self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) *
                self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2))
                 * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(
                int(self.widget_diameter / 2 - 1), int(self.widget_diameter - 1)))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                    self.angle_offset - 1)

            # todo definition scale color as array here
            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            # grad.setColorAt(.00, Qt.red)
            # grad.setColorAt(.1, Qt.yellow)
            # grad.setColorAt(.15, Qt.green)
            # grad.setColorAt(1, Qt.transparent)
            # self.brush = QBrush(QColor(255, 0, 255, 255))
            # grad.setStyle(Qt.Dense6Pattern)
            # painter_filled_polygon.setBrush(self.brush)
            painter_filled_polygon.setBrush(grad)

            painter_filled_polygon.drawPolygon(colored_scale_polygon)
            # return painter_filled_polygon

    def draw_icon_image(self):
        pass

    def draw_big_scaled_marker(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        # my_painter.setPen(Qt.NoPen)
        self.pen = QPen(self.bigScaleMarker)
        self.pen.setWidth(2)
        # # if outline_pen_with > 0:
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int((self.widget_diameter / 2) -
                                (self.widget_diameter / 20))
        # print(stepszize)
        for i in range(self.scalaCount + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        font = QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter / 2 * text_radius_factor

        scale_per_div = int((self.maxValueGround - self.minValueGround) / self.scalaCount)

        angle_distance = (float(self.scale_angle_size) /
                          float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            # text = str(int((self.maxValue - self.minValue) / self.scalaCount * i))
            text = str(int(self.minValueGround + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname,
                            self.scale_fontsize, QFont.Bold))
            angle = angle_distance * i + \
                float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            # print(w, h, x, y, text)

            painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                             int(h), Qt.AlignCenter, text)
        # painter.restore()

    def create_fine_scaled_marker(self):
        #  Description_dict = 0
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(self.fineScaleColor)
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) /
                      float(self.scalaCount * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int(
            (self.widget_diameter / 2) - (self.widget_diameter / 40))
        for i in range((self.scalaCount * self.scala_subdiv_count) + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, self.value_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor
        text = str(int(self.valueGround))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname,
                        self.value_fontsize, QFont.Bold))
        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    def create_units_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold))

        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size + 180)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)


    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 8) - (self.pen.width() / 2)),
            0,
            self.scale_angle_start_value, 360, False)

        grad = QConicalGradient(QPointF(0, 0), 0)

        # todo definition scale color as array here
        for eachcolor in self.needle_center_bg:
            grad.setColorAt(eachcolor[0], eachcolor[1])
        painter.setBrush(grad)

        painter.drawPolygon(colored_scale_polygon)
    def draw_outer_circle(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 2) - (self.pen.width())),
            (self.widget_diameter / 6),
            self.scale_angle_start_value / 10, 360, False)

        radialGradient = QRadialGradient(QPointF(0, 0), self.width())

        for eachcolor in self.outer_circle_bg:
            radialGradient.setColorAt(eachcolor[0], eachcolor[1])

        painter.setBrush(radialGradient)

        painter.drawPolygon(colored_scale_polygon)

    
    # NEEDLE POINTER
    

    def draw_needle(self):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.valueGround - self.value_offset - self.minValueGround) * self.scale_angle_size /
                        (self.maxValueGround - self.minValueGround)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    
    # EVENTS
    

    
    # ON WINDOW RESIZE
    
    def resizeEvent(self, event):
        # self.resized.emit()
        # return super(self.parent, self).resizeEvent(event)
        # print("resized")
        # print(self.width())
        self.rescale_method()
        # self.emit(QtCore.SIGNAL("resize()"))
        # print("resizeEvent")

    
    # ON PAINT EVENT
    
    def paintEvent(self, event):
        # Main Drawing Event:
        # Will be executed on every change
        # vgl http://doc.qt.io/qt-4.8/qt-demos-affine-xform-cpp.html
        # print("event", event)

        self.draw_outer_circle()
        self.draw_icon_image()
        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_marker()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()
            self.create_units_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(
                diameter=(self.widget_diameter / 6))

    
    # MOUSE EVENTS
    

    # def setMouseTracking(self, flag):
    #     def recursive_set(parent):
    #         for child in parent.findChildren(QObject):
    #             try:
    #                 child.setMouseTracking(flag)
    #             except:
    #                 pass
    #             recursive_set(child)

    #     QWidget.setMouseTracking(self, flag)
    #     recursive_set(self)



#!####################################################### GROUND END

###############################################! AİRSPEED START
class AnalogGauge_airSpeed(QWidget):
    valueChanged = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(100, 100)
        
        self.timerAirSpeed = QTimer(self)
        self.timerAirSpeed.timeout.connect(self.updateairSpeed)
        self.timerAirSpeed.start(1000) # 1 saniyede bir tekrarla
        
    def updateairSpeed(self):
        groundAir = vehicle.recv_match(type='VFR_HUD', blocking=True)
        gaugeAir = groundAir.airspeed
        self.valueAir = gaugeAir
        
        self.use_timer_event = True
        self.setNeedleColor(0, 0, 0, 255)
        self.NeedleColorReleased = self.NeedleColor
        self.setNeedleColorOnDrag(255, 0, 00, 255)
        self.setScaleValueColor(0, 0, 0, 255)
        self.setDisplayValueColor(0, 0, 0, 255)
        self.set_CenterPointColor(0, 0, 0, 255)
        self.value_needle_count = 1
        self.value_needle = QObject
        self.minValueAir = 0
        self.maxValueAir = 50
        
                
        self.value_offset = 0

        self.valueNeedleSnapzone = 0.05
        self.last_value = 0
        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.angle_offset = 0

        self.setScalaCount(10)
        self.scala_subdiv_count = 5

        self.pen = QPen(QColor(0, 0, 0))

        QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(
            __file__), 'fonts/Orbitron/Orbitron-VariableFont_wght.ttf'))

        self.scale_polygon_colors = []

        self.bigScaleMarker = Qt.black

        self.fineScaleColor = Qt.black

        self.setEnableScaleText(True)
        self.scale_fontname = "Orbitron"
        self.initial_scale_fontsize = 14
        self.scale_fontsize = self.initial_scale_fontsize
        self.enable_value_text = True
        self.value_fontname = "Orbitron"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.5
        self.setEnableBarGraph(True)
        self.setEnableScalePolygon(True)
        self.enable_CenterPoint = True
        self.enable_fine_scaled_marker = True
        self.enable_big_scaled_marker = True
        self.needle_scale_factor = 0.8
        self.enable_Needle_Polygon = True

        self.setMouseTracking(False)
        self.units = "m/s"

        # QTimer sorgt für neu Darstellung alle X ms
        # evtl performance hier verbessern mit self.update() und self.use_timer_event = False
        # todo: self.update als default ohne ueberpruefung, ob self.use_timer_event gesetzt ist oder nicht
        # Timer startet alle 10ms das event paintEvent
        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        self.setGaugeTheme(0)

        self.rescale_method()

    def setScaleFontFamily(self, font):
        self.scale_fontname = str(font)

    def setValueFontFamily(self, font):
        self.value_fontname = str(font)

    def setBigScaleColor(self, color):
        self.bigScaleMarker = QColor(color)

    def setFineScaleColor(self, color):
        self.fineScaleColor = QColor(color)

    def setGaugeTheme(self, Theme=1):
        if Theme == 0 or Theme == None:
            self.set_scale_polygon_colors([[.00, Qt.red],
                                           [.1, Qt.yellow],
                                           [.15, Qt.green],
                                           [1, Qt.transparent]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 1:
            self.set_scale_polygon_colors([[.75, Qt.red],
                                           [.5, Qt.yellow],
                                           [.25, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 2:
            self.set_scale_polygon_colors([[.25, Qt.red],
                                           [.5, Qt.yellow],
                                           [.75, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        elif Theme == 3:
            self.set_scale_polygon_colors([[.00, Qt.white]])

            self.needle_center_bg = [
                                    [0, Qt.white],
            ]

            self.outer_circle_bg = [
                [0, Qt.white],
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 4:
            self.set_scale_polygon_colors([[1, Qt.black]])

            self.needle_center_bg = [
                                    [0, Qt.black],
            ]

            self.outer_circle_bg = [
                [0, Qt.black],
            ]

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 5:
            self.set_scale_polygon_colors([[1, QColor("#029CDE")]])

            self.needle_center_bg = [
                                    [0, QColor("#029CDE")],
            ]

            self.outer_circle_bg = [
                [0, QColor("#029CDE")],
            ]

        elif Theme == 6:
            self.set_scale_polygon_colors([[.75, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.25, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 7:
            self.set_scale_polygon_colors([[.25, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.75, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black


    def setNeedleCenterColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color3']))],
                                            [0.322581, QColor(
                                                str(colors['color1']))],
                                            [0.571429, QColor(
                                                str(colors['color2']))],
                                            [1, QColor(str(colors['color3']))]
                    ]

                else:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color2']))],
                                            [1, QColor(str(colors['color1']))]
                    ]

            else:

                self.needle_center_bg = [
                                        [1, QColor(str(colors['color1']))]
                ]
        else:
            print("color1 is not defined")

    def setOuterCircleColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.outer_circle_bg = [
                        [0.0645161, QColor(str(colors['color3']))],
                        [0.37788, QColor(
                            str(colors['color1']))],
                        [1, QColor(str(colors['color2']))]
                    ]

                else:

                    self.outer_circle_bg = [
                        [0, QColor(str(colors['color2']))],
                        [1, QColor(str(colors['color2']))]
                    ]

            else:

                self.outer_circle_bg = [
                    [1, QColor(str(colors['color1']))]
                ]

        else:
            print("color1 is not defined")

    def rescale_method(self):
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()
        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, int(- self.widget_diameter / 2 * self.needle_scale_factor)),
            QPoint(0, int(- self.widget_diameter /
                   2 * self.needle_scale_factor - 6)),
            QPoint(2, int(- self.widget_diameter / 2 * self.needle_scale_factor))
        ])])

        self.scale_fontsize = int(
            self.initial_scale_fontsize * self.widget_diameter / 400)
        self.value_fontsize = int(
            self.initial_value_fontsize * self.widget_diameter / 400)

    def change_value_needle_style(self, design):
        # prepared for multiple needle instrument
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()


    def updateAngleOffset(self, offset):
        self.angle_offset = offset
        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value
        # print("horizontal: " + str(self.center_horizontal_value))

    def center_vertical(self, value):
        self.center_vertical_value = value
        # print("vertical: " + str(self.center_vertical_value))

    def setNeedleColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()

    def setNeedleColorOnDrag(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.NeedleColorDrag = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setScaleValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.ScaleValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setDisplayValueColor(self, R=50, G=50, B=50, Transparency=255):
        # Red: R = 0 - 255
        # Green: G = 0 - 255
        # Blue: B = 0 - 255
        # Transparency = 0 - 255
        self.DisplayValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    def setEnableNeedlePolygon(self, enable=True):
        self.enable_Needle_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScaleText(self, enable=True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBarGraph(self, enable=True):
        self.enableBarGraph = enable

        if not self.use_timer_event:
            self.update()

    def setEnableValueText(self, enable=True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    def setEnableCenterPoint(self, enable=True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    def setEnableScalePolygon(self, enable=True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    def setEnableBigScaleGrid(self, enable=True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def setEnableFineScaleGrid(self, enable=True):
        self.enable_fine_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    def setScalaCount(self, count):
        if count < 1:
            count = 1
        self.scalaCount = count

        if not self.use_timer_event:
            self.update()

    def setMinValue(self, min):
        if self.valueAir < min:
            self.valueAir = min
        if min >= self.maxValueAir:
            self.minValueAir = self.maxValueAir - 1
        else:
            self.minValueAir = min

        if not self.use_timer_event:
            self.update()

    def setMaxValue(self, max):
        if self.valueAir > max:
            self.valueAir = max
        if max <= self.minValueAir:
            self.maxValueAir = self.minValueAir + 1
        else:
            self.maxValueAir = max

        if not self.use_timer_event:
            self.update()

    def setScaleStartAngle(self, value):
        # Value range in DEG: 0 - 360
        self.scale_angle_start_value = value
        # print("startFill: " + str(self.scale_angle_start_value))

        if not self.use_timer_event:
            self.update()

    def setTotalScaleAngleSize(self, value):
        self.scale_angle_size = value
        # print("stopFill: " + str(self.scale_angle_size))

        if not self.use_timer_event:
            self.update()

    def setGaugeColorOuterRadiusFactor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000
        # print(self.gauge_color_outer_radius_factor)

        if not self.use_timer_event:
            self.update()

    def setGaugeColorInnerRadiusFactor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000
        # print(self.gauge_color_inner_radius_factor)

        if not self.use_timer_event:
            self.update()

    def set_scale_polygon_colors(self, color_array):
        # print(type(color_array))
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        if not self.use_timer_event:
            self.update()

    
    # GET MAXIMUM VALUE
    
    def get_value_max(self):
        return self.maxValue

    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght, bar_graph=True):
        polygon_pie = QPolygonF()
        n = 360     # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n   # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enableBarGraph and bar_graph:
            # float_value = ((lenght / (self.maxValue - self.minValue)) * (self.value - self.minValue))
            lenght = int(
                round((lenght / (self.maxValueAir - self.minValueAir)) * (self.valueAir - self.minValueAir)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        # add the points of polygon
        for i in range(lenght + 1):
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        # add the points of polygon
        for i in range(lenght + 1):
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        # close outer line
        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            # Koordinatenursprung in die Mitte der Flaeche legen
            painter_filled_polygon.translate(
                self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) *
                self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2))
                 * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(
                int(self.widget_diameter / 2 - 1), int(self.widget_diameter - 1)))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                    self.angle_offset - 1)

            # todo definition scale color as array here
            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            painter_filled_polygon.setBrush(grad)

            painter_filled_polygon.drawPolygon(colored_scale_polygon)
            # return painter_filled_polygon

    def draw_icon_image(self):
        pass

    def draw_big_scaled_marker(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        # my_painter.setPen(Qt.NoPen)
        self.pen = QPen(self.bigScaleMarker)
        self.pen.setWidth(2)
        # # if outline_pen_with > 0:
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int((self.widget_diameter / 2) -
                                (self.widget_diameter / 20))
        # print(stepszize)
        for i in range(self.scalaCount + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        font = QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter / 2 * text_radius_factor

        scale_per_div = int((self.maxValueAir - self.minValueAir) / self.scalaCount)

        angle_distance = (float(self.scale_angle_size) /
                          float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            # text = str(int((self.maxValue - self.minValue) / self.scalaCount * i))
            text = str(int(self.minValueAir + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname,
                            self.scale_fontsize, QFont.Bold))
            angle = angle_distance * i + \
                float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            # print(w, h, x, y, text)

            painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                             int(h), Qt.AlignCenter, text)
        # painter.restore()

    def create_fine_scaled_marker(self):
        #  Description_dict = 0
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(self.fineScaleColor)
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) /
                      float(self.scalaCount * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int(
            (self.widget_diameter / 2) - (self.widget_diameter / 40))
        for i in range((self.scalaCount * self.scala_subdiv_count) + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, self.value_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor
        text = str(int(self.valueAir))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname,
                        self.value_fontsize, QFont.Bold))
        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    def create_units_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold))

        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size + 180)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)


    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 8) - (self.pen.width() / 2)),
            0,
            self.scale_angle_start_value, 360, False)

        grad = QConicalGradient(QPointF(0, 0), 0)

        # todo definition scale color as array here
        for eachcolor in self.needle_center_bg:
            grad.setColorAt(eachcolor[0], eachcolor[1])
        painter.setBrush(grad)

        painter.drawPolygon(colored_scale_polygon)
    def draw_outer_circle(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 2) - (self.pen.width())),
            (self.widget_diameter / 6),
            self.scale_angle_start_value / 10, 360, False)

        radialGradient = QRadialGradient(QPointF(0, 0), self.width())

        for eachcolor in self.outer_circle_bg:
            radialGradient.setColorAt(eachcolor[0], eachcolor[1])

        painter.setBrush(radialGradient)

        painter.drawPolygon(colored_scale_polygon)

    
    # NEEDLE POINTER
    

    def draw_needle(self):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.valueAir - self.value_offset - self.minValueAir) * self.scale_angle_size /
                        (self.maxValueAir - self.minValueAir)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    
    # EVENTS
    

    
    # ON WINDOW RESIZE
    
    def resizeEvent(self, event):
        self.rescale_method()
    def paintEvent(self, event):

        self.draw_outer_circle()
        self.draw_icon_image()
        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_marker()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()
            self.create_units_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(
                diameter=(self.widget_diameter / 6))



#!####################################################### AİRSPEED END

#!####################################################### VELOCİTY START

class AnalogGauge_velocity(QWidget):
    valueChanged = pyqtSignal(int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timerAlt = QTimer(self)
        self.timerAlt.timeout.connect(self.updateVelocity)
        self.timerAlt.start(1000) # 1 saniyede bir tekrarla
        
    def updateVelocity(self):
        msg = vehicle.recv_match(type='RAW_IMU', blocking=True)
        compass_x = msg.xmag
        self.valueVelo = compass_x
        #print(self.value)

        
        self.use_timer_event = True

        
        # DEFAULT NEEDLE COLOR
        
        self.setNeedleColor(0, 0, 0, 255)

        
        # DEFAULT NEEDLE WHEN RELEASED
        
        self.NeedleColorReleased = self.NeedleColor

        
        # DEFAULT NEEDLE COLOR ON DRAG
        
        # self.NeedleColorDrag = QColor(255, 0, 00, 255)
        self.setNeedleColorOnDrag(255, 0, 00, 255)

        
        # DEFAULT SCALE TEXT COLOR
        
        self.setScaleValueColor(0, 0, 0, 255)

        
        # DEFAULT VALUE COLOR
        
        self.setDisplayValueColor(0, 0, 0, 255)

        
        # DEFAULT CENTER POINTER COLOR
        
        # self.CenterPointColor = QColor(50, 50, 50, 255)
        self.set_CenterPointColor(0, 0, 0, 255)

        
        # DEFAULT NEEDLE COUNT
        
        self.value_needle_count = 1

        self.value_needle = QObject

        
        # DEFAULT MINIMUM AND MAXIMUM VALUE
        
        self.minValueVelo = 0
        self.maxValueVelo = 200
        
        # DEFAULT START VALUE
        
        #self.value = self.minValue

        
        # DEFAULT OFFSET
        
        self.value_offset = 0

        self.valueNeedleSnapzone = 0.05
        self.last_value = 0

        # self.value2 = 0
        # self.value2Color = QColor(0, 0, 0, 255)

        
        # DEFAULT RADIUS
        
        self.gauge_color_outer_radius_factor = 1
        self.gauge_color_inner_radius_factor = 0.9

        self.center_horizontal_value = 0
        self.center_vertical_value = 0

        
        # DEFAULT SCALE VALUE
        
        self.scale_angle_start_value = 135
        self.scale_angle_size = 270

        self.angle_offset = 0

        self.setScalaCount(10)
        self.scala_subdiv_count = 5

        self.pen = QPen(QColor(0, 0, 0))

        
        # LOAD CUSTOM FONT
        
        QFontDatabase.addApplicationFont(os.path.join(os.path.dirname(
            __file__), 'fonts/Orbitron/Orbitron-VariableFont_wght.ttf'))

        
        # DEFAULT POLYGON COLOR
        
        self.scale_polygon_colors = []

        
        # BIG SCALE COLOR
        
        self.bigScaleMarker = Qt.black

        
        # FINE SCALE COLOR
        
        self.fineScaleColor = Qt.black

        
        # DEFAULT SCALE TEXT STATUS
        
        self.setEnableScaleText(True)
        self.scale_fontname = "Orbitron"
        self.initial_scale_fontsize = 14
        self.scale_fontsize = self.initial_scale_fontsize

        
        # DEFAULT VALUE TEXT STATUS
        
        self.enable_value_text = True
        self.value_fontname = "Orbitron"
        self.initial_value_fontsize = 40
        self.value_fontsize = self.initial_value_fontsize
        self.text_radius_factor = 0.5

        
        # ENABLE BAR GRAPH BY DEFAULT
        
        self.setEnableBarGraph(True)
        
        # FILL POLYGON COLOR BY DEFAULT
        
        self.setEnableScalePolygon(True)
        
        # ENABLE CENTER POINTER BY DEFAULT
        
        self.enable_CenterPoint = True
        
        # ENABLE FINE SCALE BY DEFAULT
        
        self.enable_fine_scaled_marker = True
        
        # ENABLE BIG SCALE BY DEFAULT
        
        self.enable_big_scaled_marker = True

        
        # NEEDLE SCALE FACTOR/LENGTH
        
        self.needle_scale_factor = 0.8
        
        # ENABLE NEEDLE POLYGON BY DEFAULT
        
        self.enable_Needle_Polygon = True

        
        # ENABLE NEEDLE MOUSE TRACKING BY DEFAULT
        
        self.setMouseTracking(True)

        
        # SET GAUGE UNITS
        
        self.units = "m"
        if self.use_timer_event:
            timer = QTimer(self)
            timer.timeout.connect(self.update)
            timer.start(10)
        else:
            self.update()

        
        # SET DEFAULT THEME
        
        self.setGaugeTheme(0)

        
        # RESIZE GAUGE
        
        self.rescale_method()

    # SET SCALE FONT FAMILY
    
    def setScaleFontFamily(self, font):
        self.scale_fontname = str(font)

    
    # SET VALUE FONT FAMILY
    
    def setValueFontFamily(self, font):
        self.value_fontname = str(font)

    
    # SET BIG SCALE COLOR
    
    def setBigScaleColor(self, color):
        self.bigScaleMarker = QColor(color)

    
    # SET FINE SCALE COLOR
    
    def setFineScaleColor(self, color):
        self.fineScaleColor = QColor(color)

    
    # GAUGE THEMES
    
    def setGaugeTheme(self, Theme=1):
        if Theme == 0 or Theme == None:
            self.set_scale_polygon_colors([[.00, Qt.red],
                                           [.1, Qt.yellow],
                                           [.15, Qt.green],
                                           [1, Qt.transparent]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 1:
            self.set_scale_polygon_colors([[.75, Qt.red],
                                           [.5, Qt.yellow],
                                           [.25, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        if Theme == 2:
            self.set_scale_polygon_colors([[.25, Qt.red],
                                           [.5, Qt.yellow],
                                           [.75, Qt.green]])

            self.needle_center_bg = [
                                    [0, QColor(35, 40, 3, 255)],
                                    [0.16, QColor(30, 36, 45, 255)],
                                    [0.225, QColor(36, 42, 54, 255)],
                                    [0.423963, QColor(19, 23, 29, 255)],
                                    [0.580645, QColor(45, 53, 68, 255)],
                                    [0.792627, QColor(59, 70, 88, 255)],
                                    [0.935, QColor(30, 35, 45, 255)],
                                    [1, QColor(35, 40, 3, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(30, 35, 45, 255)],
                [0.37788, QColor(57, 67, 86, 255)],
                [1, QColor(30, 36, 45, 255)]
            ]

        elif Theme == 3:
            self.set_scale_polygon_colors([[.00, Qt.white]])

            self.needle_center_bg = [
                                    [0, Qt.white],
            ]

            self.outer_circle_bg = [
                [0, Qt.white],
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 4:
            self.set_scale_polygon_colors([[1, Qt.black]])

            self.needle_center_bg = [
                                    [0, Qt.black],
            ]

            self.outer_circle_bg = [
                [0, Qt.black],
            ]

            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white

        elif Theme == 5:
            self.set_scale_polygon_colors([[1, QColor("#029CDE")]])

            self.needle_center_bg = [
                                    [0, QColor("#029CDE")],
            ]

            self.outer_circle_bg = [
                [0, QColor("#029CDE")],
            ]

        elif Theme == 6:
            self.set_scale_polygon_colors([[.75, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.25, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black

        elif Theme == 7:
            self.set_scale_polygon_colors([[.25, QColor("#01ADEF")],
                                           [.5, QColor("#0086BF")],
                                           [.75, QColor("#005275")]])

            self.needle_center_bg = [
                                    [0, QColor(0, 46, 61, 255)],
                                    [0.322581, QColor(1, 173, 239, 255)],
                                    [0.571429, QColor(0, 73, 99, 255)],
                                    [1, QColor(0, 46, 61, 255)]
            ]

            self.outer_circle_bg = [
                [0.0645161, QColor(0, 85, 116, 255)],
                [0.37788, QColor(1, 173, 239, 255)],
                [1, QColor(0, 69, 94, 255)]
            ]

            self.bigScaleMarker = Qt.black
            self.fineScaleColor = Qt.black
            self.bigScaleMarker = Qt.white
            self.fineScaleColor = Qt.white


    
    # # SET SCALE POLYGON COLOR
    
    def setScalePolygonColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.set_scale_polygon_colors([[.25, QColor(str(colors['color1']))],
                                                   [.5, QColor(
                                                       str(colors['color2']))],
                                                   [.75, QColor(str(colors['color3']))]])

                else:

                    self.set_scale_polygon_colors([[.5, QColor(str(colors['color1']))],
                                                   [1, QColor(str(colors['color2']))]])

            else:

                self.set_scale_polygon_colors(
                    [[1, QColor(str(colors['color1']))]])

        else:
            print("color1 is not defined")

    
    # SET NEEDLE CENTER COLOR
    
    def setNeedleCenterColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color3']))],
                                            [0.322581, QColor(
                                                str(colors['color1']))],
                                            [0.571429, QColor(
                                                str(colors['color2']))],
                                            [1, QColor(str(colors['color3']))]
                    ]

                else:

                    self.needle_center_bg = [
                                            [0, QColor(str(colors['color2']))],
                                            [1, QColor(str(colors['color1']))]
                    ]

            else:

                self.needle_center_bg = [
                                        [1, QColor(str(colors['color1']))]
                ]
        else:
            print("color1 is not defined")

    
    # SET OUTER CIRCLE COLOR
    
    def setOuterCircleColor(self, **colors):
        if "color1" in colors and len(str(colors['color1'])) > 0:
            if "color2" in colors and len(str(colors['color2'])) > 0:
                if "color3" in colors and len(str(colors['color3'])) > 0:

                    self.outer_circle_bg = [
                        [0.0645161, QColor(str(colors['color3']))],
                        [0.37788, QColor(
                            str(colors['color1']))],
                        [1, QColor(str(colors['color2']))]
                    ]

                else:

                    self.outer_circle_bg = [
                        [0, QColor(str(colors['color2']))],
                        [1, QColor(str(colors['color2']))]
                    ]

            else:

                self.outer_circle_bg = [
                    [1, QColor(str(colors['color1']))]
                ]

        else:
            print("color1 is not defined")

    
    # RESCALE
    

    def rescale_method(self):
        # print("slotMethod")
        
        # SET WIDTH AND HEIGHT
        
        if self.width() <= self.height():
            self.widget_diameter = self.width()
        else:
            self.widget_diameter = self.height()

        
        # SET NEEDLE SIZE
        
        self.change_value_needle_style([QPolygon([
            QPoint(4, 30),
            QPoint(-4, 30),
            QPoint(-2, int(- self.widget_diameter / 2 * self.needle_scale_factor)),
            QPoint(0, int(- self.widget_diameter /
                   2 * self.needle_scale_factor - 6)),
            QPoint(2, int(- self.widget_diameter / 2 * self.needle_scale_factor))
        ])])

        
        # SET FONT SIZE
        
        self.scale_fontsize = int(
            self.initial_scale_fontsize * self.widget_diameter / 400)
        self.value_fontsize = int(
            self.initial_value_fontsize * self.widget_diameter / 400)

    def change_value_needle_style(self, design):
        # prepared for multiple needle instrument
        self.value_needle = []
        for i in design:
            self.value_needle.append(i)
        if not self.use_timer_event:
            self.update()
            
    def updateAngleOffset(self, offset):
        self.angle_offset = offset
        if not self.use_timer_event:
            self.update()

    def center_horizontal(self, value):
        self.center_horizontal_value = value
        # print("horizontal: " + str(self.center_horizontal_value))

    def center_vertical(self, value):
        self.center_vertical_value = value
        # print("vertical: " + str(self.center_vertical_value))

    
    # SET NEEDLE COLOR
    
    def setNeedleColor(self, R=50, G=50, B=50, Transparency=255):
        self.NeedleColor = QColor(R, G, B, Transparency)
        self.NeedleColorReleased = self.NeedleColor

        if not self.use_timer_event:
            self.update()
    
    # SET NEEDLE COLOR ON DRAG
    

    def setNeedleColorOnDrag(self, R=50, G=50, B=50, Transparency=255):

        self.NeedleColorDrag = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE VALUE COLOR
    
    def setScaleValueColor(self, R=50, G=50, B=50, Transparency=255):

        self.ScaleValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET DISPLAY VALUE COLOR
    
    def setDisplayValueColor(self, R=50, G=50, B=50, Transparency=255):

        self.DisplayValueColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SET CENTER POINTER COLOR
    
    def set_CenterPointColor(self, R=50, G=50, B=50, Transparency=255):
        self.CenterPointColor = QColor(R, G, B, Transparency)

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE NEEDLE POLYGON
    
    def setEnableNeedlePolygon(self, enable=True):
        self.enable_Needle_Polygon = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE SCALE TEXT
    
    def setEnableScaleText(self, enable=True):
        self.enable_scale_text = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE BAR GRAPH
    
    def setEnableBarGraph(self, enable=True):
        self.enableBarGraph = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE VALUE TEXT
    
    def setEnableValueText(self, enable=True):
        self.enable_value_text = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE CENTER POINTER
    
    def setEnableCenterPoint(self, enable=True):
        self.enable_CenterPoint = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE FILLED POLYGON
    
    def setEnableScalePolygon(self, enable=True):
        self.enable_filled_Polygon = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE BIG SCALE
    
    def setEnableBigScaleGrid(self, enable=True):
        self.enable_big_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE FINE SCALE
    

    def setEnableFineScaleGrid(self, enable=True):
        self.enable_fine_scaled_marker = enable

        if not self.use_timer_event:
            self.update()

    
    # SHOW HIDE SCALA MAIN CONT
    
    def setScalaCount(self, count):
        if count < 1:
            count = 1
        self.scalaCount = count

        if not self.use_timer_event:
            self.update()

    
    # SET MINIMUM VALUE
    
    def setMinValue(self, min):
        if self.valueVelo < min:
            self.valueVelo = min
        if min >= self.maxValueVelo:
            self.minValueVelo = self.maxValueVelo - 1
        else:
            self.minValueVelo = min

        if not self.use_timer_event:
            self.update()

    
    # SET MAXIMUM VALUE
    
    def setMaxValue(self, max):
        if self.valueVelo > max:
            self.valueVelo = max
        if max <= self.minValueVelo:
            self.maxValueVelo = self.minValueVelo + 1
        else:
            self.maxValueVelo = max

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE ANGLE
    
    def setScaleStartAngle(self, value):
        # Value range in DEG: 0 - 360
        self.scale_angle_start_value = value
        # print("startFill: " + str(self.scale_angle_start_value))

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE SIZE
    
    def setTotalScaleAngleSize(self, value):
        self.scale_angle_size = value
        # print("stopFill: " + str(self.scale_angle_size))

        if not self.use_timer_event:
            self.update()

    
    # SET GAUGE COLOR OUTER RADIUS
    
    def setGaugeColorOuterRadiusFactor(self, value):
        self.gauge_color_outer_radius_factor = float(value) / 1000
        # print(self.gauge_color_outer_radius_factor)

        if not self.use_timer_event:
            self.update()

    
    # SET GAUGE COLOR INNER RADIUS
    
    def setGaugeColorInnerRadiusFactor(self, value):
        self.gauge_color_inner_radius_factor = float(value) / 1000
        # print(self.gauge_color_inner_radius_factor)

        if not self.use_timer_event:
            self.update()

    
    # SET SCALE POLYGON COLOR
    
    def set_scale_polygon_colors(self, color_array):
        # print(type(color_array))
        if 'list' in str(type(color_array)):
            self.scale_polygon_colors = color_array
        elif color_array == None:
            self.scale_polygon_colors = [[.0, Qt.transparent]]
        else:
            self.scale_polygon_colors = [[.0, Qt.transparent]]

        if not self.use_timer_event:
            self.update()

    
    # GET MAXIMUM VALUE
    
    def get_value_max(self):
        return self.maxValue

    
    # SCALE PAINTER
    

    
    # CREATE PIE
    
    def create_polygon_pie(self, outer_radius, inner_raduis, start, lenght, bar_graph=True):
        polygon_pie = QPolygonF()
        # start = self.scale_angle_start_value
        # start = 0
        # lenght = self.scale_angle_size
        # lenght = 180
        # inner_raduis = self.width()/4
        # print(start)
        n = 360     # angle steps size for full circle
        # changing n value will causes drawing issues
        w = 360 / n   # angle per step
        # create outer circle line from "start"-angle to "start + lenght"-angle
        x = 0
        y = 0

        # todo enable/disable bar graf here
        if not self.enableBarGraph and bar_graph:
            # float_value = ((lenght / (self.maxValue - self.minValue)) * (self.value - self.minValue))
            lenght = int(
                round((lenght / (self.maxValueVelo - self.minValueVelo)) * (self.valueVelo - self.minValueVelo)))
            # print("f: %s, l: %s" %(float_value, lenght))
            pass

        # mymax = 0

        # add the points of polygon
        for i in range(lenght + 1):
            t = w * i + start - self.angle_offset
            x = outer_radius * math.cos(math.radians(t))
            y = outer_radius * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))
        # create inner circle line from "start + lenght"-angle to "start"-angle
        # add the points of polygon
        for i in range(lenght + 1):
            # print("2 " + str(i))
            t = w * (lenght - i) + start - self.angle_offset
            x = inner_raduis * math.cos(math.radians(t))
            y = inner_raduis * math.sin(math.radians(t))
            polygon_pie.append(QPointF(x, y))

        # close outer line
        polygon_pie.append(QPointF(x, y))
        return polygon_pie

    def draw_filled_polygon(self, outline_pen_with=0):
        if not self.scale_polygon_colors == None:
            painter_filled_polygon = QPainter(self)
            painter_filled_polygon.setRenderHint(QPainter.Antialiasing)
            # Koordinatenursprung in die Mitte der Flaeche legen
            painter_filled_polygon.translate(
                self.width() / 2, self.height() / 2)

            painter_filled_polygon.setPen(Qt.NoPen)

            self.pen.setWidth(outline_pen_with)
            if outline_pen_with > 0:
                painter_filled_polygon.setPen(self.pen)

            colored_scale_polygon = self.create_polygon_pie(
                ((self.widget_diameter / 2) - (self.pen.width() / 2)) *
                self.gauge_color_outer_radius_factor,
                (((self.widget_diameter / 2) - (self.pen.width() / 2))
                 * self.gauge_color_inner_radius_factor),
                self.scale_angle_start_value, self.scale_angle_size)

            gauge_rect = QRect(QPoint(0, 0), QSize(
                int(self.widget_diameter / 2 - 1), int(self.widget_diameter - 1)))
            grad = QConicalGradient(QPointF(0, 0), - self.scale_angle_size - self.scale_angle_start_value +
                                    self.angle_offset - 1)

            # todo definition scale color as array here
            for eachcolor in self.scale_polygon_colors:
                grad.setColorAt(eachcolor[0], eachcolor[1])
            # grad.setColorAt(.00, Qt.red)
            # grad.setColorAt(.1, Qt.yellow)
            # grad.setColorAt(.15, Qt.green)
            # grad.setColorAt(1, Qt.transparent)
            # self.brush = QBrush(QColor(255, 0, 255, 255))
            # grad.setStyle(Qt.Dense6Pattern)
            # painter_filled_polygon.setBrush(self.brush)
            painter_filled_polygon.setBrush(grad)

            painter_filled_polygon.drawPolygon(colored_scale_polygon)
            # return painter_filled_polygon

    def draw_icon_image(self):
        pass

    
    # BIG SCALE MARKERS
    
    def draw_big_scaled_marker(self):
        my_painter = QPainter(self)
        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        # my_painter.setPen(Qt.NoPen)
        self.pen = QPen(self.bigScaleMarker)
        self.pen.setWidth(2)
        # # if outline_pen_with > 0:
        my_painter.setPen(self.pen)

        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) / float(self.scalaCount))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int((self.widget_diameter / 2) -
                                (self.widget_diameter / 20))
        # print(stepszize)
        for i in range(self.scalaCount + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    def create_scale_marker_values_text(self):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        font = QFont(self.scale_fontname, self.scale_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.ScaleValueColor)
        painter.setPen(pen_shadow)

        text_radius_factor = 0.8
        text_radius = self.widget_diameter / 2 * text_radius_factor

        scale_per_div = int((self.maxValueVelo - self.minValueVelo) / self.scalaCount)

        angle_distance = (float(self.scale_angle_size) /
                          float(self.scalaCount))
        for i in range(self.scalaCount + 1):
            # text = str(int((self.maxValue - self.minValue) / self.scalaCount * i))
            text = str(int(self.minValueVelo + scale_per_div * i))
            w = fm.width(text) + 1
            h = fm.height()
            painter.setFont(QFont(self.scale_fontname,
                            self.scale_fontsize, QFont.Bold))
            angle = angle_distance * i + \
                float(self.scale_angle_start_value - self.angle_offset)
            x = text_radius * math.cos(math.radians(angle))
            y = text_radius * math.sin(math.radians(angle))
            # print(w, h, x, y, text)

            painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                             int(h), Qt.AlignCenter, text)
        # painter.restore()

    
    # FINE SCALE MARKERS
    
    def create_fine_scaled_marker(self):
        #  Description_dict = 0
        my_painter = QPainter(self)

        my_painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        my_painter.translate(self.width() / 2, self.height() / 2)

        my_painter.setPen(self.fineScaleColor)
        my_painter.rotate(self.scale_angle_start_value - self.angle_offset)
        steps_size = (float(self.scale_angle_size) /
                      float(self.scalaCount * self.scala_subdiv_count))
        scale_line_outer_start = self.widget_diameter // 2
        scale_line_lenght = int(
            (self.widget_diameter / 2) - (self.widget_diameter / 40))
        for i in range((self.scalaCount * self.scala_subdiv_count) + 1):
            my_painter.drawLine(scale_line_lenght, 0,
                                scale_line_outer_start, 0)
            my_painter.rotate(steps_size)

    
    # VALUE TEXT
    
    def create_values_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        # painter.save()
        # xShadow = 3.0
        # yShadow = 3.0
        font = QFont(self.value_fontname, self.value_fontsize, QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        # angle_distance = (float(self.scale_angle_size) / float(self.scalaCount))
        # for i in range(self.scalaCount + 1):
        text = str(int(self.valueVelo))
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname,
                        self.value_fontsize, QFont.Bold))

        # Mitte zwischen Skalenstart und Skalenende:
        # Skalenende = Skalenanfang - 360 + Skalenlaenge
        # Skalenmitte = (Skalenende - Skalenanfang) / 2 + Skalenanfang
        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size - 360)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    
    # UNITS TEXT
    

    def create_units_text(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        font = QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold)
        fm = QFontMetrics(font)

        pen_shadow = QPen()

        pen_shadow.setBrush(self.DisplayValueColor)
        painter.setPen(pen_shadow)

        text_radius = self.widget_diameter / 2 * self.text_radius_factor

        text = str(self.units)
        w = fm.width(text) + 1
        h = fm.height()
        painter.setFont(QFont(self.value_fontname, int(
            self.value_fontsize / 2.5), QFont.Bold))

        angle_end = float(self.scale_angle_start_value +
                          self.scale_angle_size + 180)
        angle = (angle_end - self.scale_angle_start_value) / \
            2 + self.scale_angle_start_value

        x = text_radius * math.cos(math.radians(angle))
        y = text_radius * math.sin(math.radians(angle))
        # print(w, h, x, y, text)
        painter.drawText(int(x - w / 2), int(y - h / 2), int(w),
                         int(h), Qt.AlignCenter, text)

    
    # CENTER POINTER
    

    def draw_big_needle_center_point(self, diameter=30):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)

        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        # painter.setPen(Qt.NoPen)

        # painter.setBrush(self.CenterPointColor)
        # diameter = diameter # self.widget_diameter/6
        # painter.drawEllipse(int(-diameter / 2), int(-diameter / 2), int(diameter), int(diameter))

        # create_polygon_pie(self, outer_radius, inner_raduis, start, lenght)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 8) - (self.pen.width() / 2)),
            0,
            self.scale_angle_start_value, 360, False)

        # 150.0 0.0 131 360

        grad = QConicalGradient(QPointF(0, 0), 0)

        # todo definition scale color as array here
        for eachcolor in self.needle_center_bg:
            grad.setColorAt(eachcolor[0], eachcolor[1])
        # grad.setColorAt(.00, Qt.red)
        # grad.setColorAt(.1, Qt.yellow)
        # grad.setColorAt(.15, Qt.green)
        # grad.setColorAt(1, Qt.transparent)
        painter.setBrush(grad)
        # self.brush = QBrush(QColor(255, 0, 255, 255))
        # painter_filled_polygon.setBrush(self.brush)

        painter.drawPolygon(colored_scale_polygon)
        # return painter_filled_polygon

    
    # CREATE OUTER COVER
    
    def draw_outer_circle(self, diameter=30):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        colored_scale_polygon = self.create_polygon_pie(
            ((self.widget_diameter / 2) - (self.pen.width())),
            (self.widget_diameter / 6),
            self.scale_angle_start_value / 10, 360, False)

        radialGradient = QRadialGradient(QPointF(0, 0), self.width())

        for eachcolor in self.outer_circle_bg:
            radialGradient.setColorAt(eachcolor[0], eachcolor[1])

        painter.setBrush(radialGradient)

        painter.drawPolygon(colored_scale_polygon)

    
    # NEEDLE POINTER
    

    def draw_needle(self):
        painter = QPainter(self)
        # painter.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.Antialiasing)
        # Koordinatenursprung in die Mitte der Flaeche legen
        painter.translate(self.width() / 2, self.height() / 2)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.NeedleColor)
        painter.rotate(((self.valueVelo - self.value_offset - self.minValueVelo) * self.scale_angle_size /
                        (self.maxValueVelo - self.minValueVelo)) + 90 + self.scale_angle_start_value)

        painter.drawConvexPolygon(self.value_needle[0])

    
    # EVENTS
    

    
    # ON WINDOW RESIZE
    
    def resizeEvent(self, event):
        # self.resized.emit()
        # return super(self.parent, self).resizeEvent(event)
        # print("resized")
        # print(self.width())
        self.rescale_method()
        # self.emit(QtCore.SIGNAL("resize()"))
        # print("resizeEvent")

    
    # ON PAINT EVENT
    
    def paintEvent(self, event):
        # Main Drawing Event:
        # Will be executed on every change
        # vgl http://doc.qt.io/qt-4.8/qt-demos-affine-xform-cpp.html
        # print("event", event)

        self.draw_outer_circle()
        self.draw_icon_image()
        # colored pie area
        if self.enable_filled_Polygon:
            self.draw_filled_polygon()

        # draw scale marker lines
        if self.enable_fine_scaled_marker:
            self.create_fine_scaled_marker()
        if self.enable_big_scaled_marker:
            self.draw_big_scaled_marker()

        # draw scale marker value text
        if self.enable_scale_text:
            self.create_scale_marker_values_text()

        # Display Value
        if self.enable_value_text:
            self.create_values_text()
            self.create_units_text()

        # draw needle 1
        if self.enable_Needle_Polygon:
            self.draw_needle()

        # Draw Center Point
        if self.enable_CenterPoint:
            self.draw_big_needle_center_point(
                diameter=(self.widget_diameter / 6))

    
    # MOUSE EVENTS
    

    # def setMouseTracking(self, flag):
    #     def recursive_set(parent):
    #         for child in parent.findChildren(QObject):
    #             try:
    #                 child.setMouseTracking(flag)
    #             except:
    #                 pass
    #             recursive_set(child)

    #     QWidget.setMouseTracking(self, flag)
    #     recursive_set(self)

    # def mouseReleaseEvent(self, QMouseEvent):
    #     self.NeedleColor = self.NeedleColorReleased

    #     if not self.use_timer_event:
    #         self.update()
    #     pass

########################################################! VELOCİTY END

global degisken 
degisken = None

##
class hpPage(QMainWindow):
    
    def __init__(self) -> None:
        super().__init__()
        self.homeForm = Ui_MainWindow() ## HomePage_python formu tanımlandı
        self.historyAc = historyPage() ## flightHisyory den, obje show yapmak için obje oluşturuldu
        self.homeForm.setupUi(self) 
        # self.setMinimumSize(1180,630)
        # self.setMaximumSize(1180,630)
        
        
        
        ######################## MAP ##################################
        # layoutdataFlight = QVBoxLayout()
        # self.setLayout(layoutdataFlight)
        hx = round(homeLoc.lat/1e7,6)
        hy = round(homeLoc.lon/1e7,6)
        home_icon = folium.Icon(icon='home', prefix='fa', color='green')
        mapObj2 = folium.Map(location=[hx, hy],   # HOME POSITION
                    zoom_start=10, tiles=None)
        #folium.Marker(location=[homeLoc.lat, homeLoc.lat], tooltip='Home Location',icon= home_icon).add_to(mapObj2)
        
        ###############
        folium.Marker(location=[homeLoc.lat, homeLoc.lon], tooltip='Target Location').add_to(mapObj2)   # HOME LOCATİON
        folium.Marker(location=[51.5074, -0.1205], tooltip='Target Location').add_to(mapObj2)   # HEDEF NOKTA
        folium.PolyLine(locations=[[homeLoc.lat, homeLoc.lon], [51.5074, -0.1205]], color='green',icon = home_icon).add_to(mapObj2)
        # çizim yapmak için kullanıyoruz
        draw = Draw(
            
            export=True,
            filename="my_data.geojson",
            position="topleft",
            draw_options={"polyline": {"allowIntersection": True}}, #kesişim olmamasını istiyorsak false yaparız
            edit_options={"poly": {"allowIntersection": True}},
        )
        draw.add_to(mapObj2)
        
        
        formatter = "function(num) {return L.Util.formatNum(num, ) + ' º ';};"

        MousePosition(
            position="topright",
            separator=" | ",
            empty_string="NaN",
            lng_first=True,
            num_digits=20,
            prefix="Coordinates:",
            lat_formatter=formatter,
            lng_formatter=formatter,
        ).add_to(mapObj2)

        

      
        minimap = plugins.MiniMap()
        mapObj2.add_child(minimap)
        

        # add tile layers
        folium.TileLayer('openstreetmap').add_to(mapObj2)
        folium.TileLayer('stamenterrain', attr="stamenterrain").add_to(mapObj2)
        folium.TileLayer('stamenwatercolor', attr="stamenwatercolor").add_to(mapObj2)
        folium.TileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', name='CartoDB.DarkMatter', attr="CartoDB.DarkMatter").add_to(mapObj2)

        
        # add layers control over the map
        folium.LayerControl().add_to(mapObj2)

        data = io.BytesIO()
        mapObj2.save(data, close_file=False)
        mp = MousePosition()
        mp.add_to(mapObj2)

        # bu kısım sadece konum verilerini ekrana göstermek için kullanılıyor
        class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):
            def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
                    sil = "TRUNCATE TABLE koordinat"
                    #im.execute(sil)
                    #conn.commit()
                    coords_dict = json.loads(message)
                    print(*coords_dict['geometry']['coordinates'])
                    coords = coords_dict['geometry']['coordinates']
                    for pos in coords:
                        ekle = "INSERT INTO koordinat (KoordinatID,X,Y) VALUES (NULL,'{}','{}')" 
                        data1=(pos[0],pos[1])
                        ekle = ekle.format(*data1)
                        #im.execute(ekle)
                        #conn.commit()

        view = QtWebEngineWidgets.QWebEngineView(self.homeForm.mapwidget)
        page = WebEnginePage(view)
        view.setGeometry(0, 0, 700, 500)
        map_html = mapObj2._repr_html_()
        view.setHtml(map_html)
        #view.setPage(page)
        view.setHtml(data.getvalue().decode())
        mapObj2.save('map.html')

        
        ######################## ALTTİTUDE GAUGE ########################
        altGauge = AnalogGauge_alt() # Gauge eklemek için bir widget class'ını ekle
        altGaugeLayout = QVBoxLayout(self.homeForm.altGauge)
        altGaugeLayout.addWidget(altGauge)
        self.homeForm.altGauge.setLayout(altGaugeLayout)# Ana pencereye layout ekle
        #################################################################
        
        ######################## GROUNDSPEED GAUGE ######################## 
        groundGauge = AnalogGauge_ground()
        groundGaugeLayout = QVBoxLayout()
        self.homeForm.groundGauge.setLayout(groundGaugeLayout)# Ana pencereye layout ekle
        groundGaugeLayout.addWidget(groundGauge)
        #################################################################
        
        ######################## AİRSPEED GAUGE ######################## 
        airSpeedGauge = AnalogGauge_airSpeed()
        airSpeedGaugeLayout = QVBoxLayout(self.homeForm.airSpeedGauge)
        airSpeedGaugeLayout.addWidget(airSpeedGauge)
        self.homeForm.airSpeedGauge.setLayout(airSpeedGaugeLayout)# Ana pencereye layout ekle
        #################################################################
        
        ######################## VELOCİTY GAUGE ######################## 
        velocityGauge = AnalogGauge_velocity()
        velocityGaugeLayout = QVBoxLayout()
        self.homeForm.velocityGauges.setLayout(velocityGaugeLayout)# Ana pencereye layout ekle
        velocityGaugeLayout.addWidget(velocityGauge)
        #################################################################
        
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_mission)        
        self.homeForm.btn_package.clicked.connect(self.showPackage)
        self.homeForm.btn_homePage.clicked.connect(self.showEnvanter)
        self.homeForm.btn_dataFlight.clicked.connect(self.showDataFlight)
        self.homeForm.btn_preFlight.clicked.connect(self.showPreFlight)
        self.homeForm.btn_settings.clicked.connect(self.showSettings)
        self.homeForm.btn_sepeteEkle.clicked.connect(self.sepeteEkle)
        self.homeForm.btn_mission.clicked.connect(self.showMission)
        self.homeForm.btn_tansiyon.clicked.connect(self.tansiyonSec)
        self.homeForm.btn_insulin.clicked.connect(self.insulinSec)
        self.homeForm.btn_boyunluk.clicked.connect(self.boyunlukSec)
        self.homeForm.btn_ilacKutusu.clicked.connect(self.ilacSec)
        self.homeForm.btn_nebulizator.clicked.connect(self.nebulizatorSec)
        self.homeForm.btn_telefon.clicked.connect(self.telefonSec)
        self.homeForm.btn_laptop.clicked.connect(self.laptopSec)
        self.homeForm.btn_tablet.clicked.connect(self.tabletSec)
        self.homeForm.btn_kulaklik.clicked.connect(self.kulaklikSec)
        self.homeForm.btn_guckaynagi.clicked.connect(self.powerSec)
        self.homeForm.btn_kablo.clicked.connect(self.kabloSec)
        self.homeForm.urun1Sil.hide()
        self.homeForm.urun2Sil.hide()
        self.homeForm.urun3Sil.hide()
        self.homeForm.urunpic1.hide()
        self.homeForm.urunpic2.hide()
        self.homeForm.urunpic3.hide()
        self.homeForm.urun1Sil.clicked.connect(self.urun1Sil)
        self.homeForm.urun2Sil.clicked.connect(self.urun2Sil)
        self.homeForm.urun3Sil.clicked.connect(self.urun3Sil)
        self.homeForm.btnOnayla.clicked.connect(self.paketBilgisi)
        self.homeForm.textGondericiGemi.setText("POYRAZ")
        self.homeForm.textHedefGemi.setText("POYRAZ V2")
        self.homeForm.paketurun1.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.paketurun2.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.paketurun3.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.btnGuideMode.clicked.connect(self.guideMode)
        self.homeForm.btnAutoMode.clicked.connect(self.autoMode)
        self.homeForm.btnQrtlMode.clicked.connect(self.qrtlMode)
        self.homeForm.btnGuideMode.clicked.connect(self.disarmedMode)
        self.homeForm.checkCameraOn.stateChanged.connect(self.start_webcam)
        self.homeForm.armBtn.clicked.connect(self.armControl)
        self.homeForm.takeOffBtn.clicked.connect(self.takeOffControl)
        self.homeForm.connectBtn.clicked.connect(self.mapGetir)
        #self.homeForm.escCheckBtn.clicked.connect(self.escCheck)
        self.homeForm.disarmBtn.clicked.connect(self.disarmedMode)
        self.homeForm.btnExit.clicked.connect(self.close)
        self.homeForm.labelTitle.setText("MİSSİON")
        # self.homeForm.btn_menu.clicked.connect(self.toggleMenu)
        self.homeForm.labelSatellite.setText("15")
        self.homeForm.labelFixed.setText("0.8")
        
        homeline = [homeLoc.lat,homeLoc.lon]
        self.homeForm.line_HomeLocation.setText(str(homeline))
        
        self.homeForm.textNereden_lat.setText(str(homeLoc.lat/1e7)) 
        self.homeForm.textNereden_lon.setText(str(homeLoc.lon/1e7))
        
        ####### DONANIM KONTROLLERİ
        self.homeForm.modeCheck.setCurrentIndex(1)
        self.homeForm.labelTelemetry.setText("% 100")
        self.homeForm.gpsCheck.setChecked(True)
        #self.homeForm.yesRadioEquip.setChecked(True)
        ### Waypoint number eklenecek(folium marker'den saydırılacak)
        #######
        
        ###### YAZILIM KONTROLLERİ
        self.homeForm.batteryLabel.setText("100")
        self.homeForm.cameraYesradio.setChecked(True)
        self.homeForm.engineCheck.setChecked(True)
        self.homeForm.safetyFuseCheck.setChecked(True)
        self.homeForm.mechanicCheck.setChecked(True)
        self.homeForm.switchCheck.setChecked(True)#
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_alt)
        self.timer.start(1000) # 1 saniyede bir tekrarla
        
        
        
 
    def mapGetir(self):
        mapgetir = QMessageBox()
        mapgetir.about(self,"BASARILI","BAGLANTI SAGLANDI!")
        self.historyAc.show()
    
    
    """def escCheck(self): # bağlantısı yapılmadı
        # ESC kalibrasyon moduna geçiş yapma
        vehicle.mav.command_long_send(
            vehicle.target_system,      # Hedef sistemin sistem ID'si
            vehicle.target_component,   # Hedef bileşenin bileşen ID'si
            mavutil.mavlink.MAV_CMD_DO_ESC_CALIBRATION, # ESC kalibrasyon komutu
            0, 0, 0, 0, 0, 0, 0)      # Parametreler
        
        # Motorların minimum hızda dönmesini sağlama
        vehicle.mav.command_long_send(
            vehicle.target_system,      # Hedef sistemin sistem ID'si
            vehicle.target_component,   # Hedef bileşenin bileşen ID'si
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # Servo pozisyonu ayarlama komutu
            1,                          # SERVO1 kanalı
            1100,                       # Minimum hız için PWM değeri
            0, 0, 0, 0, 0)             # Parametreler
        # Bekleme süresi
        time.sleep(5)   
        
        # Motorların durdurulması
        vehicle.mav.command_long_send(
            vehicle.target_system,      # Hedef sistemin sistem ID'si
            vehicle.target_component,   # Hedef bileşenin bileşen ID'si
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,  # Servo pozisyonu ayarlama komutu
            1,                          # SERVO1 kanalı
            1500,                       # Orta nokta için PWM değeri
            0, 0, 0, 0, 0)             # Parametreler"""
    
        
    def update_alt(self):     
            # # GPS_RAW_INT mesajının uydu sayısı bilgisinin alınması
            # satellites_visible = getattr(Gpsmsg, 'satellites_visible', None )
            # self.homeForm.labelSatellite.setText(str(satellites_visible))
        
            # fix_type = getattr(Gpsmsg, 'fix_type', None)
            # self.homeForm.labelFixed.setText(str(fix_type))
            
            msg = vehicle.recv_match(type='SYS_STATUS', blocking=True)
            batarya = msg.voltage_battery / 1000.0
            self.homeForm.progressBar.setValue(batarya)
            

            
                                                
        
    def guideMode(self):
        QMessageBox.warning(" VTOL |GUIDE| Moda geçiş yapiliyor...")
        
    
    def qrtlMode(self):
        QMessageBox.warning(" VTOL |QRTL| Moda geçiş yapiliyor...")
        
    def autoMode(self):
        QMessageBox.warning(" VTOL |AUTO| Moda geçiş yapiliyor...")
        
    def disarmedMode(self):
        QMessageBox.warning(" VTOL |DİSARMED| Moda geçiş yapiliyor...\nBaglanti Kesiliyor...")
        
    
    # def toggleMenu(self):
    #     if  self.homeForm.leftMenu.maximumWidth()==70:
    #         self.homeForm.leftMenu.setMaximumWidth(130)
    #         self.homeForm.btn_homePage.setText("Envanter ")
    #         self.homeForm.btn_package.setText("Package  ")
    #         self.homeForm.btn_mission.setText("Mission   ")
    #         self.homeForm.btn_dataFlight.setText("Data F.   ")
    #         self.homeForm.btn_preFlight.setText("Pre F.     ")
    #         self.homeForm.btn_settings.setText("Settings  ")
    #         self.homeForm.btn_poyrazLogo.show()
    #     else:
    #         self.homeForm.leftMenu.setMaximumWidth(70)
    #         self.homeForm.btn_homePage.setText("")
    #         self.homeForm.btn_package.setText("")
    #         self.homeForm.btn_mission.setText("")
    #         self.homeForm.btn_dataFlight.setText("")
    #         self.homeForm.btn_preFlight.setText("")
    #         self.homeForm.btn_settings.setText("")
    #         self.homeForm.btn_poyrazLogo.hide()
    #         self.homeForm.logoWidget.show()        
    
    def takeOffControl(self):
        vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0)
        ############################## ARM
        print("Waiting for the vehicle to arm")
        vehicle.motors_armed_wait()
        print('Armed!')
        time.sleep(3)
        ############################ ARM COMPLETE
        
        # Take off
        print("Taking off!")
        vehicle.mav.command_long_send(
            vehicle.target_system,
            vehicle.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 1,1)  # 10 meters altitude
        time.sleep(1)
        
        # Transition to forward flight mode
        print("Transitioning to forward flight mode...")
        vehicle.mav.set_mode_send(
            vehicle.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mavutil.mavlink.MAV_VTOL_STATE_TRANSITION_TO_MC)

        # Wait for transition to complete
        time.sleep(3)
        print("VTOL takeoff complete!")
        
                # Disarm
        # vehicle.arducopter_disarm() or:
        vehicle.mav.command_long_send(
            vehicle.target_system,
            vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0)

        # wait until disarming confirmed
        vehicle.motors_disarmed_wait()
        print('disArmed!')
        
    def disarmedMode(self):
                # Disarm
        # vehicle.arducopter_disarm() or:
        vehicle.mav.command_long_send(
            vehicle.target_system,
            vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0)

        # wait until disarming confirmed
        vehicle.motors_disarmed_wait()
        print('disArmed!')

        
        # vehicle.mav.command_long_send(
        # vehicle.target_system,
        # vehicle.target_component,
        # mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        # 0,
        # 0, 0, 0, 0, 0, 0, 0)
        # # wait until disarming confirmed
        # vehicle.motors_disarmed_wait()
        
    
    def armControl(self):
        vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_MANUAL_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0)
        ############################## ARM
        print("Waiting for the vehicle to arm")
        vehicle.motors_armed_wait()
        print('Armed!')
        ############################ ARM COMPLETE
        # while True:
        #     vehicle.mav.command_long_send(
        #     vehicle.target_system,
        #     vehicle.target_component,
        #     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        #     0,
        #     1, 0, 0, 0, 0, 0, 0)
        #     print("Waiting for the vehicle to arm")
        #     vehicle.motors_armed_wait()
        #     print('Armed!')
        #     break
        
    def urun1Sil(self):
        self.homeForm.urunpic1.setStyleSheet("")
        self.homeForm.paketurun1.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.urunpic1.hide()
        self.homeForm.urun1Sil.hide()
        
    def urun2Sil(self):
        self.homeForm.urunpic2.setStyleSheet("")
        self.homeForm.paketurun2.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.urunpic2.hide()
        self.homeForm.urun2Sil.hide()
        
    def urun3Sil(self):
        self.homeForm.urunpic3.hide()
        self.homeForm.urunpic3.setStyleSheet("")
        self.homeForm.paketurun3.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        self.homeForm.urun3Sil.hide()
        pass
    
    def tansiyonSec(self):
        
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/tansiyon aleti1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/tansiyon aleti1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/tansiyon aleti1.png);")
        else : 
            pass
        pass
    
    def insulinSec(self):
        if not self.homeForm.urunpic1.styleSheet():
          self.homeForm.urunpic1.show()
          self.homeForm.urun1Sil.show()
          self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/İnsulin kalemi1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
          self.homeForm.urunpic2.show()
          self.homeForm.urun2Sil.show()
          self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/İnsulin kalemi1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/İnsulin kalemi1.png);")
        else : 
            pass
        
    def boyunlukSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Medikal boyunluk1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Medikal boyunluk1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Medikal boyunluk1.png);")
        else : 
            pass
            
    def ilacSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/ilacKutusu1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/ilacKutusu1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/ilacKutusu1.png);")
        else : 
            pass
            
    def nebulizatorSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Nebulizator1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
             self.homeForm.urunpic2.show()
             self.homeForm.urun2Sil.show()
             self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Nebulizator1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Nebulizator1.png);")
        else : 
            pass
        
    def telefonSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Cep Telefonu1.jpg.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Cep Telefonu1.jpg.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Cep Telefonu1.jpg.png);")
        else : 
            pass
        
    def laptopSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/laptop1.jpg.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/laptop1.jpg.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/laptop1.jpg.png);")
        else : 
            pass
    
    def kulaklikSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kulaklik1.jpg.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kulaklik1.jpg.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kulaklik1.jpg.png);")
        else : 
            pass
    
    def tabletSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Tablet1.jpg.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Tablet1.jpg.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Tablet1.jpg.png);")
        else : 
            pass
            
    def powerSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/gucKaynagi1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/gucKaynagi1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/gucKaynagi1.png);")
        else : 
            pass
    
    def kabloSec(self):
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.urunpic1.show()
            self.homeForm.urun1Sil.show()
            self.homeForm.urunpic1.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kablo1.png);")
        elif not self.homeForm.urunpic2.styleSheet():
            self.homeForm.urunpic2.show()
            self.homeForm.urun2Sil.show()
            self.homeForm.urunpic2.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kablo1.png);")
        elif not self.homeForm.urunpic3.styleSheet():
            self.homeForm.urunpic3.show()
            self.homeForm.urun3Sil.show()
            self.homeForm.urunpic3.setStyleSheet("border-image: url(:/envanter/images/img/newimg/Kablo1.png);")  
        else : 
            pass
        
    def start_webcam(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.timer = QTimer()
        self.timer.start(30)
        self.timer.timeout.connect(self.update_frame)
        
                  
    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            self.homeForm.label_location.height = 640
            self.homeForm.label_location.width = 480
            height = 640
            width = 480
            # Görüntüyü ekrana yansıt
            image = QImage(frame, frame.shape[1], frame.shape[0], 
                           frame.strides[0], QImage.Format_RGB888)
            self.homeForm.label_location.setPixmap(QPixmap.fromImage(image))
            frame_flipped = cv2.flip(frame,1) #### Camera yatay eksende flip
            rgb_image = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
            rgb_image_resized = cv2.resize(rgb_image, (width,height))
            qimage = QImage(rgb_image_resized, rgb_image_resized.shape[1], rgb_image_resized.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            self.homeForm.label_location.setPixmap(pixmap)
            self.homeForm.label_location.setMaximumHeight = height
            self.homeForm.label_location.setMaximumWidth = width
            
        ret, frame = self.capture.read()
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        label_size = self.homeForm.label_location.size()
        rgb_image_resized = cv2.resize(rgb_image, (label_size.width(), label_size.height()))
        qimage = QImage(rgb_image_resized, rgb_image_resized.shape[1], rgb_image_resized.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.homeForm.label_location.setPixmap(pixmap)    
        if ret:
         frame_flipped = cv2.flip(frame, 1)  # 1, görüntüyü yatayda ters çevirir
         rgb_image = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
         label_size = self.homeForm.label_location.size()
         rgb_image_resized = cv2.resize(rgb_image, (label_size.width(), label_size.height()))
         qimage = QImage(rgb_image_resized, rgb_image_resized.shape[1], rgb_image_resized.shape[0], QImage.Format_RGB888)
         pixmap = QPixmap.fromImage(qimage)
         self.homeForm.label_location.setPixmap(pixmap)
        
    def paketBilgisi(self):
        
        gondericiAdi = self.homeForm.textisim.text()
        gondericiSoyad = self.homeForm.textSoyad.text()
        gondericiTel = self.homeForm.textTelefon.text()
        gonderenGemi = "POYRAZ"
        hedefGemi = "POYRAZ V2" 
        home_lat = self.homeForm.textNereden_lat.text()
        home_lon = self.homeForm.textNereden_lon.text()
        QMessageBox.warning(self, "PAKET", "SİPARİS BASARİYLA GONDERİLDİ!")
        self.homeForm.textisim.clear()
        self.homeForm.textSoyad.clear()
        self.homeForm.textTelefon.clear()       
        self.homeForm.textGondericiGemi.clear()     
        self.homeForm.textHedefGemi.clear()
        self.homeForm.textNereden_lat.clear()
        self.homeForm.textNereden_lon.clear()
        
        
    
    def sepeteEkle(self):
        mesajKutusu=QMessageBox
        mesajKutusu.about(self,"Başarili!","Urunler Pakete Eklendi!")       
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_package)
        self.homeForm.paketurun1.setStyleSheet(self.homeForm.urunpic1.styleSheet())
        self.homeForm.paketurun2.setStyleSheet(self.homeForm.urunpic2.styleSheet())
        self.homeForm.paketurun3.setStyleSheet(self.homeForm.urunpic3.styleSheet())
        if not self.homeForm.urunpic1.styleSheet():
            self.homeForm.paketurun1.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        if not self.homeForm.urunpic2.styleSheet():
            self.homeForm.paketurun2.setStyleSheet("background-color:rgba(80, 70, 230,150);")
        if not self.homeForm.urunpic3.styleSheet():
            self.homeForm.paketurun3.setStyleSheet("background-color:rgba(80, 70, 230,150);")
                
    def showEnvanter(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_envanter)
        print("Envanter acildi.")
        self.homeForm.labelTitle.setText("ENVANTER")
        
        
    def showPackage(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_package)
        print("Paket acildi.")
        self.homeForm.labelTitle.setText("PACKAGE")
        
    def showDataFlight(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_dataFlight)
        print("Ucus Verileri acildi.")
        self.homeForm.labelTitle.setText("DATA-FLİGHT")
        
    
    def showPreFlight(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_preFlight)
        print("PreFlight acildi.")
        self.homeForm.labelTitle.setText("PRE-FLİGHT")
        
    def showSettings(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_settings)
        print("Ayarlar acildi.")
        self.homeForm.labelTitle.setText("SETTİNGS")
        
    def showMission(self):
        self.homeForm.stackedWidget.setCurrentWidget(self.homeForm.page_mission)
        print("Gorev acildi.")
        self.homeForm.labelTitle.setText("MİSSİON")       
        