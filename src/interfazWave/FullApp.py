import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import io
import geocoder
import re
from AppFromPyQt import Ui_MainWindow
# from test import Ui_MainWindow
from math import radians, cos, sin, asin, sqrt
from folium import plugins
import json


latVery = r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$'
lonVery = r'^[-+]?((1[0-7]|[1-9])?\d(\.\d+)?|180(\.0+)?)$'


def calcularDistancia(arr: list)->float:
    """
    La funcion devuelve la distancia en Kilometros entre los las cordenadas dentro del array
    """
    dis = 0
    r = 6357
    for index, i in enumerate(arr):
        if(index == len(arr)-1):
            break
        lat1, lon1, lat2, lon2 = map(radians, [arr[index][0], arr[index][1], arr[index+1][0], arr[index+1][1]])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        dis += c * r
    if len(arr) > 0:
        lat1, lon1, lat2, lon2 = map(radians, [arr[-1][0], arr[-1][1], arr[0][0], arr[0][1]])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        dis += c * r
    return dis

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #Se cargan las variables del arrchivo test.py
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        #Se inicializa el menu de la app
        self.ui.iconOnly.hide()
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.Ruta1.setChecked(True)
        self.ui.Ruta2.setChecked(True)
        # self.ui.Menu.setChecked(True)

        #Aqui se generan las acciones de los botones
        self.ui.AgregarParada.clicked.connect(self.AgregarCords)
        self.ui.EditarParada.clicked.connect(self.EditarCords)
        self.ui.EliminarParada.clicked.connect(self.EliminarParada)
        self.ui.Subir.clicked.connect(self.upThing)
        self.ui.Bajar.clicked.connect(self.downThing)
        self.ui.GuardaDatos.clicked.connect(self.SaveData)
        self.ui.ActualizarDatos.clicked.connect(self.ui.ActualizarPosicion)



        # self.ui.pushButton_6.clicked.connect(self.ui.Grafica1)
        # self.ui.pushButton.clicked.connect(self.ui.Grafica2)
        # self.ui.pushButton_2.clicked.connect(self.ui.Grafica3)
        # self.ui.pushButton_3.clicked.connect(self.ui.Grafica4)
        # self.ui.pushButton_4.clicked.connect(self.ui.Grafica5)
        # self.ui.pushButton_5.clicked.connect(self.ui.Grafica6)
        # self.ui.pushButton_19.clicked.connect(self.ui.Grafica19)


        #Aqui se sincroniza la seleccion de las dos listas
        self.ui.LatitudList.currentRowChanged.connect(self.sync_lists1)
        self.ui.LongitudList.currentRowChanged.connect(self.sync_lists2)
        self.ui.IndexList.currentRowChanged.connect(self.sync_lists3)


        #Aqui se detectan los cambios de la lista
        self.ui.LatitudList.model().rowsRemoved.connect(self.on_rowsChange)
        self.ui.LatitudList.model().rowsInserted.connect(self.on_rowsChange)
        self.ui.LatitudList.itemChanged.connect(self.on_rowsChange)

        self.ui.IndexList.model().rowsRemoved.connect(self.on_rowsChange)
        self.ui.IndexList.model().rowsInserted.connect(self.on_rowsChange)
        self.ui.IndexList.itemChanged.connect(self.on_rowsChange)

        self.ui.LongitudList.model().rowsRemoved.connect(self.on_rowsChange)
        self.ui.LongitudList.model().rowsInserted.connect(self.on_rowsChange)
        self.ui.LongitudList.itemChanged.connect(self.on_rowsChange)


    def on_stackedWidget_currentChanged(self, index):
        btn_list = self.ui.verticalLayout_2.findChildren(QPushButton) \
                    + self.ui.verticalLayout.findChildren(QPushButton)
        
        for btn in btn_list:
            if index in [5, 6]:
                btn.setAutoExclusive(False)
                btn.setChecked(False)
            else:
                btn.setAutoExclusive(True)
            
    ## functions for changing menu page
    def on_Ruta2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def on_Ruta1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def on_Modelo2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_Modelo1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)

    def on_Metricas1_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_Metricas2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_Graficas2_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_Graficas_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
    
    #Paradas ======================================
        
    def on_rowsChange(self):
        # m = folium.Map(
        # title='coastlines',
        # zoom_start=100)
        h = []
        lati = [(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())]
        longi = [(self.ui.LongitudList.item(i).text()) for i in range(self.ui.LongitudList.count())]
        indexi = [(self.ui.IndexList.item(i).text()) for i in range(self.ui.IndexList.count())]
        for index, i in enumerate(lati):
            h.insert(0, [float(lati[index]), float(longi[index]), indexi[index]])
        self.ui.marker_coord = h

        data = io.BytesIO()
        g = geocoder.ip('me')
        coordinates = g.latlng
        if len(self.ui.marker_coord) > 0 :
            m = folium.Map(location=[self.ui.marker_coord[0][0],self.ui.marker_coord[0][1]], zoom_start=50)
            # tiles='Cartodb dark_matter'
        elif coordinates is not None:
            latitude, longitude = coordinates
            m = folium.Map(location=[latitude, longitude], zoom_start=50)
        else:
            m = folium.Map(location=[4.7086033306706145, -74.06116161374081], zoom_start=50)
        marker_radius = 20
        #Mapa
        # justMarks = []
        # for i in self.marker_coord:
        #     justMarks.append([i[0], i[0]])
        for index, i in enumerate(self.ui.marker_coord):
            if(index == 0):
                folium.Marker(
                    location = [i[0], i[1]],
                    icon = folium.Icon(color='black', icon='home'),
                    tooltip=f'{i[2]}',
                    ).add_to(m)
            else:
                folium.vector_layers.Circle(
                location=[i[0], i[1]],
                tooltip=f"Radio de {marker_radius} metros",
                radius=marker_radius,
                color="red",
                fill=True,
                fill_color="blue"
                    ).add_to(m)
                folium.Marker(
                    location = [i[0], i[1]],
                    icon = folium.Icon(color='red'),
                    tooltip=f'Punto de control: {i[2]}',
                    ).add_to(m)
            if(index < len(self.ui.marker_coord)-1):
                folium.PolyLine(
                    [[self.ui.marker_coord[index][0],self.ui.marker_coord[index][1]], [self.ui.marker_coord[index+1][0],self.ui.marker_coord[index+1][1]]],
                    tooltip=f"Trayecto: {self.ui.marker_coord[index][2]} --> {self.ui.marker_coord[index+1][2]}",
                    color= 'black',
                    weight= 10,
                    opacity= 0.5
                ).add_to(m)
            #lines
        if(len(self.ui.marker_coord) > 2):
            folium.PolyLine(
                [[self.ui.marker_coord[0][0],self.ui.marker_coord[0][1]], [self.ui.marker_coord[-1][0],self.ui.marker_coord[-1][1]]],
                tooltip='Trayectoria de regreso',
                color= 'red',
                weight= 10,
                opacity= 0.5
            ).add_to(m)
        elif(len(self.ui.marker_coord) == 2):
                folium.PolyLine(
                [[self.ui.marker_coord[0][0],self.ui.marker_coord[0][1]], [self.ui.marker_coord[-1][0],self.ui.marker_coord[-1][1]]],
                tooltip='Trayectoria de ida y vuelta',
                color= 'purple',
                weight= 10,
                opacity= 0.5
            ).add_to(m)
                
        roundnum = "function(num) {return L.Util.formatNum(num, 5);};"
        folium.plugins.LocateControl().add_to(m)

        plugins.MousePosition(position='topright', separator=' | ', prefix="Position:",lat_formatter=roundnum, lng_formatter=roundnum).add_to(self.ui.m)
        m.add_child(folium.LatLngPopup())

        m.save(data, close_file=False)
        self.ui.webView.setHtml(data.getvalue().decode())

    def AgregarCords(self):
        dlg = QInputDialog
        indexi, ok3 = dlg.getText(self, "Agregar nombre", "Ingrese la el nombre del punto de control: ")
        latitud, ok1 = dlg.getText(self, "Agregar coordenada", "Ingrese la latitud: ")
        longitud, ok2 = dlg.getText(self, "Agregar coordenada", "Ingrese la longitud: ")
        if ok1 and ok2 and (re.match(latVery, latitud) and re.match(lonVery,longitud)) and ok3:
            self.ui.LongitudList.insertItem(0,longitud)
            self.ui.IndexList.insertItem(0,indexi)
            self.ui.LatitudList.insertItem(0,latitud)
            h = []
            lati = [(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())]
            longi = [(self.ui.LongitudList.item(i).text()) for i in range(self.ui.LongitudList.count())]
            for index, i in enumerate(([(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())])):
                h.insert(0, [float(lati[index]), float(longi[index])])

            b = calcularDistancia(h)
            if (re.match(latVery, latitud) and re.match(lonVery,longitud)):
                if b > 50:
                    self.error_dialog = QErrorMessage()
                    self.error_dialog.showMessage(f'El wave no conseguira recorrer tanta distancia: {round(b, 2)}Km.')
                    item1 = self.ui.LatitudList.takeItem(0)
                    item2 = self.ui.LongitudList.takeItem(0)
                    item3 = self.ui.IndexList.takeItem(0)
                    del item1
                    del item2
                    del item3
                    
            else:
                self.error_dialog = QErrorMessage()
                self.error_dialog.showMessage('La latitud y longitud agregadas no son coordenadas validas.')
                item1 = self.ui.LatitudList.takeItem(0)
                item2 = self.ui.LongitudList.takeItem(0)
                item3 = self.ui.IndexList.takeItem(0)
                del item1
                del item2
                del item3
        else:
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('La latitud o longitud agregadas no son numeros.')

        
    def EditarCords(self):
        currentIndex = self.ui.LatitudList.currentRow()
        item1 = self.ui.LatitudList.item(currentIndex)
        item2 = self.ui.LongitudList.item(currentIndex)
        item3 = self.ui.IndexList.item(currentIndex)
        if item3.text() != 'Posicion En Tiempo Real':
            if item1 is not None and item2 is not None:
                oldLatitdu = item1.text()
                oldLongitud = item2.text()
                oldIndex = item3.text()
                indexi, ok3 = QInputDialog.getText(self, "Editar coordenada", "Ingrese el nuevo nombre del punto de control: ", QLineEdit.Normal, item3.text())
                latitud, ok1 = QInputDialog.getText(self, "Editar coordenada", "Ingrese la nueva latitud: ", QLineEdit.Normal, item1.text())
                longitud, ok2 = QInputDialog.getText(self, "Editar coordenada", "Ingrese la nueva longitud: ", QLineEdit.Normal, item2.text())
                if ok1 and ok2 and (re.match(latVery, latitud) and re.match(lonVery,longitud)) and ok3:
                    item1.setText(latitud)
                    item2.setText(longitud)
                    item3.setText(indexi)
                    h = []
                    lati = [(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())]
                    longi = [(self.ui.LongitudList.item(i).text()) for i in range(self.ui.LongitudList.count())]
                    for index, i in enumerate(([(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())])):
                        h.insert(0, [float(lati[index]), float(longi[index])])
                    b = calcularDistancia(h)
                    if (re.match(latVery, latitud) and re.match(lonVery,longitud)):
                        if b > 50:
                            self.error_dialog = QErrorMessage()
                            self.error_dialog.showMessage(f'El wave no conseguira recorrer tanta distancia: {round(b, 2)}Km.')
                            item1.setText(oldLatitdu)
                            item2.setText(oldLongitud)      
                            item3.setText(oldIndex) 
                    else:
                        self.error_dialog = QErrorMessage()
                        self.error_dialog.showMessage('La latitud y longitud agregadas no son coordenadas validas.')
                        item1.setText(oldLatitdu)
                        item2.setText(oldLongitud)
                        item3.setText(oldIndex) 

                else:
                    self.error_dialog = QErrorMessage()
                    self.error_dialog.showMessage('La latitud y longitud agregadas no son numeros.')

    def EliminarParada(self):
        currentIndex = self.ui.LatitudList.currentRow()
        item1 = self.ui.LatitudList.item(currentIndex)
        item2 = self.ui.LongitudList.item(currentIndex)
        item3 = self.ui.IndexList.item(currentIndex)
        print(currentIndex)
        if item1 is None or item2 is None or item3 is None or item3.text() == 'Posicion En Tiempo Real':
            return
        question = QMessageBox.question(self, 'Eliminar parada', 'Seguro de eliminar el punto de control "' + str(item3.text()) + '"?', QMessageBox.Yes | QMessageBox.No)

        if question == QMessageBox.Yes:
            item1 = self.ui.LatitudList.takeItem(currentIndex)
            item2 = self.ui.LongitudList.takeItem(currentIndex)
            item3 = self.ui.IndexList.takeItem(currentIndex)
            del item1
            del item2
            del item3


    def sync_lists1(self, row):
        self.ui.IndexList.setCurrentRow(row)
        self.ui.LongitudList.setCurrentRow(row)
    def sync_lists2(self, row):
        self.ui.LatitudList.setCurrentRow(row)
        self.ui.IndexList.setCurrentRow(row)
    def sync_lists3(self, row):
        self.ui.LatitudList.setCurrentRow(row)
        self.ui.LongitudList.setCurrentRow(row)

    def upThing(self):
        currentIndex = self.ui.LongitudList.currentRow()
        if currentIndex > 0 and currentIndex != self.ui.LatitudList.count()-1:
            item1 = self.ui.LatitudList.takeItem(currentIndex)
            item2 = self.ui.LongitudList.takeItem(currentIndex)
            item3 = self.ui.IndexList.takeItem(currentIndex)
            self.ui.LongitudList.insertItem(currentIndex-1,item2)
            self.ui.IndexList.insertItem(currentIndex-1,item3)
            self.ui.LatitudList.insertItem(currentIndex-1,item1)

            self.ui.LongitudList.setCurrentItem(item2)
    def downThing(self):
        currentIndex = self.ui.LongitudList.currentRow()
        if currentIndex < self.ui.LatitudList.count()-2 and currentIndex != self.ui.LatitudList.count()-1:
            item1 = self.ui.LatitudList.takeItem(currentIndex)
            item2 = self.ui.LongitudList.takeItem(currentIndex)
            item3 = self.ui.IndexList.takeItem(currentIndex)
            self.ui.LongitudList.insertItem(currentIndex+1,item2)
            self.ui.IndexList.insertItem(currentIndex+1,item3)
            self.ui.LatitudList.insertItem(currentIndex+1,item1)

            self.ui.LongitudList.setCurrentItem(item2)
    def SaveData(self):
        h = []
        lati = [(self.ui.LatitudList.item(i).text()) for i in range(self.ui.LatitudList.count())]
        longi = [(self.ui.LongitudList.item(i).text()) for i in range(self.ui.LongitudList.count())]
        indexi = [(self.ui.IndexList.item(i).text()) for i in range(self.ui.IndexList.count())]
        for index, i in enumerate(lati):
            h.insert(0, [float(lati[index]), float(longi[index]), indexi[index]])
        self.ui.marker_coord = h
        json_object = json.dumps(h)
        with open("./datosGuardados/currentData.json", "w") as outfile:
            outfile.write(json_object)
        msg = QMessageBox()
        # msg.setWindowTitle("Tutorial on PyQt5")
        msg.setText("La ruta fue guardada.")
        x = msg.exec_()
   

def App():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

App()