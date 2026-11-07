import gc
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5 import sip
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit

import main


class FilmSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.source = Path(main.__file__).resolve().parent

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.data = Path(self.folder.name)
        for name in ("films_db.sqlite", "films_love.sqlite", "films_result.sqlite", "films_recomendations.sqlite", "img.png"):
            shutil.copyfile(self.source / name, self.data / name)
        self.old_base = main.BASE_DIR
        self.old_cwd = Path.cwd()
        main.BASE_DIR = self.data
        self.elsewhere = self.data / "elsewhere"
        self.elsewhere.mkdir()
        os.chdir(self.elsewhere)

    def tearDown(self):
        names = []
        for widget in self.app.topLevelWidgets():
            if sip.isdeleted(widget):
                continue
            db = getattr(widget, "db", None)
            if db is not None:
                names.append(db.connectionName())
                db.close()
                widget.db = None
            del db
            widget.close()
            sip.delete(widget)
        gc.collect()
        for name in names:
            QSqlDatabase.removeDatabase(name)
        main.BASE_DIR = self.old_base
        os.chdir(self.old_cwd)
        self.folder.cleanup()

    def read_rows(self, database):
        with sqlite3.connect(self.data / database) as db:
            return db.execute("SELECT * FROM films ORDER BY id").fetchall()

    def test_year_and_duration_search(self):
        search = main.Search()
        search.button_year.setText("1989")
        search.button_duration.setText("154")
        search.search_bd()
        rows = self.read_rows("films_result.sqlite")
        self.assertEqual([row[0] for row in rows], [1])
        self.assertEqual(search.window.model.rowCount(), 1)

    def test_title_is_passed_as_value(self):
        search = main.Search()
        search.button_name.setText("' OR 1=1 --")
        search.search_bd()
        self.assertEqual(self.read_rows("films_result.sqlite"), [])

    def test_favorites_duplicate_and_delete(self):
        table = main.Table("Избранное", "films_love.sqlite")
        edit = QLineEdit("1")
        table.addbt(edit)
        table.addbt(edit)
        self.assertEqual([row[0] for row in self.read_rows("films_love.sqlite")], [1])
        self.assertEqual(table.model.rowCount(), 1)
        table.adddl(edit)
        self.assertEqual(self.read_rows("films_love.sqlite"), [])
        self.assertEqual(table.model.rowCount(), 0)

    def test_recommendations_refresh_after_favorite(self):
        window = main.MainWindow()
        self.assertEqual(window.window3.model.rowCount(), 0)
        window.window2.addbt(QLineEdit("1"))
        window.toggle_window(window.window3)
        rows = self.read_rows("films_recomendations.sqlite")
        self.assertIn(1, [row[0] for row in rows])
        self.assertTrue(all(row[2] == 1989 and row[3] == 1 for row in rows))
        self.assertEqual(window.window3.model.rowCount(), len(rows))

    def test_main_window_loads_image_outside_project_cwd(self):
        window = main.MainWindow()
        images = [label.pixmap() for label in window.findChildren(QLabel)]
        self.assertTrue(any(image is not None and not image.isNull() for image in images))
        self.assertFalse((self.elsewhere / "films_db.sqlite").exists())


if __name__ == "__main__":
    unittest.main()
