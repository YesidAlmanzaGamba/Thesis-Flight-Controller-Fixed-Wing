import folium
import io
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore, QtGui
#import geocoder
import json
from folium import plugins
from stl import mesh
from pyqtgraph.opengl import GLViewWidget, MeshData, GLMeshItem
import pyqtgraph as pg
import numpy as np
import serial_comm as my_serial
import sys

yaw, roll, pitch = 0, 0, 0
lat, lon = 0, 0

def animate_mesh():
    global yaw, roll, pitch
    rotate_mesh(yaw, roll, pitch)

def rotate_mesh(yaw_angle, roll_angle, pitch_angle):
    meshIem.resetTransform()  # Reset the transformation
    meshIem.rotate((yaw_angle), 0, 1, 0)  # Apply yaw rotation
    meshIem.rotate((pitch_angle), 1, 0, 0) 
    meshIem.rotate((roll_angle), 0, 0, 1)
    

def update_yaw(value):
    global yaw
    yaw = value
    animate_mesh()

def update_roll(value):
    global roll
    roll = value
    animate_mesh()

def update_pitch(value):
    global pitch
    pitch = value
    animate_mesh()

class WorkerThread(QThread):
    def run(self):
        serial_connector = my_serial.SerialObj(115200)
    
        serialForConnect = sys.argv[1]
        serial_connector.connect(serialForConnect)
        first = True
        global altInicial
        altInicial = 0
        while True: 

           if serial_connector.is_connect():
            
                try:
                    data_string = serial_connector.get_data().decode('utf-8').replace('\r\n','')
                    data_array = data_string.split(',')
                    print(data_array)
                    yaw=float(data_array[6])
                    pitch=float(data_array[7])
                    roll=float(data_array[8])
                    global lat, lon
                    #lat = (data_array[9])
                    #lon = (data_array[10])
                    temp = data_array[0]
                    presu = float(data_array[1])
                    alt = float(data_array[2])

                    Temperatura.setText(str(temp))

                    PunteroAltura.setGeometry(QtCore.QRect(90, 400 - int(alt - altInicial)*4, 70, 20))
                    HorizonteArt.setGeometry(QtCore.QRect(15, -int(pitch), 175, 175))
                    HorizonteArt.setPixmap(QtGui.QPixmap(".\\img/Untitled-8.png").transformed(QtGui.QTransform().rotate(roll)))
                    Brujula.setPixmap(QtGui.QPixmap(".\\img/Untitled-7.png").transformed(QtGui.QTransform().rotate(-yaw)))
                    Presion.setPixmap(QtGui.QPixmap(".\\img/Untitled-11.png").transformed(QtGui.QTransform().rotate(((presu/133.322)/50)*360)))
                    Velocidad.setPixmap(QtGui.QPixmap(".\\img/Untitled-10.png").transformed(QtGui.QTransform().rotate(yaw))) #==================================================================================================Toca Cambiarlo
                    
                    metri3_2.setText(f"Presion manifold ({round(presu,2)})")
                    metri5.setText(f"Horizonte artificial ({round(pitch, 2)}, {round(roll,2)})")
                    metri7.setText(f"Norte (Roll) ({round(roll, 2)})")
                    metri4.setText(f"Altitud ({alt})")
                    metri8.setText(f"Anometro ({round(yaw, 2)})") #==================================================================================================Toca Cambiarlo

                    update_pitch(pitch)
                    update_roll(roll)
                    update_yaw(yaw)
                    if first:
                        altInicial = alt
                        first = False
                    

                except:
                    pass
                    try:
                        serial_connector.connect(serialForConnect)
                    except:
                        pass
                

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        #=============================================================
        try:
            myjsonFile = open('currentData.json', 'r')
        except:
            open("currentData.json", "x")
            myjsonFile = open('currentData.json', 'r')

        df = myjsonFile.read()
        if(df != ''):
            if(json.loads(df)[0][2] != 'Posicion En Tiempo Real'):
                self.marker_coord = [[lon, lat, 'Posicion En Tiempo Real'] ,*json.loads(df)]
            else:
                self.marker_coord = [*json.loads(df)]


        data = io.BytesIO()

        if len(self.marker_coord) > 0 :
            self.m = folium.Map(location=[self.marker_coord[0][0],self.marker_coord[0][1]], zoom_start=50)
        marker_radius = 20
        for index, i in enumerate(self.marker_coord):
            if(index == 0):
                folium.Marker(
                    location = [i[0], i[1]],
                    icon = folium.Icon(color='black', icon='home'),
                    tooltip=f'{i[2]}',
                    ).add_to(self.m)
            else:
                folium.vector_layers.Circle(
                location=[i[0], i[1]],
                tooltip=f"Radio de {marker_radius} metros",
                radius=marker_radius,
                color="red",
                fill=True,
                fill_color="blue"
                    ).add_to(self.m)
                folium.Marker(
                    location = [i[0], i[1]],
                    icon = folium.Icon(color='red'),
                    tooltip=f'Punto de control: {i[2]}',
                    ).add_to(self.m)
            if(index < len(self.marker_coord)-1):
                folium.PolyLine(
                    [[self.marker_coord[index][0],self.marker_coord[index][1]], [self.marker_coord[index+1][0],self.marker_coord[index+1][1]]],
                    tooltip=f"Trayecto: {self.marker_coord[index][2]} --> {self.marker_coord[index+1][2]}",
                    color= 'black',
                    weight= 10,
                    opacity= 0.5
                ).add_to(self.m)
            #lines
        if(len(self.marker_coord) > 2):
            folium.PolyLine(
                [[self.marker_coord[0][0],self.marker_coord[0][1]], [self.marker_coord[-1][0],self.marker_coord[-1][1]]],
                tooltip='Trayectoria de regreso',
                color= 'red',
                weight= 10,
                opacity= 0.5
            ).add_to(self.m)
        elif(len(self.marker_coord) == 2):
                folium.PolyLine(
                [[self.marker_coord[0][0],self.marker_coord[0][1]], [self.marker_coord[-1][0],self.marker_coord[-1][1]]],
                tooltip='Trayectoria de ida y vuelta',
                color= 'purple',
                weight= 10,
                opacity= 0.5
            ).add_to(self.m)
                
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        folium.plugins.LocateControl().add_to(self.m)

        plugins.MousePosition(position='topright', separator=' | ', prefix="Position:",lat_formatter=roundnum, lng_formatter=roundnum).add_to(self.m)
        self.m.add_child(folium.LatLngPopup())

        self.m.save(data, close_file=False)
        self.webView = QtWebEngineWidgets.QWebEngineView()

        self.webView.setHtml(data.getvalue().decode())
    
        #=============================================================

        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(862, 560)
        MainWindow.setMinimumSize(QtCore.QSize(862, 560))
        MainWindow.setMaximumSize(QtCore.QSize(862, 560))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.iconOnly = QtWidgets.QWidget(self.centralwidget)
        self.iconOnly.setMaximumSize(QtCore.QSize(81, 16777215))
        self.iconOnly.setObjectName("iconOnly")
        self.iconOnly.setStyleSheet("background-color: #161B22")

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.iconOnly)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Ruta1 = QtWidgets.QPushButton(self.iconOnly)
        self.Ruta1.setMinimumSize(QtCore.QSize(40, 40))
        self.Ruta1.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(".\\img/map-marker (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(".\\img/map-marker.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Ruta1.setIcon(icon)
        self.Ruta1.setIconSize(QtCore.QSize(20, 20))
        self.Ruta1.setCheckable(True)
        self.Ruta1.setAutoExclusive(True)
        self.Ruta1.setObjectName("Ruta1")
        self.Ruta1.setStyleSheet("color: #fff; border : none")

        self.verticalLayout.addWidget(self.Ruta1)
        self.Modelo1 = QtWidgets.QPushButton(self.iconOnly)
        self.Modelo1.setMinimumSize(QtCore.QSize(40, 40))
        self.Modelo1.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(".\\img/settings-sliders (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(".\\img/settings-sliders.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Modelo1.setIcon(icon1)
        self.Modelo1.setIconSize(QtCore.QSize(20, 20))
        self.Modelo1.setCheckable(True)
        self.Modelo1.setAutoExclusive(True)
        self.Modelo1.setObjectName("Modelo1")
        self.Modelo1.setStyleSheet("color: #fff; border : none")

        self.verticalLayout.addWidget(self.Modelo1)
        self.Metricas1 = QtWidgets.QPushButton(self.iconOnly)
        self.Metricas1.setMinimumSize(QtCore.QSize(40, 40))
        self.Metricas1.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(".\\img/cubes (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon2.addPixmap(QtGui.QPixmap(".\\img/cubes.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Metricas1.setIcon(icon2)
        self.Metricas1.setIconSize(QtCore.QSize(20, 20))
        self.Metricas1.setCheckable(True)
        self.Metricas1.setAutoExclusive(True)
        self.Metricas1.setObjectName("Metricas1")
        self.Metricas1.setStyleSheet("color: #fff; border : none")

        self.verticalLayout.addWidget(self.Metricas1)
        self.Graficas = QtWidgets.QPushButton(self.iconOnly)
        self.Graficas.setMinimumSize(QtCore.QSize(40, 40))
        self.Graficas.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(".\\img/chart-line-up (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon3.addPixmap(QtGui.QPixmap(".\\img/chart-line-up.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Graficas.setIcon(icon3)
        self.Graficas.setCheckable(True)
        self.Graficas.setAutoExclusive(True)
        self.Graficas.setObjectName("Graficas")
        self.Graficas.setStyleSheet("color: #fff; border : none")

        self.verticalLayout.addWidget(self.Graficas)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 331, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.Retorno = QtWidgets.QPushButton(self.iconOnly)
        self.Retorno.setMinimumSize(QtCore.QSize(40, 40))
        self.Retorno.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(".\\img/triangle-warning (1).png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon4.addPixmap(QtGui.QPixmap(".\\img/triangle-warning.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.Retorno.setIcon(icon4)
        self.Retorno.setIconSize(QtCore.QSize(20, 20))
        self.Retorno.setCheckable(True)
        self.Retorno.setAutoExclusive(False)
        self.Retorno.setObjectName("Retorno")
        self.Retorno.setStyleSheet("color: #fff; border : none")

        self.verticalLayout_3.addWidget(self.Retorno)
        self.horizontalLayout_5.addWidget(self.iconOnly)
        self.fullMenu = QtWidgets.QWidget(self.centralwidget)
        self.fullMenu.setMinimumSize(QtCore.QSize(100, 0))
        self.fullMenu.setMaximumSize(QtCore.QSize(100, 16777215))
        self.fullMenu.setObjectName("fullMenu")
        self.fullMenu.setStyleSheet("background-color: #161B22")

        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.fullMenu)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Ruta2 = QtWidgets.QPushButton(self.fullMenu)
        self.Ruta2.setMinimumSize(QtCore.QSize(40, 40))
        self.Ruta2.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.Ruta2.setIcon(icon)
        self.Ruta2.setIconSize(QtCore.QSize(20, 20))
        self.Ruta2.setCheckable(True)
        self.Ruta2.setAutoExclusive(True)
        self.Ruta2.setObjectName("Ruta2")
        self.Ruta2.setStyleSheet("color: #fff; border : none")

        self.verticalLayout_2.addWidget(self.Ruta2)
        self.Modelo2 = QtWidgets.QPushButton(self.fullMenu)
        self.Modelo2.setMinimumSize(QtCore.QSize(40, 40))
        self.Modelo2.setIcon(icon1)
        self.Modelo2.setIconSize(QtCore.QSize(20, 20))
        self.Modelo2.setCheckable(True)
        self.Modelo2.setAutoExclusive(True)
        self.Modelo2.setObjectName("Modelo2")
        self.Modelo2.setStyleSheet("color: #fff; border : none")

        self.verticalLayout_2.addWidget(self.Modelo2)
        self.Metricas2 = QtWidgets.QPushButton(self.fullMenu)
        self.Metricas2.setMinimumSize(QtCore.QSize(40, 40))
        self.Metricas2.setIcon(icon2)
        self.Metricas2.setIconSize(QtCore.QSize(20, 20))
        self.Metricas2.setCheckable(True)
        self.Metricas2.setAutoExclusive(True)
        self.Metricas2.setAutoDefault(False)
        self.Metricas2.setObjectName("Metricas2")
        self.Metricas2.setStyleSheet("color: #fff; border : none")

        self.verticalLayout_2.addWidget(self.Metricas2)
        self.Graficas2 = QtWidgets.QPushButton(self.fullMenu)
        self.Graficas2.setMinimumSize(QtCore.QSize(0, 40))
        self.Graficas2.setIcon(icon3)
        self.Graficas2.setCheckable(True)
        self.Graficas2.setAutoExclusive(True)
        self.Graficas2.setObjectName("Graficas2")
        self.Graficas2.setStyleSheet("color: #fff; border : none")

        self.verticalLayout_2.addWidget(self.Graficas2)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 331, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem1)
        self.Retorno2 = QtWidgets.QPushButton(self.fullMenu)
        self.Retorno2.setMinimumSize(QtCore.QSize(0, 40))
        self.Retorno2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.Retorno2.setIcon(icon4)
        self.Retorno2.setIconSize(QtCore.QSize(20, 20))
        self.Retorno2.setCheckable(True)
        self.Retorno2.setObjectName("Retorno2")
        self.Retorno2.setStyleSheet("color: #fff; border : none")


        self.verticalLayout_4.addWidget(self.Retorno2)
        self.horizontalLayout_5.addWidget(self.fullMenu)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.horizontalLayout_5.addLayout(self.verticalLayout_11)
        self.Content = QtWidgets.QWidget(self.centralwidget)
        self.Content.setObjectName("Content")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.Content)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.Menu = QtWidgets.QPushButton(self.Content)
        self.Menu.setMinimumSize(QtCore.QSize(30, 30))
        self.Menu.setMaximumSize(QtCore.QSize(30, 30))
        self.Menu.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(".\\img/apps.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Menu.setIcon(icon5)
        self.Menu.setIconSize(QtCore.QSize(20, 20))
        self.Menu.setCheckable(True)
        self.Menu.setObjectName("Menu")
        self.Menu.setStyleSheet("border: none")

        self.verticalLayout_5.addWidget(self.Menu)
        self.stackedWidget = QtWidgets.QStackedWidget(self.Content)
        self.stackedWidget.setMinimumSize(QtCore.QSize(0, 420))
        self.stackedWidget.setObjectName("stackedWidget")
        self.pageRuta = QtWidgets.QWidget()
        self.pageRuta.setMouseTracking(False)
        self.pageRuta.setObjectName("pageRuta")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.pageRuta)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.widget = self.webView
        # self.widget = QtWidgets.QWidget(self.pageRuta)
        self.widget.setMinimumSize(QtCore.QSize(0, 250))
        self.widget.setObjectName("widget")
        self.verticalLayout_9.addWidget(self.widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.AgregarParada = QtWidgets.QPushButton(self.pageRuta)
        self.AgregarParada.setObjectName("AgregarParada")
        self.AgregarParada.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout.addWidget(self.AgregarParada)
        self.EditarParada = QtWidgets.QPushButton(self.pageRuta)
        self.EditarParada.setObjectName("EditarParada")
        self.EditarParada.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout.addWidget(self.EditarParada)
        self.EliminarParada = QtWidgets.QPushButton(self.pageRuta)
        self.EliminarParada.setObjectName("EliminarParada")
        self.EliminarParada.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout.addWidget(self.EliminarParada)
        self.Subir = QtWidgets.QPushButton(self.pageRuta)
        self.Subir.setObjectName("Subir")
        self.Subir.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout.addWidget(self.Subir)
        self.Bajar = QtWidgets.QPushButton(self.pageRuta)
        self.Bajar.setObjectName("Bajar")
        self.Bajar.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout.addWidget(self.Bajar)
        self.ActualizarDatos = QtWidgets.QPushButton(self.pageRuta)
        self.ActualizarDatos.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.ActualizarDatos.setMinimumSize(QtCore.QSize(115, 0))
        self.ActualizarDatos.setObjectName("ActualizarDatos")
        self.horizontalLayout.addWidget(self.ActualizarDatos)
        self.GuardaDatos = QtWidgets.QPushButton(self.pageRuta)
        self.GuardaDatos.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.GuardaDatos.setMinimumSize(QtCore.QSize(100, 0))
        self.GuardaDatos.setObjectName("GuardaDatos")
        self.horizontalLayout.addWidget(self.GuardaDatos)
        self.verticalLayout_9.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_3 = QtWidgets.QLabel(self.pageRuta)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_8.addWidget(self.label_3)
        self.IndexList = QtWidgets.QListWidget(self.pageRuta)
        self.IndexList.setMaximumSize(QtCore.QSize(12000000, 16777215))
        self.IndexList.setObjectName("IndexList")
        self.verticalLayout_8.addWidget(self.IndexList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_8)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label = QtWidgets.QLabel(self.pageRuta)
        self.label.setObjectName("label")
        self.verticalLayout_7.addWidget(self.label)
        self.LatitudList = QtWidgets.QListWidget(self.pageRuta)
        self.LatitudList.setMaximumSize(QtCore.QSize(12000000, 12000000))
        self.LatitudList.setObjectName("LatitudList")
        self.verticalLayout_7.addWidget(self.LatitudList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_7)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_2 = QtWidgets.QLabel(self.pageRuta)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_6.addWidget(self.label_2)
        self.LongitudList = QtWidgets.QListWidget(self.pageRuta)
        self.LongitudList.setMaximumSize(QtCore.QSize(12000000, 12000000))
        self.LongitudList.setObjectName("LongitudList")
        self.verticalLayout_6.addWidget(self.LongitudList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.verticalLayout_9.addLayout(self.horizontalLayout_2)
        self.stackedWidget.addWidget(self.pageRuta)
        self.pageMetricas = QtWidgets.QWidget()
        self.pageMetricas.setObjectName("pageMetricas")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.pageMetricas)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.widget_2 = QtWidgets.QWidget(self.pageMetricas)
        self.widget_2.setObjectName("widget_2")
        self.metri3 = QtWidgets.QLabel(self.widget_2)
        self.metri3.setGeometry(QtCore.QRect(0, 0, 118, 421))
        self.metri3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.metri3.setText("")
        self.metri3.setPixmap(QtGui.QPixmap(".\\img/Untitled-3.png"))
        self.metri3.setObjectName("metri3")

        global PunteroAltura
        PunteroAltura = QtWidgets.QLabel(self.widget_2)
        PunteroAltura.setGeometry(QtCore.QRect(90, 400, 70, 20))
        PunteroAltura.setText("")
        PunteroAltura.setPixmap(QtGui.QPixmap(".\\img/Untitled-4.png"))
        PunteroAltura.setObjectName("PunteroAltura")

        self.verticalLayout_13.addWidget(self.widget_2)

        global metri4
        metri4 = QtWidgets.QLabel(self.pageMetricas)
        metri4.setMaximumSize(QtCore.QSize(16777215, 20))
        metri4.setObjectName("metri4")
        self.verticalLayout_13.addWidget(metri4)

        self.horizontalLayout_4.addLayout(self.verticalLayout_13)
        self.verticalLayout_17 = QtWidgets.QVBoxLayout()
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.widget_3 = QtWidgets.QWidget(self.pageMetricas)
        self.widget_3.setObjectName("widget_3")
        self.label_4 = QtWidgets.QLabel(self.widget_3)
        self.label_4.setGeometry(QtCore.QRect(5, 0, 190, 190))
        self.label_4.setMouseTracking(False)
        self.label_4.setStyleSheet("")
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(".\\img/Heading_indicator.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")

        global Brujula
        Brujula = QtWidgets.QLabel(self.widget_3)
        Brujula.setGeometry(QtCore.QRect(5, 4, 190, 190))
        Brujula.setText("")
        Brujula.setPixmap(QtGui.QPixmap(".\\img/Untitled-7.png"))
        Brujula.setScaledContents(True)
        Brujula.setObjectName("Brujula")

        self.verticalLayout_14.addWidget(self.widget_3)

        global metri7
        metri7 = QtWidgets.QLabel(self.pageMetricas)
        metri7.setMaximumSize(QtCore.QSize(16777215, 30))
        metri7.setAlignment(QtCore.Qt.AlignCenter)
        metri7.setObjectName("metri7")
        self.verticalLayout_14.addWidget(metri7)

        self.verticalLayout_17.addLayout(self.verticalLayout_14)
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.widget_4 = QtWidgets.QWidget(self.pageMetricas)
        self.widget_4.setObjectName("widget_4")
        self.label_8 = QtWidgets.QLabel(self.widget_4)
        self.label_8.setGeometry(QtCore.QRect(5, 0, 190, 190))
        self.label_8.setText("")
        self.label_8.setPixmap(QtGui.QPixmap(".\\img/Untitled-9.png"))
        self.label_8.setScaledContents(True)
        self.label_8.setObjectName("label_8")

        global HorizonteArt
        HorizonteArt = QtWidgets.QLabel(self.widget_4)
        HorizonteArt.setGeometry(QtCore.QRect(5, 0, 190, 190))
        HorizonteArt.setText("")
        HorizonteArt.setPixmap(QtGui.QPixmap(".\\img/Untitled-8.png"))
        HorizonteArt.setScaledContents(True)
        HorizonteArt.setObjectName("HorizonteArt")

        self.label_10 = QtWidgets.QLabel(self.widget_4)
        self.label_10.setGeometry(QtCore.QRect(5, 6, 190, 190))
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap(".\\img/Attitude_indicator_level_flight.png"))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_15.addWidget(self.widget_4)

        global metri5
        metri5 = QtWidgets.QLabel(self.pageMetricas)
        metri5.setMaximumSize(QtCore.QSize(16777215, 30))
        metri5.setAlignment(QtCore.Qt.AlignCenter)
        metri5.setObjectName("metri5")
        self.verticalLayout_15.addWidget(metri5)

        self.verticalLayout_17.addLayout(self.verticalLayout_15)
        self.horizontalLayout_4.addLayout(self.verticalLayout_17)
        self.verticalLayout_16 = QtWidgets.QVBoxLayout()
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.widget_5 = QtWidgets.QWidget(self.pageMetricas)
        self.widget_5.setObjectName("widget_5")
        self.label_11 = QtWidgets.QLabel(self.widget_5)
        self.label_11.setGeometry(QtCore.QRect(5, 0, 190, 190))
        self.label_11.setMouseTracking(False)
        self.label_11.setStyleSheet("")
        self.label_11.setText("")
        self.label_11.setPixmap(QtGui.QPixmap(".\\img/aircraft-36298.png"))
        self.label_11.setScaledContents(True)
        self.label_11.setObjectName("label_11")

        global Velocidad
        Velocidad = QtWidgets.QLabel(self.widget_5)
        Velocidad.setGeometry(QtCore.QRect(5, 0, 190, 190))
        Velocidad.setText("")
        Velocidad.setPixmap(QtGui.QPixmap(".\\img/Untitled-10.png"))
        Velocidad.setScaledContents(True)
        Velocidad.setObjectName("Velocidad")

        global Temperatura
        Temperatura = QtWidgets.QLabel(self.widget_5)
        Temperatura.setGeometry(QtCore.QRect(76, 12, 47, 13))
        Temperatura.setAlignment(QtCore.Qt.AlignCenter)
        Temperatura.setObjectName("Temperatura")

        self.verticalLayout_12.addWidget(self.widget_5)

        global metri8
        metri8 = QtWidgets.QLabel(self.pageMetricas)
        metri8.setMaximumSize(QtCore.QSize(16777215, 30))
        metri8.setAlignment(QtCore.Qt.AlignCenter)
        metri8.setObjectName("metri8")
        self.verticalLayout_12.addWidget(metri8)

        self.verticalLayout_16.addLayout(self.verticalLayout_12)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.widget_6 = QtWidgets.QWidget(self.pageMetricas)
        self.widget_6.setObjectName("widget_6")
        self.label_21 = QtWidgets.QLabel(self.widget_6)
        self.label_21.setGeometry(QtCore.QRect(5, 0, 190, 190))
        self.label_21.setMouseTracking(False)
        self.label_21.setStyleSheet("")
        self.label_21.setText("")
        self.label_21.setPixmap(QtGui.QPixmap(".\\img/istockphoto-546787274-612x612.png"))
        self.label_21.setScaledContents(True)
        self.label_21.setObjectName("label_21")

        global Presion
        Presion = QtWidgets.QLabel(self.widget_6)
        Presion.setGeometry(QtCore.QRect(5, 0, 190, 190))
        Presion.setText("")
        Presion.setPixmap(QtGui.QPixmap(".\\img/Untitled-11.png"))
        Presion.setScaledContents(True)
        Presion.setObjectName("Presion")

        self.verticalLayout_10.addWidget(self.widget_6)

        global metri3_2
        metri3_2 = QtWidgets.QLabel(self.pageMetricas)
        metri3_2.setMaximumSize(QtCore.QSize(16777215, 30))
        metri3_2.setAlignment(QtCore.Qt.AlignCenter)
        metri3_2.setObjectName("metri3_2")
        self.verticalLayout_10.addWidget(metri3_2)

        self.verticalLayout_16.addLayout(self.verticalLayout_10)
        self.horizontalLayout_4.addLayout(self.verticalLayout_16)
        self.stackedWidget.addWidget(self.pageMetricas)
        self.pageGraficas = QtWidgets.QWidget()
        self.pageGraficas.setObjectName("pageGraficas")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout(self.pageGraficas)
        self.verticalLayout_18.setObjectName("verticalLayout_18")

        global plot_graph
        plot_graph = pg.PlotWidget()
        plot_graph.setBackground("#F0F0F0")
        pen = pg.mkPen(color=(255, 0, 0), width=2)
        time = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        plot_graph.plot(time, temperature, pen=pen, symbol="h", symbolSize=10)
        plot_graph.setLabel(
            "left",
            '<span style="font-size: 12px">Altitud (m)</span>'
        )
        plot_graph.setLabel(
            "bottom",
            '<span style="font-size: 12px">Tiempo (s)</span>'
        )
        plot_graph.showGrid(x=True, y=True)

        self.verticalLayout_18.addWidget(plot_graph)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.pushButton_6 = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton_6)
        self.pushButton = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton_4)
        self.pushButton_5 = QtWidgets.QPushButton(self.pageGraficas)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setStyleSheet('border: 1.5px solid #db5d4f; padding: 5px')

        self.horizontalLayout_6.addWidget(self.pushButton_5)
        self.verticalLayout_18.addLayout(self.horizontalLayout_6)
        self.stackedWidget.addWidget(self.pageGraficas)
        self.pageModelo = QtWidgets.QWidget()
        self.pageModelo.setObjectName("pageModelo")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.pageModelo)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        # self.openGLWidget = QtWidgets.QOpenGLWidget(self.pageModelo)
        # self.openGLWidget.setObjectName("openGLWidget")
        #===================================================================================

        view = GLViewWidget(rotationMethod='quaternion')
        view.setBackgroundColor(240,240,240, 0)
        view.setCameraPosition(distance=500) 
        view.pan(0, 0, 0) 
        view.opts['panning'] = False 
        view.opts['rotationMode'] = 'cube'
        stl_mesh = mesh.Mesh.from_file('plane.STL')
        points = stl_mesh.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        mesh_data = MeshData(vertexes=points, faces=faces)
        global meshIem
        meshIem = GLMeshItem(meshdata=mesh_data, drawFaces=False, drawEdges=True, edgeColor=(1, 0.4, 0.2, 1))
        view.addItem(meshIem)
        # view.show()
        worker_thread = WorkerThread()
        worker_thread.start()
        self.horizontalLayout_3.addWidget(view)

        #===================================================================================

        # self.horizontalLayout_3.addWidget(self.openGLWidget)
        self.stackedWidget.addWidget(self.pageModelo)
        self.verticalLayout_5.addWidget(self.stackedWidget)
        self.horizontalLayout_5.addWidget(self.Content)
        MainWindow.setCentralWidget(self.centralwidget)

        for i in self.marker_coord:
            self.LatitudList.insertItem(0,str(i[0]))
            self.LongitudList.insertItem(0,str(i[1]))
            self.IndexList.insertItem(0,str(i[2]))

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)
        self.LatitudList.setCurrentRow(-1)
        self.Metricas2.toggled['bool'].connect(self.Metricas1.setChecked) # type: ignore
        self.Modelo2.toggled['bool'].connect(self.Modelo1.setChecked) # type: ignore
        self.Metricas1.toggled['bool'].connect(self.Metricas2.setChecked) # type: ignore
        self.Ruta1.toggled['bool'].connect(self.Ruta2.setChecked) # type: ignore
        self.Ruta2.toggled['bool'].connect(self.Ruta1.setChecked) # type: ignore
        self.Modelo1.toggled['bool'].connect(self.Modelo2.setChecked) # type: ignore
        self.Menu.toggled['bool'].connect(self.iconOnly.setVisible) # type: ignore
        self.Menu.toggled['bool'].connect(self.fullMenu.setHidden) # type: ignore
        self.Graficas.toggled['bool'].connect(self.Graficas2.setChecked) # type: ignore
        self.Graficas2.toggled['bool'].connect(self.Graficas.setChecked) # type: ignore
        self.Retorno2.toggled['bool'].connect(self.Retorno.setChecked) # type: ignore
        self.Retorno.toggled['bool'].connect(self.Retorno2.setChecked) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Ruta2.setText(_translate("MainWindow", "     Ruta"))
        self.Modelo2.setText(_translate("MainWindow", " Metricas"))
        self.Metricas2.setText(_translate("MainWindow", "  Modelo"))
        self.Graficas2.setText(_translate("MainWindow", " Graficas"))
        self.Retorno2.setText(_translate("MainWindow", " Retorno"))
        self.AgregarParada.setText(_translate("MainWindow", "Agregar"))
        self.EditarParada.setText(_translate("MainWindow", "Editar"))
        self.EliminarParada.setText(_translate("MainWindow", "Eliminar"))
        self.Subir.setText(_translate("MainWindow", "Subir"))
        self.Bajar.setText(_translate("MainWindow", "Bajar"))
        self.ActualizarDatos.setText(_translate("MainWindow", "Actualizar Pocision"))
        self.GuardaDatos.setText(_translate("MainWindow", "Guardar Datos"))
        self.label_3.setText(_translate("MainWindow", "Elemento:"))
        self.label.setText(_translate("MainWindow", "Latitud:"))
        self.label_2.setText(_translate("MainWindow", "Longitud:"))
        metri4.setText(_translate("MainWindow", "Altura ()"))
        metri7.setText(_translate("MainWindow", "Brujula ()"))
        metri5.setText(_translate("MainWindow", "Horizonte artificial (,)"))
        Temperatura.setText(_translate("MainWindow", "0.0"))
        metri8.setText(_translate("MainWindow", "Anometro ()"))
        metri3_2.setText(_translate("MainWindow", "Presion manifold ()"))
        self.pushButton_6.setText(_translate("MainWindow", "Yaw"))
        self.pushButton.setText(_translate("MainWindow", "Pitch y Roll"))
        self.pushButton_2.setText(_translate("MainWindow", "Altitud"))
        self.pushButton_3.setText(_translate("MainWindow", "Temperatura"))
        self.pushButton_4.setText(_translate("MainWindow", "Presión"))
        self.pushButton_5.setText(_translate("MainWindow", "Velocidad"))

    def ActualizarPosicion(self):
        print(lat, lon)
        item1 = self.LatitudList.item(len(self.LatitudList)-1)
        item2 = self.LongitudList.item(len(self.LongitudList)-1)
        item3 = self.IndexList.item(len(self.IndexList)-1)
        item1.setText(lat)
        item2.setText(lon)
        item3.setText(item3.text())