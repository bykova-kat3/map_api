import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self, req):
        super().__init__()
        self.getImage(self.resp(req))
        self.initUI()

    def getImage(self, apiinf):
        response = requests.get(apiinf[0], params=apiinf[1])
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        # Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def resp(self, reqw):
        toponym_to_find = reqw

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
        toponym_lc = toponym["boundedBy"]["Envelope"]["lowerCorner"]
        toponym_uc = toponym["boundedBy"]["Envelope"]["upperCorner"]
        map_params = {
            "ll": ",".join([toponym_longitude, toponym_lattitude]),
            "spn": ",".join([str(float(toponym_uc.split()[0]) - float(toponym_lc.split()[0])),
                             str(float(toponym_uc.split()[1]) - float(toponym_lc.split()[1]))]),
            "l": "map"
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        return map_api_server, map_params


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example(input('Введите адрес '))
    ex.show()
    sys.exit(app.exec())
