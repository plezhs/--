from datetime import datetime
import json
import sys
import PyQt6.QtCore
import PyQt6.QtGui
from PyQt6.QtWidgets import (QApplication, QLabel,QFrame,QWidget,QHBoxLayout,QVBoxLayout,QGridLayout,QLineEdit,QPushButton, QDialog, QMessageBox,QListView, QComboBox)  # Added import for QComboBox
from PyQt6.QtCore import QSortFilterProxyModel, Qt, QByteArray  # Added import for QByteArray
from PyQt6.QtGui import QFont,QStandardItemModel, QStandardItem,QIntValidator, QIcon, QImage, QPixmap  # Added import for QPixmap
import os
from qt_material import apply_stylesheet, list_themes
import webbrowser  # Added import for webbrowser
import requests  # Added import for requests

# def resource_path(relative_path):
#     """ PyInstaller 패키지 내에서 리소스 파일의 절대 경로를 가져오는 함수 """
#     if getattr(sys, 'frozen', False):
#         # PyInstaller로 패키징된 경우
#         base_path = sys._MEIPASS
#     else:
#         # 스크립트가 실행 중인 디렉터리
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

class TagFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.filter_tags = []
        self.include_tags = []

    def setFilterTags(self, tags):
        self.filter_tags = tags
        self.invalidateFilter()

    def setIncludeTags(self, tags):
        self.include_tags = tags
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        item = self.sourceModel().itemFromIndex(index)
        item_tags = item.data(Qt.ItemDataRole.UserRole)

        # 수입/지출 태그 필터링
        if self.include_tags:
            if not any(tag in item_tags for tag in self.include_tags):
                return False

        # ComboBox 태그 필터링
        if self.filter_tags:
            if not any(tag in item_tags for tag in self.filter_tags):
                return False

        return True

class DB:
    def __init__(self):
        self.dburl = ""
        self.money = int()
        self.log = []
        self.log_m = []
        self.tms = int()
        self.timestamp = ""
        self.tagli = []

