# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modbus_parser_viewer.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QPlainTextEdit, QPushButton,
    QSizePolicy, QTabWidget, QWidget)

class Ui_ModbusParserViewer(object):
    def setupUi(self, ModbusParserViewer):
        if not ModbusParserViewer.objectName():
            ModbusParserViewer.setObjectName(u"ModbusParserViewer")
        ModbusParserViewer.resize(800, 600)
        self.centralwidget = QWidget(ModbusParserViewer)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.lineEdit_port = QLineEdit(self.widget)
        self.lineEdit_port.setObjectName(u"lineEdit_port")

        self.horizontalLayout_2.addWidget(self.lineEdit_port)

        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_baudrate = QLineEdit(self.widget)
        self.lineEdit_baudrate.setObjectName(u"lineEdit_baudrate")

        self.horizontalLayout_2.addWidget(self.lineEdit_baudrate)

        self.pushButton_start = QPushButton(self.widget)
        self.buttonGroup = QButtonGroup(ModbusParserViewer)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.pushButton_start)
        self.pushButton_start.setObjectName(u"pushButton_start")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart))
        self.pushButton_start.setIcon(icon)
        self.pushButton_start.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.pushButton_start)

        self.pushButton_pause = QPushButton(self.widget)
        self.buttonGroup.addButton(self.pushButton_pause)
        self.pushButton_pause.setObjectName(u"pushButton_pause")
        self.pushButton_pause.setEnabled(False)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause))
        self.pushButton_pause.setIcon(icon1)
        self.pushButton_pause.setCheckable(True)

        self.horizontalLayout_2.addWidget(self.pushButton_pause)

        self.pushButton_stop = QPushButton(self.widget)
        self.buttonGroup.addButton(self.pushButton_stop)
        self.pushButton_stop.setObjectName(u"pushButton_stop")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStop))
        self.pushButton_stop.setIcon(icon2)
        self.pushButton_stop.setCheckable(True)
        self.pushButton_stop.setChecked(True)

        self.horizontalLayout_2.addWidget(self.pushButton_stop)


        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_raw = QWidget()
        self.tab_raw.setObjectName(u"tab_raw")
        self.gridLayout_2 = QGridLayout(self.tab_raw)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.plainTextEdit_Parsed = QPlainTextEdit(self.tab_raw)
        self.plainTextEdit_Parsed.setObjectName(u"plainTextEdit_Parsed")
        self.plainTextEdit_Parsed.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.plainTextEdit_Parsed, 1, 1, 1, 1)

        self.pushButton_showPair = QPushButton(self.tab_raw)
        self.pushButton_showPair.setObjectName(u"pushButton_showPair")
        self.pushButton_showPair.setEnabled(False)

        self.gridLayout_2.addWidget(self.pushButton_showPair, 3, 1, 1, 1)

        self.listWidget_addrValue = QListWidget(self.tab_raw)
        self.listWidget_addrValue.setObjectName(u"listWidget_addrValue")

        self.gridLayout_2.addWidget(self.listWidget_addrValue, 2, 1, 1, 1)

        self.plainTextEdit_Raw = QPlainTextEdit(self.tab_raw)
        self.plainTextEdit_Raw.setObjectName(u"plainTextEdit_Raw")
        self.plainTextEdit_Raw.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.plainTextEdit_Raw, 1, 0, 2, 1)

        self.checkBox_scrollEnd = QCheckBox(self.tab_raw)
        self.checkBox_scrollEnd.setObjectName(u"checkBox_scrollEnd")
        self.checkBox_scrollEnd.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_scrollEnd, 3, 0, 1, 1)

        self.tabWidget.addTab(self.tab_raw, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

        ModbusParserViewer.setCentralWidget(self.centralwidget)
#if QT_CONFIG(shortcut)
        self.label.setBuddy(self.lineEdit_port)
        self.label_2.setBuddy(self.lineEdit_baudrate)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(ModbusParserViewer)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ModbusParserViewer)
    # setupUi

    def retranslateUi(self, ModbusParserViewer):
        ModbusParserViewer.setWindowTitle(QCoreApplication.translate("ModbusParserViewer", u"ModbusParserViewer", None))
        self.label.setText(QCoreApplication.translate("ModbusParserViewer", u"Port:", None))
        self.label_2.setText(QCoreApplication.translate("ModbusParserViewer", u"Baudrate:", None))
        self.pushButton_start.setText(QCoreApplication.translate("ModbusParserViewer", u"Start", None))
        self.pushButton_pause.setText(QCoreApplication.translate("ModbusParserViewer", u"Pause", None))
        self.pushButton_stop.setText(QCoreApplication.translate("ModbusParserViewer", u"Stop", None))
        self.pushButton_showPair.setText(QCoreApplication.translate("ModbusParserViewer", u"Show Corresponding Pair", None))
        self.checkBox_scrollEnd.setText(QCoreApplication.translate("ModbusParserViewer", u"Scroll to End", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_raw), QCoreApplication.translate("ModbusParserViewer", u"Raw Packets", None))
    # retranslateUi

