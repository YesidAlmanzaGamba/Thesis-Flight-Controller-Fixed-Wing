import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtCore import QProcess
import serial_comm as my_serial

class Ventana(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Selecciona el puerto que quieres utilizar: ')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.lista_numeros = QListWidget()
        self.lista_numeros.addItems([x[0] for x in my_serial.SerialObj.get_ports()])

        self.boton_seleccionar = QPushButton('Seleccionar')
        self.boton_seleccionar.clicked.connect(self.abrir_segunda_app)

        layout.addWidget(self.lista_numeros)
        layout.addWidget(self.boton_seleccionar)

        self.setLayout(layout)

    def abrir_segunda_app(self):
        items_seleccionados = self.lista_numeros.selectedItems()
        if items_seleccionados:
            numero_seleccionado = items_seleccionados[0].text()
            self.ejecutar_segunda_app(numero_seleccionado)
            self.close()

    def ejecutar_segunda_app(self, numero):
        segunda_app = QProcess()
        segunda_app.startDetached(sys.executable, ['FullApp.py', numero])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec_())