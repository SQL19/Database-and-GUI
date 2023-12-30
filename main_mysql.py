import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QAction, \
     QGridLayout, QLineEdit, QPushButton, QMainWindow, QTableWidget, \
     QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sqlite3
import mysql.connector

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon('icons/add.png'), 'Add Student', self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction('About', self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon('icons/search.png'), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id', 'Name', 'Course', 'Mobile'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # add toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # add status bar
        self. statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton('Edit Record')
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton('Delete Record')
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM students')
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for col_number, data in enumerate(row_data):
                self.table.setItem(row_number, col_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Insert Student Data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        # add combo box of courses
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText('Mobile')
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton('Register')
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO students (name, course, mobile) Values (%s, %s, %s)',
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        row = list(result)[0]
        print(row)
        items = sms.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            sms.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Update Student Data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = sms.table.currentRow()
        self.student_id = sms.table.item(index, 0).text()
        student_name = sms.table.item(index, 1).text()
        course_name = sms.table.item(index, 2).text()
        mobile = sms.table.item(index, 3).text()

        # add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText(student_name)
        layout.addWidget(self.student_name)

        # add combo box of courses
        self.course_name = QComboBox()
        courses = ['Biology', 'Math', 'Astronomy', 'Physics']
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # add mobile widget
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText(mobile)
        layout.addWidget(self.mobile)

        # add submit button
        button = QPushButton('Update')
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        id = self.student_id
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('UPDATE students SET name = %s, course = %s, mobile = %s \
                        WHERE id = %s', (name, course, mobile, id))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Delete Student Data')

        layout = QGridLayout()
        confirmation = QLabel('Are you sure to delete this record?')
        yes = QPushButton('Yes')
        no = QPushButton('No')

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        index = sms.table.currentRow()
        student_id = sms.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('DELETE from students WHERE id = %s', (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()

        self.close()
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle('Success')
        confirmation_widget.setText('The record was deleted successfully!')
        confirmation_widget.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        message = """This app was created during the course 
                     'The Python Mega Course' 
                  """
        self.setText(message)

class DatabaseConnection:
    def __init__(self, host='localhost', user='root', password='<insert your database password here>', database='school'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection

app = QApplication(sys.argv)
sms = MainWindow()
sms.show()
sms.load_data()
sys.exit(app.exec())
