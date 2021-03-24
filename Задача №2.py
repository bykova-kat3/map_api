import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from qtpy import QtCore

SCREEN_SIZE = [600, 450]


class MainWindow(QWidget):
    def __init__(self, req):
        super().__init__()
        self.z = 10
        self.address = req
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.getImage(self.response(self.address)))
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def getImage(self, apiinf):
        response = requests.get(apiinf[0], params=apiinf[1])
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        return map_file

    def keyPressEvent(self, event):
        fl = 0
        if event.key() == QtCore.Qt.Key_PageUp:
            self.z += 1
            fl = 1
        if event.key() == QtCore.Qt.Key_PageDown:
            self.z -= 1
            fl = 1

        if self.z < 0:
            self.z = 0
        elif self.z > 17:
            self.z = 17
        else:
            fl = 1
        if fl:
            self.image.setPixmap(QPixmap(self.getImage(self.response(self.address))))

    def closeEvent(self, event):
        os.remove('map.png')

    def response(self, address):
        toponym_to_find = address
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            pass
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "l": "map",
            "z": self.z
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        return map_api_server, map_params

    sys.excepthook = lambda cls, exception, traceback: sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow(input('Введите адрес '))
    ex.show()
    sys.exit(app.exec())
