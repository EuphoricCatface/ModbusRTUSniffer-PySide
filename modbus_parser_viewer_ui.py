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
from PySide6.QtWidgets import (QApplication, QGridLayout, QMainWindow, QPlainTextEdit,
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
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_raw = QWidget()
        self.tab_raw.setObjectName(u"tab_raw")
        self.gridLayout_2 = QGridLayout(self.tab_raw)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.plainTextEdit_Raw = QPlainTextEdit(self.tab_raw)
        self.plainTextEdit_Raw.setObjectName(u"plainTextEdit_Raw")
        self.plainTextEdit_Raw.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.plainTextEdit_Raw, 0, 0, 1, 1)

        self.plainTextEdit_Parsed = QPlainTextEdit(self.tab_raw)
        self.plainTextEdit_Parsed.setObjectName(u"plainTextEdit_Parsed")
        self.plainTextEdit_Parsed.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByKeyboard|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_2.addWidget(self.plainTextEdit_Parsed, 0, 1, 1, 1)

        self.tabWidget.addTab(self.tab_raw, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        ModbusParserViewer.setCentralWidget(self.centralwidget)

        self.retranslateUi(ModbusParserViewer)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ModbusParserViewer)
    # setupUi

    def retranslateUi(self, ModbusParserViewer):
        ModbusParserViewer.setWindowTitle(QCoreApplication.translate("ModbusParserViewer", u"ModbusParserViewer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_raw), QCoreApplication.translate("ModbusParserViewer", u"Raw Packets", None))
    # retranslateUi

