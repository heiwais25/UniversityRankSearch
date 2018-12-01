import sys
import ctypes

from univ_rank import UnivRank
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Filter(QtCore.QObject):
    def eventFilter(self, widget, event):
        # Focus out filter
        # It is used for maintaining inital content when it is focused out
        # without changing certain value
        if event.type() == QtCore.QEvent.FocusOut:
            widget.setCurrentIndex(widget.currentIndex())
            return False
        else:
            return False


class Form(QtWidgets.QDialog):
    DEFAULT_DISPLAY_LENGTH = 25
    DISPLAY_ITEMS = [25, 50, 100, 200]
    FILTER_MODE = {
        "default" : 0,
        "extended" : 1
    }

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        # QtWidgets.QMainWindow.setA(self, QtGui.QIcon('icon.ico'))



        self.ui = uic.loadUi("ui.ui", self)
        self.ui.show()
        self._univ_rank = UnivRank()

        self._init_lineEdit()

        self._filter = Filter()
        self._init_comboBox("country")
        self._init_comboBox("subject")

        self._init_tableWidget()
        self._init_detailTableWidget()

        self._init_displayLengthComboBox()


    def _get_current_filter_mode(self):
        ''' 0 : Default, 1 : Subject and country selected, 2 : else
        '''
        if self._cur_country == "All country" and self._cur_subject == "All subject":
            return 0
        elif self._cur_subject != "All subject" and self._cur_country != "All country":
            return 1
        else:
            return 2


    def _print_univ_list(self, 
                        user_input="", 
                        category_change=False, 
                        display_length_modified=False, 
                        limit=25):
        '''
        '''
        widget = self.ui.tableWidget
        widget.setRowCount(0)
        current_filter_mode = self._get_current_filter_mode()

        if category_change:
            user_input = self.ui.lineEdit.text().lower()
            self._change_tableWidget_template(current_filter_mode)

        # Based on user input, get the related candidate
        candidate = self._univ_rank.get_candidates(user_input, limit=limit)

        # In the default case
        total_display_length = self._univ_rank.get_total_result_length()

        if current_filter_mode == Form.FILTER_MODE["extended"]:
            candidate, total_display_length = \
                self.__get_candidates_at_selected_option(user_input)

        self.__fill_tableWidget(candidate, current_filter_mode)

        if not display_length_modified:
            # Change the comobobox
            self.__setDisplayLengthComboBox(total_display_length)
            

    # Methods for initializing ================================================
    def _init_comboBox(self, mode):
        '''Initialize country and subject comboBox 
        '''
        if mode == "country":
            comboBox = self.ui.countryComboBox
            contents = ["All country"] + self._univ_rank.get_all_country()
            self._cur_country = contents[0]

        else:
            comboBox = self.ui.subjectComboBox
            contents = ["All subject"] + self._univ_rank.get_all_subject()
            self._cur_subject = contents[0]
        # print(contents)
        # Set country combobox
        comboBox.clear()
        comboBox.setEditable(True)
        comboBox.addItems(contents)
        comboBox.completer().setCompletionMode(QCompleter.PopupCompletion)
        comboBox.installEventFilter(self._filter)

        if mode == "country":
            comboBox.currentTextChanged.connect(self._countryComboBox_changed)

        elif mode == "subject":
            comboBox.currentTextChanged.connect(self._subjectComboBox_changed)


    def _init_tableWidget(self):
        '''Initialize tableWidget which will display university list
        '''
        widget = self.ui.tableWidget

        # Set the number of university to display
        self._cur_table_content_id = []
        self._cur_row_cnt = Form.DEFAULT_DISPLAY_LENGTH
        self._cur_display_length = Form.DEFAULT_DISPLAY_LENGTH

        widget.setRowCount(self._cur_row_cnt)
        widget.setColumnCount(3)
        header = widget.horizontalHeader()

        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self._column_headers = [
            'Current\nRank', 'Default\nRank', 'Name', 'Country'
        ]

        widget.setHorizontalHeaderLabels(self._column_headers[1:])

        # Default show university
        candidate = self._univ_rank.get_candidates()
        for idx, element in enumerate(candidate):
            widget.setItem(idx, 0, self.__centeredTableItem(idx+1))
            widget.setItem(idx, 1, QTableWidgetItem(str(element.name)))
            widget.setItem(idx, 2, QTableWidgetItem(str(element.country)))
            self._cur_table_content_id.append(element.id)

        widget.cellClicked.connect(self._change_img)
        widget.itemSelectionChanged.connect(self.__change_img_item_changed)
        widget.cellDoubleClicked.connect(self._get_detailed_info)


    def _init_detailTableWidget(self):
        '''Initialize detailTableWidget which shows selected university info
        '''
        self._cur_row = -1
        widget = self.ui.detailTableWidget
        detail_column_header = ['Subject', 'Rank']
        widget.setColumnCount(2)

        header = widget.horizontalHeader()
        header.setStyleSheet("::section { padding:10px; }")
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.sectionClicked.connect(self.__setSortingMode)

        widget.setHorizontalHeader(header)
        widget.setHorizontalHeaderLabels(detail_column_header)


    def _init_displayLengthComboBox(self):
        '''Initialize displayLengthComboBox which choose how much univ we want
        to see at one widget
        '''
        comboBox = self.ui.displayLengthComboBox
        # Set length combobox
        comboBox.currentIndexChanged.connect(
            self.__change_display_length
        )
        self.__setDisplayLengthComboBox(
            self._univ_rank.get_total_result_length()
        )


    def _init_lineEdit(self):
        '''Initialize lineEdit where user can type what he want to find
        '''
        self.ui.lineEdit.textChanged.connect(self._sync_lineEdit)
        # Set each box's placeholder text
        self.ui.lineEdit.setPlaceholderText("University Name")



    # For the detailTableWidget ===============================================
    def _get_detailed_info(self, row, col):
        header = self.ui.tableWidget.horizontalHeaderItem(col).text()
        item = self.ui.tableWidget.item(row, col).text()
        # In the case of country column is doubleclicked
        if header == self._column_headers[-1]:
            index = self.ui.countryComboBox.findText(
                item, QtCore.Qt.MatchFixedString)
            if index >= 0:
                self.ui.countryComboBox.setCurrentIndex(index)
            self.ui.countryComboBox.setCurrentIndex(index)


    def _change_img(self, row, col):
        if row != self._cur_row:
            self.ui.detailTableWidget.setRowCount(0)

        # Get current id
        univ = self._univ_rank.get_univ_by_id(self._cur_table_content_id[row])
        self.ui.detailTableWidget.setRowCount(len(univ.rank))

        for idx, content in enumerate(univ.rank.items()):
            self.ui.detailTableWidget.setItem(
                idx, 0, self.__centeredTableItem(content[0])
            )
            self.ui.detailTableWidget.setItem(
                idx, 1, self.__centeredTableItem(content[1])
            )

        if row == self._cur_row:
            return

        image_path = './univ_img/img_%d.jpg' % univ.id
        self.textBrowser.document().setHtml("""
        <div align="center">
            <img src="{0}" style="vertical-align: middle;"/>
            <span style="vertical-align: middle;">{1}</span>
        </div>""".format(image_path, univ.name))

        self._cur_row = row

    def __change_img_item_changed(self):
        items = self.ui.tableWidget.selectedItems()
        if len(items):
            self._change_img(items[0].row(), 0)


    def __setSortingMode(self):
        self.ui.detailTableWidget.setSortingEnabled(True)
        self.ui.detailTableWidget.setSortingEnabled(False)



    # For the displayLengthComboBox ===========================================
    def __setDisplayLengthComboBox(self, totalLength):
        comboBox = self.ui.displayLengthComboBox
        # Set length combobox
        comboBox.clear()
        display_length_idx = self.__find_corresponding_idx(
            Form.DISPLAY_ITEMS, totalLength
        )
        items = Form.DISPLAY_ITEMS[:display_length_idx] + ['All']
        comboBox.addItems([str(val) for val in items])


    def __change_display_length(self, value):
        currentText = self.ui.displayLengthComboBox.currentText()
        if currentText == '':
            return
        if currentText == 'All':
            display_length = self._univ_rank.get_total_result_length()
        else:
            display_length = int(currentText)
        # if self._cur_display_length != display_length:
        self._cur_display_length = display_length
        self._print_univ_list(category_change=True,
                             limit=display_length, 
                             display_length_modified=True)


    def __find_corresponding_idx(self, arr, value):
        for idx, arr_value in enumerate(arr):
            if value <= arr_value:
                return idx
        return len(arr)


    # For the country, subject comboBox =======================================
    def _countryComboBox_changed(self, value):
        if value == "All country":
            self._cur_country = value
            if self._cur_subject == "All subject":
                self._univ_rank.set_category()
            else:
                self._univ_rank.set_category("subject", self._cur_subject)
            self._cur_display_length = 25
            self._print_univ_list(category_change=True)
        if self._univ_rank.has_country_key(value):
            self._cur_display_length = 25
            self._cur_country = value
            self._univ_rank.set_category("country", value)
            self._print_univ_list(category_change=True)


    def _subjectComboBox_changed(self, value):
        if value == "All subject":
            self._cur_subject = value
            if self._cur_country == "All country":
                self._univ_rank.set_category()
            else:
                self._univ_rank.set_category("country", self._cur_country)
            self._cur_display_length = 25
            self._print_univ_list(category_change=True)
        if self._univ_rank.has_subject_key(value):
            self._cur_subject = value
            self._univ_rank.set_category("subject", value)
            self._cur_display_length = 25
            self._print_univ_list(category_change=True)


    # For the lineEdit =======================================================
    def _sync_lineEdit(self, text):
        user_input = self.ui.lineEdit.text().lower()
        self._print_univ_list(user_input)


    @pyqtSlot()
    def slot_1st(self):
        self.ui.lineEdit.clear()
        self.ui.subjectComboBox.setCurrentIndex(0)
        self.ui.countryComboBox.setCurrentIndex(0)
        self.ui.displayLengthComboBox.setCurrentIndex(0)
        self.ui.detailTableWidget.setRowCount(0)
        self.textBrowser.clear()


    # For the tableWidget =====================================================
    def _change_tableWidget_template(self, mode):
        widget = self.ui.tableWidget
        resize_mode = [QHeaderView.ResizeToContents, QHeaderView.Stretch]
        if mode == 0:
            widget.setColumnCount(3)
            header = widget.horizontalHeader()
            header.setSectionResizeMode(0, resize_mode[0])
            header.setSectionResizeMode(1, resize_mode[1])
            header.setSectionResizeMode(2, resize_mode[0])
            widget.setHorizontalHeaderLabels(self._column_headers[1:])
        else:
            widget.setColumnCount(4)
            header = widget.horizontalHeader()
            header.setSectionResizeMode(0, resize_mode[0])
            header.setSectionResizeMode(1, resize_mode[0])
            header.setSectionResizeMode(2, resize_mode[1])
            header.setSectionResizeMode(3, resize_mode[0])
            widget.setHorizontalHeaderLabels(self._column_headers)


    def __get_candidates_at_selected_option(self, user_input):
        # Because it is easy to compare only country in both cases
        self._univ_rank.set_category("subject", self._cur_subject)
        candidate = self._univ_rank.get_candidates(user_input, limit=-1)

        all_candidate = [
            element for element in self._univ_rank.get_candidates(limit=-1) 
            if element.country == self._cur_country
        ]

        cnt = 0
        new_candidate = []
        for element in candidate:
            if element.country != self._cur_country:
                continue
            while element.id != all_candidate[cnt].id:
                cnt += 1
            element.rank["country"] = cnt + 1
            new_candidate.append(element)

        candidate = new_candidate[:self._cur_display_length]

        return candidate, len(new_candidate)

    def __centeredTableItem(self, data):
        rank_item = QtWidgets.QTableWidgetItem("%s" % str(data))
        # rank_item.setTextAlignment(QtCore.Qt.AlignVCenter)
        rank_item.setTextAlignment(QtCore.Qt.AlignCenter)
        return rank_item



    def __get_correct_rank(self, element_rank, mode):
        if mode == Form.FILTER_MODE["default"]:
            rank = element_rank["default"]
            if rank == -1:
                ret = "1000+"
            else:
                ret = str(rank)
        else:
            if self._cur_country == "All country":
                ret = element_rank[self._cur_subject]
            else:
                ret = element_rank["country"]
        return ret


    def __fill_tableWidget(self, candidate, mode):
        widget = self.ui.tableWidget
        self._cur_row_cnt = len(candidate)
        self._cur_table_content_id = []
        widget.setRowCount(self._cur_row_cnt)
        for idx, element in enumerate(candidate):
            default_rank = self.__get_correct_rank(element.rank, 0)

            if mode == Form.FILTER_MODE["default"]:
                widget.setItem(idx, 0, self.__centeredTableItem(default_rank))
                widget.setItem(idx, 1, QTableWidgetItem(str(element.name)))
                widget.setItem(idx, 2, QTableWidgetItem(str(element.country)))
            else:
                current_rank = self.__get_correct_rank(element.rank, mode)
                widget.setItem(idx, 0, self.__centeredTableItem(current_rank))
                widget.setItem(idx, 1, self.__centeredTableItem(default_rank))
                widget.setItem(idx, 2, QTableWidgetItem(str(element.name)))
                widget.setItem(idx, 3, QTableWidgetItem(str(element.country)))
            self._cur_table_content_id.append(element.id)





if __name__ == '__main__':
    myappid = u'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('univ_icon.ico'))
    w = Form()
    sys.exit(app.exec())
