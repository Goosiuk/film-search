import sys
import sqlite3
from pathlib import Path
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTableView
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel


BASE_DIR = Path(__file__).resolve().parent


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle("Поиск любимых фильмов")
        self.resize(600, 450)

        self.window1 = Search()
        self.window2 = Table("Список любимых фильмов", 'films_love.sqlite')
        self.window3 = Table("Список рекомендованных фильмов", 'films_recomendations.sqlite')

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.button1 = QtWidgets.QPushButton(self.centralwidget)
        self.button1.setGeometry(QtCore.QRect(215, 390, 170, 35))
        self.button1.setObjectName("button1")

        self.button2 = QtWidgets.QPushButton(self.centralwidget)
        self.button2.setGeometry(QtCore.QRect(420, 390, 170, 35))
        self.button2.setObjectName("button2")

        self.button3 = QtWidgets.QPushButton(self.centralwidget)
        self.button3.setGeometry(QtCore.QRect(10, 390, 170, 35))
        self.button3.setObjectName("button3")

        label = QLabel(self)
        pixmap = QPixmap(str(BASE_DIR / 'img.png'))
        label.setPixmap(pixmap)
        label.resize(600, 375)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 311, 26))
        self.menubar.setObjectName("menubar")

        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslatemain()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.button1.clicked.connect(lambda checked: self.toggle_window(self.window1))
        self.button2.clicked.connect(lambda checked: self.toggle_window(self.window2))
        self.button3.clicked.connect(lambda checked: self.toggle_window(self.window3))

    def retranslatemain(self):
        _translate = QtCore.QCoreApplication.translate
        self.button1.setText(_translate("MainWindow", "Поиск фильмов"))
        self.button2.setText(_translate("MainWindow", "Любимые фильмы"))
        self.button3.setText(_translate("MainWindow", "Рекомендованные фильмы"))

    def toggle_window(self, window):
        if window.isVisible():
            window.hide()

        else:
            if hasattr(window, "refresh"):
                window.refresh()
            window.show()


