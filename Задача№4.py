import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from qtpy import QtCore

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self, req):
        super().__init__()
        self.spn1 = 0
        self.spn2 = 0
        self.l = 'map'
        self.s = 0
        self.address = req
        self.getImage(self.response(req))
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.pixmap = QPixmap(self.getImage(self.response(self.address)))
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)
        self.btn = QPushButton(self.l, self)
        self.btn.resize(100, 50)
        self.btn.move(500, 400)
        self.btn.clicked.connect(self.layer)

    def getImage(self, apiinf):
        response = requests.get(apiinf[0], params=apiinf[1])
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        return map_file

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.spn2 += float(self.spn()[1])

        if event.key() == QtCore.Qt.Key_Down:
            self.spn2 += (float(self.spn()[1]) * (-1))

        if event.key() == QtCore.Qt.Key_Right:
            self.spn1 += float(self.spn()[0])

        if event.key() == QtCore.Qt.Key_Left:
            self.spn1 += (float(self.spn()[0]) * (-1))

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
        self.toponym_lc = toponym["boundedBy"]["Envelope"]["lowerCorner"]
        self.toponym_uc = toponym["boundedBy"]["Envelope"]["upperCorner"]
        map_params = {
            "ll": ",".join([str(float(toponym_longitude) + self.spn1), str(float(toponym_lattitude) + self.spn2)]),
            "spn": ",".join(self.spn()),
            "l": self.l
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        return map_api_server, map_params

    def spn(self):
        return [str(float(self.toponym_uc.split()[0]) - float(self.toponym_lc.split()[0])), str(
            float(self.toponym_uc.split()[1]) - float(self.toponym_lc.split()[1]))]

    def layer(self):
        self.s += 1
        if self.s > 2:
            self.s = 0
        self.l = ["map", "sat", "sat,skl"][self.s]
        self.btn.setText(self.l)
        self.image.setPixmap(QPixmap(self.getImage(self.response(self.address))))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example(input('Введите адрес '))
    ex.show()
    sys.exit(app.exec())
