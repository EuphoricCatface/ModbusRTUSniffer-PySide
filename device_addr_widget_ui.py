# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device_addr_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QSizePolicy,
    QTabWidget, QVBoxLayout, QWidget)

from device_value_table import DeviceValueTable

class Ui_DeviceAddrWidget(object):
    def setupUi(self, DeviceAddrWidget):
        if not DeviceAddrWidget.objectName():
            DeviceAddrWidget.setObjectName(u"DeviceAddrWidget")
        DeviceAddrWidget.resize(751, 616)
        self.verticalLayout = QVBoxLayout(DeviceAddrWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(DeviceAddrWidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_sameRegisters = QCheckBox(self.widget)
        self.checkBox_sameRegisters.setObjectName(u"checkBox_sameRegisters")
        self.checkBox_sameRegisters.setEnabled(False)
        self.checkBox_sameRegisters.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_sameRegisters)

        self.checkBox_sameBits = QCheckBox(self.widget)
        self.checkBox_sameBits.setObjectName(u"checkBox_sameBits")
        self.checkBox_sameBits.setEnabled(False)
        self.checkBox_sameBits.setChecked(True)

        self.horizontalLayout.addWidget(self.checkBox_sameBits)


        self.verticalLayout.addWidget(self.widget)

        self.tabWidget = QTabWidget(DeviceAddrWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_bit = DeviceValueTable()
        self.tab_bit.setObjectName(u"tab_bit")
        self.tabWidget.addTab(self.tab_bit, "")
        self.tab_register = DeviceValueTable()
        self.tab_register.setObjectName(u"tab_register")
        self.tabWidget.addTab(self.tab_register, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(DeviceAddrWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DeviceAddrWidget)
    # setupUi

    def retranslateUi(self, DeviceAddrWidget):
        DeviceAddrWidget.setWindowTitle(QCoreApplication.translate("DeviceAddrWidget", u"DeviceAddrWidget", None))
        self.checkBox_sameRegisters.setText(QCoreApplication.translate("DeviceAddrWidget", u"Holding/input registers are the same", None))
        self.checkBox_sameBits.setText(QCoreApplication.translate("DeviceAddrWidget", u"Coils/Discrete Inputs are the same", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_bit), QCoreApplication.translate("DeviceAddrWidget", u"Bits", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_register), QCoreApplication.translate("DeviceAddrWidget", u"Registers", None))
    # retranslateUi

