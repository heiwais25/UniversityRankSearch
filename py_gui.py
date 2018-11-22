import sys
from univ_rank import UnivRank 
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListView, QWidget, QTableWidgetItem
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtWidgets import QLineEdit, QGridLayout, QLabel, QTableWidget
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QSize

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QApplication

def get_center_aligned_table_data(data):
    rank_item = QTableWidgetItem("%s" % str(data))
    rank_item.setTextAlignment(Qt.AlignHCenter)
    return rank_item


class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("ui.ui", self)
        self.ui.show()

        self.univ_rank = UnivRank()
        self.ui.lineEdit.textChanged.connect(self.sync_lineEdit)

        # Set each box's placeholder text
        self.ui.lineEdit.setPlaceholderText("University Name") 


        # Set country combobox
        self.cur_country = "All country"
        countryList = [self.cur_country] + self.univ_rank.get_all_country()
        self.ui.countryComboBox.clear()
        self.ui.countryComboBox.setEditable(True)
        self.ui.countryComboBox.addItems(countryList)
        self.ui.countryComboBox.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.ui.countryComboBox.currentTextChanged.connect(self.countryComboBox_changed)

        # Set subject combobox
        self.cur_subject = "All subject"
        subjectList = [self.cur_subject] + self.univ_rank.get_all_subject()
        self.ui.subjectComboBox.clear()
        self.ui.subjectComboBox.setEditable(True)
        self.ui.subjectComboBox.addItems(subjectList)
        self.ui.subjectComboBox.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.ui.subjectComboBox.currentTextChanged.connect(self.subjectComboBox_changed)

        # Init table view
        self.ui.tableWidget.cellDoubleClicked.connect(self.get_detailed_info)
        self.cur_row_cnt = 25

        self.ui.tableWidget.setRowCount(self.cur_row_cnt)
        self.ui.tableWidget.setColumnCount(3)
        header = self.ui.tableWidget.horizontalHeader()  

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self.column_headers = ['Current\nRank', 'Default\nRank', 'Name', 'Country']
        self.ui.tableWidget.setHorizontalHeaderLabels(self.column_headers[1:])
        
        # Default show university
        candidate = self.univ_rank.get_candidates()
        for idx, element in enumerate(candidate):
            self.ui.tableWidget.setItem(idx, 0, get_center_aligned_table_data(idx+1))
            self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem("%s" % element.name))
            self.ui.tableWidget.setItem(idx, 2, QTableWidgetItem("%s" % element.country))


    def print_univ_list(self, user_input="", category_change=False):
        self.ui.tableWidget.setRowCount(0)
        if category_change:
            user_input = self.ui.lineEdit.text().lower()
        candidate = self.univ_rank.get_candidates(user_input)
        # In the default case
        if self.cur_country == "All country" and self.cur_subject == "All subject":
            if category_change:
                self.cur_row_cnt = 50
                self.ui.tableWidget.setRowCount(self.cur_row_cnt)
                self.ui.tableWidget.setColumnCount(3)
                header = self.ui.tableWidget.horizontalHeader()  
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
                header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
                self.ui.tableWidget.setHorizontalHeaderLabels(self.column_headers[1:])
        
            self.ui.tableWidget.setRowCount(len(candidate))
            for idx, element in enumerate(candidate):
                rank = element.rank["default"]
                if rank == -1:
                    rank = "1000+"
                else:
                    rank = "%d" % rank
                self.ui.tableWidget.setItem(idx, 0, get_center_aligned_table_data(rank))
                self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem("%s" % element.name))
                self.ui.tableWidget.setItem(idx, 2, QTableWidgetItem("%s" % element.country))

        else:
            # Remove the table
            if category_change:
                self.ui.tableWidget.setColumnCount(4)
                header = self.ui.tableWidget.horizontalHeader()  
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
                header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
                self.ui.tableWidget.setHorizontalHeaderLabels(self.column_headers)

            if self.cur_subject != "All subject" and self.cur_country != "All country":
                tmp_candidate = self.univ_rank.get_candidates()
                new_candidate = []
                cnt = 0
                for element in candidate:
                    if element.country != self.cur_country:
                        continue
                    while cnt < len(tmp_candidate) and element.id != tmp_candidate[cnt].id:
                        cnt += 1
                    element.rank["country"] = cnt + 1
                    new_candidate.append(element)
                candidate = new_candidate

            self.ui.tableWidget.setRowCount(len(candidate))
            for idx, element in enumerate(candidate):
                default_rank = element.rank["default"]
                if default_rank == -1:
                    default_rank = "1000+"
                else:
                    default_rank = str(default_rank)
                
                if self.cur_country == "All country":
                    current_rank = element.rank[self.cur_subject]
                else:
                    current_rank = element.rank["country"]
                
                self.ui.tableWidget.setItem(idx, 0, get_center_aligned_table_data(current_rank))
                self.ui.tableWidget.setItem(idx, 1, get_center_aligned_table_data(default_rank))
                self.ui.tableWidget.setItem(idx, 2, QTableWidgetItem("%s" % element.name))
                self.ui.tableWidget.setItem(idx, 3, QTableWidgetItem("%s" % element.country))


    def countryComboBox_changed(self, value):
        if value == "All country":
            self.cur_country = value
            if self.cur_subject == "All subject":
                self.univ_rank.set_category()
            else:
                self.univ_rank.set_category("subject", self.cur_subject)
            self.print_univ_list(category_change = True)
        if self.univ_rank.has_country_key(value):
            self.cur_country = value
            self.univ_rank.set_category("country", value)
            self.print_univ_list(category_change = True)
        # do your code


    def subjectComboBox_changed(self, value):
        if value == "All subject":
            self.cur_subject = value
            if self.cur_country == "All country":
                self.univ_rank.set_category()
            else:
                self.univ_rank.set_category("country", self.cur_country)
            self.print_univ_list(category_change = True)
        if self.univ_rank.has_subject_key(value):
            self.cur_subject = value
            self.univ_rank.set_category("subject", value)
            self.print_univ_list(category_change = True)


    def sync_lineEdit(self, text):
        user_input = self.ui.lineEdit.text().lower()
        self.print_univ_list(user_input)


    @pyqtSlot()
    def slot_1st(self):
        self.ui.lineEdit.clear()
        self.ui.subjectComboBox.setCurrentIndex(0)
        self.ui.countryComboBox.setCurrentIndex(0)
 
    def get_detailed_info(self, row, col):
        header = self.ui.tableWidget.horizontalHeaderItem(col).text()
        item = self.ui.tableWidget.item(row, col).text()
        # In the case of country column is doubleclicked
        if header == self.column_headers[-1]:
            index = self.ui.countryComboBox.findText(item, QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.ui.countryComboBox.setCurrentIndex(index)
            self.ui.countryComboBox.setCurrentIndex(index)



    # @pyqtSlot()
    # def slot_3rd(self):
    #     self.ui.lineEdit.setText("세번째 버튼")
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())