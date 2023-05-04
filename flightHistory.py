from PyQt5.QtWidgets import *
from flightHistory_python import Ui_flightWindow
import sys
import cv2
import os
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time
from folium.plugins import MarkerCluster
from encodings import search_function
from PyQt5 import QtWebEngineWidgets
from folium.plugins import Draw ,MousePosition
import folium, io, sys, json
from folium import plugins
from pymavlink import mavutil
import HomePage

class historyPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.historyForm = Ui_flightWindow() ## flightHistory_python formu tanımlandı
        self.historyForm.setupUi(self)
        self.vehicle = HomePage.vehicle
        self.gps = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        self.mapTimer = QTimer(self)
        self.mapTimer.timeout.connect(self.update_Map)
        self.mapTimer.start(1000) # 1 saniyede bir tekrarla
    
        dx = round(self.gps.lat/1e7,6)
        dy = round(self.gps.lon/1e7,6)
        

        self.mapObj = folium.Map(location=[dx, dy],zoom_start=50, icon = 'home' ) # HARİTA BAŞLANGIÇ LOCATİON
        home_icon = folium.Icon(icon='home', prefix='fa', color='green')
        folium.Marker(location=[dx, dy], tooltip='Home Location',icon=home_icon).add_to(self.mapObj)
        draw = Draw(
        export=True,
        filename="my_data.geojson",
        position="topleft",
        draw_options={"polyline": {"allowIntersection": True}}, #kesişim olmamasını istiyorsak false yaparız
        edit_options={"poly": {"allowIntersection": True}},
        )
        draw.add_to(self.mapObj)
        
        
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
        ).add_to(self.mapObj)
        
        minimap = plugins.MiniMap()
        self.mapObj.add_child(minimap)
        

        # add tile layers
        folium.TileLayer('openstreetmap').add_to(self.mapObj)
        folium.TileLayer('stamenterrain', attr="stamenterrain").add_to(self.mapObj)
        folium.TileLayer('stamenwatercolor', attr="stamenwatercolor").add_to(self.mapObj)
        folium.TileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', name='CartoDB.DarkMatter', attr="CartoDB.DarkMatter").add_to(self.mapObj)

        
        # add layers control over the map
        folium.LayerControl().add_to(self.mapObj)

        data = io.BytesIO()
        self.mapObj.save(data, close_file=False)
        
        mp = MousePosition()
        mp.add_to(self.mapObj)

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

        view = QtWebEngineWidgets.QWebEngineView(self.historyForm.mapWidget)
        view.setGeometry(0, 0, 1900, 950)
        map_html = self.mapObj._repr_html_()
        view.setHtml(map_html)
        view.setHtml(data.getvalue().decode())
        self.mapObj.save('map_dataFlight.html')
        
        self.timerAlt = QTimer(self)
        self.timerAlt.timeout.connect(self.update_Map)
        self.timerAlt.start(1000) # 1 saniyede bir tekrarla
        
    def update_Map(self):        
        live_lat = round(self.gps.lat / 1.0e7, 4)
        live_lon = round(self.gps.lon / 1.0e7, 4)
        folium.Marker(location=[live_lat, live_lon], tooltip='Live Location',icon=folium.Icon(color='red', icon='info-sign')).add_to(self.mapObj)
        #print("lat:{}, lon:{}".format(live_lat, live_lon))  
        