class Search(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search")
        self.resize(590, 245)

        self.button_search = QtWidgets.QPushButton(self)
        self.button_search.setGeometry(QtCore.QRect(410, 170, 141, 31))
        self.button_search.setObjectName("button_search")

        add = QVBoxLayout()
        self.button_search.clicked.connect(lambda checked: self.search_bd())
        add.addWidget(self.button_search)

        self.button_duration = QtWidgets.QLineEdit(self)
        self.button_duration.setGeometry(QtCore.QRect(30, 170, 251, 31))
        self.button_duration.setObjectName("button_duration")

        self.label_duration = QtWidgets.QLabel(self)
        self.label_duration.setGeometry(QtCore.QRect(30, 130, 271, 31))
        self.label_duration.setObjectName("label_duration")

        self.button_year = QtWidgets.QLineEdit(self)
        self.button_year.setGeometry(QtCore.QRect(390, 70, 161, 31))
        self.button_year.setObjectName("button_year")

        self.label_year = QtWidgets.QLabel(self)
        self.label_year.setGeometry(QtCore.QRect(390, 30, 111, 31))
        self.label_year.setObjectName("label_year")

        self.button_name = QtWidgets.QLineEdit(self)
        self.button_name.setGeometry(QtCore.QRect(210, 70, 161, 31))
        self.button_name.setObjectName("button_name")

        self.label_name = QtWidgets.QLabel(self)
        self.label_name.setGeometry(QtCore.QRect(210, 30, 141, 31))
        self.label_name.setObjectName("label_name")

        self.button_genre = QtWidgets.QLineEdit(self)
        self.button_genre.setGeometry(QtCore.QRect(30, 70, 161, 31))
        self.button_genre.setObjectName("button_genre")

        self.label_genre = QtWidgets.QLabel(self)
        self.label_genre.setGeometry(QtCore.QRect(30, 30, 131, 31))
        self.label_genre.setObjectName("label_genre")

        for field in (self.button_name, self.button_genre, self.button_year, self.button_duration):
            field.returnPressed.connect(self.search_bd)

        self.retranslateui()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.name = self.button_name.text()
        self.genre = self.button_genre.text()
        self.year = self.button_year.text()
        self.duration = self.button_duration.text()

    def out(self):
        self.name = self.button_name.text().strip()
        self.genre = self.button_genre.text().strip()
        self.year = self.button_year.text().strip()
        self.duration = self.button_duration.text().strip()
        return self.name, self.genre, self.year, self.duration

    def retranslateui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Search", "Поиск фильмов"))
        self.button_search.setText(_translate("Search", "Найти"))
        self.label_year.setText(_translate("Search", "Введите год:"))
        self.label_name.setText(_translate("Search", "Введите название:"))
        self.label_genre.setText(_translate("Search", "Введите жанр:"))
        self.label_duration.setText(_translate("Search", "Введите примерную продолжительность:"))

    def toggle_window(self, window):
        if window.isVisible():
            window.hide()
        else:
            window.show()

    def search_bd(self):

        name, genre, year, duration = self.out()
        con = sqlite3.connect(BASE_DIR / "films_db.sqlite")
        cur = con.cursor()
        if name != '':
            cur.execute("""SELECT * FROM films WHERE title = ?""", (name,))

        elif genre != '' and year != '' and duration != '':
            cur.execute("""SELECT * FROM films WHERE genre=(SELECT id FROM genres WHERE title = ?) 
            and year = ? and duration = ?""", (genre, year, duration))

        elif genre != '' and duration != '':
            cur.execute("""SELECT * FROM films WHERE genre=(SELECT id FROM genres WHERE title = ?) 
            and duration = ?""", (genre, duration))

        elif year != '' and duration != '':
            cur.execute("""SELECT * FROM films WHERE year = ? and duration = ?""", (year, duration))

        elif genre != '' and year != '':
            cur.execute("""SELECT * FROM films WHERE genre=(SELECT id FROM genres WHERE title = ?) 
            and year = ?""", (genre, year))

        elif genre != '':
            cur.execute("""SELECT * FROM films WHERE genre=(SELECT id FROM genres WHERE title = ?)""", (genre,))

        elif year != '':
            cur.execute("""SELECT * FROM films WHERE year = ?""", (year,))

        elif duration != '':
            cur.execute("""SELECT * FROM films WHERE duration = ?""", (duration,))

        result = cur.fetchall()

        con.commit()
        con.close()
        con = sqlite3.connect(BASE_DIR / "films_result.sqlite")
        cur = con.cursor()
        cur.execute("""DELETE from films""")
        genres = {
            1: 'комедия',
            2: 'драма',
            3: 'мелодрама',
            4: 'детектив',
            5: 'документальный',
            6: 'ужасы',
            7: 'музыка',
            8: 'фантастика',
            9: 'анимация',
            10: 'биография',
            11: 'боевик',
            13: 'приключения',
            15: 'война',
            16: 'семейный',
            17: 'триллер',
            18: 'фэнтези',
            19: 'вестерн',
            20: 'мистика',
            21: 'короткометражный',
            22: 'мюзикл',
            23: 'исторический',
            24: 'нуар'
        }

        for elem in result:
            cur.execute("""INSERT INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)""",
                        (elem[0], elem[1], elem[2], genres[elem[3]], elem[4]))
            print((elem[0], elem[1], elem[2], genres[elem[3]], elem[4]))

        con.commit()
        con.close()
        self.window = Table('Список фильмов', 'films_result.sqlite')
        self.toggle_window(self.window)


class Table(QWidget):

    def __init__(self, name, name_bd):
        self.name = name
        self.name_bd = name_bd
        super().__init__()
        if name_bd == 'films_result.sqlite':
            self.search_table()
        elif name_bd == 'films_love.sqlite':
            self.love_table()
        elif name_bd == 'films_recomendations.sqlite':
            self.recomendation_table()

    def refresh(self):
        if self.name_bd == "films_recomendations.sqlite":
            self.update_recommendations()
        self.model.select()

    def search_table(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE', f'films_{id(self)}')
        db = self.db
        db.setDatabaseName(str(BASE_DIR / self.name_bd))
        db.open()
        view = QTableView(self)
        model = QSqlTableModel(self, db)
        self.model = model
        model.setTable('films')
        model.select()

        label = QLabel(self)
        label.setText(self.name)
        label.move(10, 25)

        view.setModel(model)
        view.move(10, 70)
        view.resize(645, 300)


        self.setGeometry(300, 100, 665, 450)
        self.setWindowTitle('Найденные фильмы')

    def love_table(self):

        self.db = QSqlDatabase.addDatabase('QSQLITE', f'films_{id(self)}')
        db = self.db
        db.setDatabaseName(str(BASE_DIR / 'films_love.sqlite'))
        db.open()

        view = QTableView(self)
        model = QSqlTableModel(self, db)
        self.model = model
        model.setTable('films')
        model.select()

        label = QLabel(self)
        label.setText(self.name)
        label.move(10, 25)

        view.setModel(model)
        view.move(10, 70)
        view.resize(645, 300)

        edit_id = QLineEdit(self)
        edit_id.move(140, 400)
        edit_id.resize(55, 30)

        label_id = QLabel(self)
        label_id.setText('Введите id фильма:')
        label_id.move(10, 410)

        button_add = QPushButton(self)
        button_add.setText('Добавить')
        button_add.resize(90, 30)
        button_add.move(200, 400)
        button_add.clicked.connect(lambda checked: self.addbt(edit_id))

        button_delete = QPushButton(self)
        button_delete.setText('Удалить')
        button_delete.resize(90, 30)
        button_delete.move(295, 400)
        button_delete.clicked.connect(lambda checked: self.adddl(edit_id))


        self.setGeometry(300, 100, 665, 450)
        self.setWindowTitle('Любимые фильмы')

    def addbt(self, edit_id):
        edit_id = edit_id.text()
        con = sqlite3.connect(BASE_DIR / "films_db.sqlite")
        cur = con.cursor()
        cur.execute("""SELECT * FROM films WHERE id = ?""", (edit_id,))
        result = cur.fetchall()
        con.commit()
        con.close()

        con = sqlite3.connect(BASE_DIR / 'films_love.sqlite')
        cur = con.cursor()
        for elem in result:
            cur.execute("""INSERT OR IGNORE INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)""",
                        (elem[0], elem[1], elem[2], elem[3], elem[4]))

        con.commit()
        con.close()
        self.model.select()

    def adddl(self, edit_id):
        edit_id = edit_id.text()
        con = sqlite3.connect(BASE_DIR / 'films_love.sqlite')
        cur = con.cursor()
        cur.execute("""DELETE from films WHERE id = ?""", (edit_id,))
        con.commit()
        con.close()
        self.model.select()

    def update_recommendations(self):
        con = sqlite3.connect(BASE_DIR / "films_love.sqlite")
        cur = con.cursor()
        cur.execute("""SELECT * FROM films""")
        result = cur.fetchall()
        con.commit()
        con.close()
        years = set()
        geanrs = set()
        con = sqlite3.connect(BASE_DIR / "films_db.sqlite")
        cur = con.cursor()
        for elem in result:
            years.add(elem[2])
            geanrs.add(elem[3])
        years = list(years)
        geanrs = list(geanrs)
        films = []
        for elem_years in years:
            for elem_genres in geanrs:
                cur.execute("""SELECT * FROM films WHERE year=? and genre=?""",
                            (elem_years, elem_genres))
                result = cur.fetchall()
                films.append(result)
        con.commit()
        con.close()

        con = sqlite3.connect(BASE_DIR / "films_recomendations.sqlite")
        cur = con.cursor()
        cur.execute("""DELETE from films""")

        for sp in films:
            for elem in sp:
                cur.execute("""INSERT INTO films(id, title, year, genre, duration) VALUES(?, ?, ?, ?, ?)""",
                            (elem[0], elem[1], elem[2], elem[3], elem[4]))

        con.commit()
        con.close()

    def recomendation_table(self):
        self.update_recommendations()

        self.db = QSqlDatabase.addDatabase('QSQLITE', f'films_{id(self)}')
        db = self.db
        db.setDatabaseName(str(BASE_DIR / 'films_recomendations.sqlite'))
        db.open()

        view = QTableView(self)
        model = QSqlTableModel(self, db)
        self.model = model
        model.setTable('films')
        model.select()

        label = QLabel(self)
        label.setText(self.name)
        label.move(10, 25)

        view.setModel(model)
        view.move(10, 70)
        view.resize(645, 300)


        self.setGeometry(300, 100, 665, 450)
        self.setWindowTitle('Рекомендованные фильмы')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