class MW(QWidget):
    def __init__(self):
        """ Constructor for Main Window Class """
        super().__init__()
        self.db = os.getenv('APPDATA')+"/plezhs/db.json"
        try:
            with open(self.db,'r') as js:
                data = json.load(js)
                DB.money = data["money"]
                DB.log = data["log"]
                DB.log_m = data["log_m"]
                DB.tms = data["theme"]
                DB.tagli = list(set(data["tags"]))
        except FileNotFoundError:
            with open(self.db,'w') as js:
                data = {
                    "money": 0,
                    "log": [],
                    "log_m": [],
                    "theme": 0,
                    "tags": [
                        "\ud544\ud130\ub9c1 \uc5c6\uc74c"
                        ]
                    }
                json.dump(data,js,indent=4)
        self.text = ''
        self.initialize_ui()



    def initialize_ui(self):
        """setup GUI application."""
        self.setFixedSize(405,720)
        self.setWindowTitle("가계부")

        mainlayout = QVBoxLayout()
        moneybal = QVBoxLayout()
        filterbox = QHBoxLayout()
        grid = QGridLayout()
        self.setLayout(mainlayout)

        mainlayout.addLayout(moneybal)
        mainlayout.addLayout(grid)

        self.btnm = QPushButton() # Set the minimum size directly without QSize
        self.btnm.setText(f"잔액\n{DB.money}₩")
        self.btnm.clicked.connect(self.btnmo)
        self.btnm.setStyleSheet("background-color: transparent;")

        self.btnfilin = QPushButton()
        self.btnfilin.setText("수입\n내역")
        self.btnfilin.setFixedSize(65,65)
        self.btnfilin.setCheckable(True)

        self.btnfilout = QPushButton()
        self.btnfilout.setText("지출\n내역")
        self.btnfilout.setFixedSize(65,65)
        self.btnfilout.setCheckable(True)
        
        self.combo_box = QComboBox()
        for j in DB.tagli:
            self.combo_box.addItem(j)
        
        # self.tag_list_widget = QListWidget()
        # self.tag_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        # self.tag_list_widget.setFixedHeight(100)
        # for j in DB.tagli:
        #     self.tag_list_widget.addItem(QListWidgetItem(j))

        # QListView 설정
        self.result_output = QListView()
        self.result_output.setFixedHeight(250)
        self.result_output.clicked.connect(lambda index: self.info(index))

        self.btnsv = QPushButton()
        self.btnsv.setFixedSize(100,30)
        self.btnsv.setText('저장')
        self.btnsv.clicked.connect(self.dbsave)

        # self.static = QPushButton()
        # self.static.setFixedSize(100,30)
        # self.static.setText('통계')
        # self.static.clicked.connect(self.sta)

        self.btninput = QPushButton()
        self.btninput.setFixedSize(100,30)
        self.btninput.setText("수입")
        self.btninput.clicked.connect(self.inp)

        self.btnminus = QPushButton()
        self.btnminus.setFixedSize(100,30)
        self.btnminus.setText("지출")
        self.btnminus.clicked.connect(self.inm)

        # QStandardItemModel 생성
        self.model = QStandardItemModel(self.result_output)

        # 아이템 생성 및 태그 설정
        self.items = []
        for k in range(0,len(DB.log_m)):
            it = (f"{DB.log_m[k]['timestamp']}",f"{DB.log[k]}",f"{DB.log_m[k][DB.log[k]]}",DB.log_m[k]["tag"])
            self.items.append(it)
        for timeline,name,mone,tags in self.items:
            item = QStandardItem(f"[{timeline}] {name} : {mone}")
            item.setData(tags, Qt.ItemDataRole.UserRole)
            item.setData([timeline,name,mone,tags],Qt.ItemDataRole.UserRole + 1)
            self.model.appendRow(item)
        
        self.proxy_model = TagFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.result_output.setModel(self.proxy_model)

        self.btnfilin.clicked.connect(self.onFilterChanged)
        self.btnfilout.clicked.connect(self.onFilterChanged)
        self.combo_box.currentTextChanged.connect(self.onFilterChanged)

        moneybal.addWidget(self.btnm)
        moneybal.addLayout(filterbox)
        filterbox.addWidget(self.btnfilin)
        filterbox.addWidget(self.btnfilout)
        filterbox.addWidget(self.combo_box)
        moneybal.addWidget(self.result_output)
        grid.addWidget(self.btnsv,0,0)
        # grid.addWidget(self.static,0,1)
        grid.addWidget(self.btninput,0,1)
        grid.addWidget(self.btnminus,0,2)

        apply_stylesheet(app,theme=f"{list_themes()[DB.tms]}")

        url_image = "https://camo.githubusercontent.com/4374f0b29a45f7d158ec8fe94398eb90f4ac94c03d6b99346b99e916e5157cb9/68747470733a2f2f6564656e742e6769746875622e696f2f537570657254696e7949636f6e732f696d616765732f706e672f6769746875622e706e67"

        # Add GitHub button with icon
        self.github_button = QPushButton()
        response = requests.get(url_image)
        image_data = QByteArray(response.content)

        # Set the icon
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.github_button.setIcon(QIcon(pixmap))
        self.github_button.setIconSize(PyQt6.QtCore.QSize(30,30))  # Adjust the icon size
        self.github_button.setFixedSize(30, 30)
        self.github_button.clicked.connect(self.open_github)
        moneybal.addWidget(self.github_button)

        self.show() # Display the window on the screen

    # def sta(self):
    #     tagli = list()
    #     for j in DB.tagli:
    #         tagli.append(j)
    #     tagli.remove('필터링 없음')
    #     reli = []
    #     for i in tagli:
    #         reli.append({i : self.calculate_tag_ratios_within_deposit_withdraw(self.model,i)})
    #     print(reli)

    def info(self, index):
        self.dialog = QDialog()
        apply_stylesheet(self.dialog,theme=list_themes()[DB.tms])
        self.dialog.setWindowTitle('Info')
        self.dialog.setFixedSize(400,400)

        source_index = self.proxy_model.mapToSource(index)
    
    # 원본 모델에서 아이템 가져오기
        item = self.model.itemFromIndex(source_index)
        item_data = item.data(Qt.ItemDataRole.UserRole + 1)

        timestamp = item_data[0]
        name = item_data[1]
        amount = item_data[2]
        tags = item_data[3]

        # vlay = QVBoxLayout()
        
        # name = QPushButton()
        # name.setText(item_data[1])
        # name.setStyleSheet("background-color: transparent; border: none;")
        # name.setEnabled(False)

        layout = QVBoxLayout()

        # 카드 스타일을 위한 프레임
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Shape.Box)
        card_frame.setLineWidth(2)
        
        # 카드 레이아웃
        card_layout = QVBoxLayout()
        
        # 타임스탬프, 이름, 금액, 태그를 표시할 라벨
        timestamp_label = QLabel(f"<b>Timestamp:</b> {timestamp}")
        name_label = QLabel(f"<b>Name:</b> {name}")
        
        # amount를 숫자로 변환하고 포맷팅 적용
        try:
            amount = float(amount)
        except ValueError:
            amount = 0.0
        
        amount_label = QLabel(f"<b>Amount:</b> {amount:,.2f}₩")
        tags_label = QLabel(f"<b>Tags:</b> {', '.join(tags)}")
        
        # 폰트 스타일 설정
        font = QFont()
        font.setPointSize(12)
        timestamp_label.setFont(font)
        name_label.setFont(font)
        amount_label.setFont(font)
        tags_label.setFont(font)
        
        # 라벨을 카드 레이아웃에 추가
        card_layout.addWidget(timestamp_label)
        card_layout.addWidget(name_label)
        card_layout.addWidget(amount_label)
        card_layout.addWidget(tags_label)
        
        # 카드 레이아웃을 프레임에 설정
        card_frame.setLayout(card_layout)
        
        # 다이얼로그에 카드 프레임 추가
        layout.addWidget(card_frame)
        
        # 닫기 버튼 추가
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setFixedHeight(65)
        
        layout.addWidget(close_button)
        self.dialog.setLayout(layout)

        self.dialog.exec()

    def accept(self):
        self.dialog.close()
        self.dialog.deleteLater()

    def onFilterChanged(self):
        include_tags = []
        if self.btnfilin.isChecked():
            include_tags.append("수입")
        if self.btnfilout.isChecked():
            include_tags.append("지출")
        
        # include_tags가 비어 있으면 "수입" 및 "지출" 태그 필터링을 하지 않음
        self.proxy_model.setIncludeTags(include_tags)

        filter_tag = self.combo_box.currentText()
        if filter_tag == "필터링 없음":
            self.proxy_model.setFilterTags([])
        else:
            self.proxy_model.setFilterTags([filter_tag])
    #=================
    #로그창 불러오기
    def loadlog(self):
        loglist = []
        text = ''
        for i in range(0,len(DB.log)) :
            text += f"[{DB.log_m[i]['timestamp']}] {DB.log[i]} : {DB.log_m[i][DB.log[i]]}"
            loglist.append(f"[{DB.log_m[i]['timestamp']}] {DB.log[i]} : {DB.log_m[i][DB.log[i]]}",)
        return loglist
    #=================
    #저장
    def dbsave(self):
        with open(self.db,'w',encoding='UTF-8') as js:
            data = {
                "money" : DB.money,
                "log" : DB.log,
                "log_m" : DB.log_m,
                "theme" : DB.tms,
                "tags" : DB.tagli
            }
            json.dump(data,js,indent=4)
    #=================
    #테마
    def btnmo(self):
        """setup the main window."""
        tms = list_themes()
        if DB.tms == 26:
            DB.tms = 0
            apply_stylesheet(app,theme=tms[DB.tms])
        else:
            DB.tms += 1
            apply_stylesheet(app,theme=tms[DB.tms])
    #=================
    #수입
    def inp(self):
        self.dialog = QDialog()
        apply_stylesheet(self.dialog,theme=list_themes()[DB.tms])
        self.dialog.setWindowTitle('수입')
        self.dialog.setFixedSize(400,400)

        self.tagli = []

        grid = QGridLayout()
        self.dialog.setLayout(grid)

        taglay = QHBoxLayout()

        self.log = QLineEdit()
        self.log.setPlaceholderText("수입 출처")
        self.log.setFixedSize(200, 55)

        self.logm = QLineEdit()
        self.logm.setValidator(QIntValidator(self))
        self.logm.setFixedSize(200, 55)
        self.logm.setPlaceholderText("금액")

        self.tag = QLineEdit()
        self.tag.setPlaceholderText("태그")
        self.tag.setFixedSize(200,55)

        tagadd = QPushButton()
        tagadd.setText("추가")
        tagadd.setFixedSize(55,55)
        tagadd.clicked.connect(self.tagadd)

        self.combtn = QPushButton()
        self.combtn.setText("완료")
        self.combtn.setFixedSize(145, 55)
        self.combtn.clicked.connect(self.moneyp)

        grid.addWidget(self.log,0,0)
        grid.addWidget(self.logm,1,0)
        grid.addLayout(taglay,2,0)
        taglay.addWidget(self.tag)
        taglay.addWidget(tagadd)
        grid.addWidget(self.combtn,3,0)

        self.dialog.exec()
    
    def tagadd(self):
        if not self.tag.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
        else:
            self.tagli.append(self.tag.text())
            DB.tagli.append(self.tag.text())
            if self.tag.text() not in self.get_combo_box_items():
                self.combo_box.addItem(self.tag.text())
            self.tag.setText('')

    def moneyp(self):
        time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if not self.log.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
        elif not self.logm.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
        else:
            DB.log.append(self.log.text())
            self.tagli.append("수입")
            DB.log_m.append({self.log.text() : int(self.logm.text()),"timestamp" : time,"tag" : self.tagli})
            DB.money += int(self.logm.text())
            self.btnm.setText(f"Money\n{DB.money}₩")
            # self.result_output.addItem(f"[{time}] {self.log.text()} : {int(self.logm.text())}")
            item = QStandardItem(f"[{time}] {self.log.text()} : {int(self.logm.text())}")
            item.setData(self.tagli, Qt.ItemDataRole.UserRole)
            item.setData([time, self.log.text(), int(self.logm.text()), self.tagli], Qt.ItemDataRole.UserRole + 1)
            self.model.appendRow(item)
            self.dbsave()
        self.log.setText('')
        self.logm.setText('')

        self.dialog.close()
        self.dialog.deleteLater()
    #=================
    #지출
    def inm(self):
        self.dialog = QDialog()
        apply_stylesheet(self.dialog,theme=list_themes()[DB.tms])
        self.dialog.setWindowTitle('지출')
        self.dialog.setFixedSize(400,400)

        self.tagli = []

        grid = QGridLayout()
        self.dialog.setLayout(grid)

        taglay = QHBoxLayout()

        self.log = QLineEdit()
        self.log.setPlaceholderText("사유")
        self.log.setFixedSize(200, 55)

        self.logm = QLineEdit()
        self.logm.setValidator(QIntValidator(self))
        self.logm.setFixedSize(200, 55)
        self.logm.setPlaceholderText("금액")

        self.tag = QLineEdit()
        self.tag.setPlaceholderText("태그")
        self.tag.setFixedSize(200,55)

        tagadd = QPushButton()
        tagadd.setText("추가")
        tagadd.setFixedSize(55,55)
        tagadd.clicked.connect(self.tagadd)

        self.combtn = QPushButton()
        self.combtn.setText("완료")
        self.combtn.setFixedSize(145, 55)
        self.combtn.clicked.connect(self.moneym)

        grid.addWidget(self.log,0,0)
        grid.addWidget(self.logm,1,0)
        grid.addLayout(taglay,2,0)
        taglay.addWidget(self.tag)
        taglay.addWidget(tagadd)
        grid.addWidget(self.combtn,3,0)

        self.dialog.exec()
    
    def get_combo_box_items(self):
        items = []
        for i in range(self.combo_box.count()):
            items.append(self.combo_box.itemText(i))
        return items

    def tagadd(self):
        if not self.tag.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
        else:
            self.tagli.append(self.tag.text())
            DB.tagli.append(self.tag.text())
            if self.tag.text() not in self.get_combo_box_items():
                self.combo_box.addItem(self.tag.text())
            self.tag.setText('')
    
    def moneym(self):
        time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if not self.log.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
            print(self.log.text())
        elif not self.logm.text():
            reply = QMessageBox.information(self, 'Warning', '모든 칸을 채워주세요.')
            print(self.logm.text())
        else:
            DB.log.append(self.log.text())
            self.tagli.append("지출")
            DB.log_m.append({self.log.text() : -int(self.logm.text()),"timestamp" : time,"tag" : self.tagli})
            DB.money -= int(self.logm.text())
            self.btnm.setText(f"Money\n{DB.money}₩")
            # self.result_output.addItem(f"[{time}] {self.log.text()} : -{int(self.logm.text())}")
            item = QStandardItem(f"[{time}] {self.log.text()} : -{int(self.logm.text())}")
            item.setData(self.tagli, Qt.ItemDataRole.UserRole)
            item.setData([time, self.log.text(), -int(self.logm.text()), self.tagli], Qt.ItemDataRole.UserRole + 1)
            self.model.appendRow(item)
            self.dbsave()

        self.log.setText('')
        self.logm.setText('')

        self.dialog.close()
        self.dialog.deleteLater()

    def open_github(self):
        webbrowser.open("https://github.com/plezhs")

# ===============================
# Run the program
if __name__ == '__main__':
    # PyQt6 관련 부분.
    print(PyQt6.QtCore.qVersion()) # PyQt6 버전 check.

    # Event Loop 등을 위한 QApplication instance 생성.
    app = QApplication(sys.argv)
    # main window 생성 및 show 호출.
    window = MW()
    # Event Loop 시작.
    sys.exit(app.exec())