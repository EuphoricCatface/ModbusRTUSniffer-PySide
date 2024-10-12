# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device_value_table.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QHeaderView,
    QLabel, QSizePolicy, QSpinBox, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_DeviceValueTable(object):
    def setupUi(self, DeviceValueTable):
        if not DeviceValueTable.objectName():
            DeviceValueTable.setObjectName(u"DeviceValueTable")
        DeviceValueTable.resize(651, 599)
        self.gridLayout = QGridLayout(DeviceValueTable)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_width = QLabel(DeviceValueTable)
        self.label_width.setObjectName(u"label_width")

        self.gridLayout.addWidget(self.label_width, 0, 0, 1, 1)

        self.spinBox_width = QSpinBox(DeviceValueTable)
        self.spinBox_width.setObjectName(u"spinBox_width")
        self.spinBox_width.setValue(16)

        self.gridLayout.addWidget(self.spinBox_width, 0, 1, 1, 1)

        self.checkBox_sameRegisters = QCheckBox(DeviceValueTable)
        self.checkBox_sameRegisters.setObjectName(u"checkBox_sameRegisters")
        self.checkBox_sameRegisters.setEnabled(False)
        self.checkBox_sameRegisters.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_sameRegisters, 0, 2, 1, 1)

        self.checkBox_sameRW = QCheckBox(DeviceValueTable)
        self.checkBox_sameRW.setObjectName(u"checkBox_sameRW")
        self.checkBox_sameRW.setEnabled(False)
        self.checkBox_sameRW.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_sameRW, 0, 3, 1, 1)

        self.tableWidget_main = QTableWidget(DeviceValueTable)
        if (self.tableWidget_main.columnCount() < 15):
            self.tableWidget_main.setColumnCount(15)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(9, __qtablewidgetitem8)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(10, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(11, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(12, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(13, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.tableWidget_main.setHorizontalHeaderItem(14, __qtablewidgetitem13)
        self.tableWidget_main.setObjectName(u"tableWidget_main")
        self.tableWidget_main.horizontalHeader().setMinimumSectionSize(25)
        self.tableWidget_main.horizontalHeader().setDefaultSectionSize(50)
        self.tableWidget_main.verticalHeader().setMinimumSectionSize(15)
        self.tableWidget_main.verticalHeader().setDefaultSectionSize(25)

        self.gridLayout.addWidget(self.tableWidget_main, 1, 0, 1, 4)

#if QT_CONFIG(shortcut)
        self.label_width.setBuddy(self.spinBox_width)
#endif // QT_CONFIG(shortcut)

        self.retranslateUi(DeviceValueTable)

        QMetaObject.connectSlotsByName(DeviceValueTable)
    # setupUi

    def retranslateUi(self, DeviceValueTable):
        DeviceValueTable.setWindowTitle(QCoreApplication.translate("DeviceValueTable", u"DeviceValueTable", None))
        self.label_width.setText(QCoreApplication.translate("DeviceValueTable", u"Width:", None))
        self.checkBox_sameRegisters.setText(QCoreApplication.translate("DeviceValueTable", u"Holding/input registers are the same", None))
        self.checkBox_sameRW.setText(QCoreApplication.translate("DeviceValueTable", u"Read/write are the same", None))
        ___qtablewidgetitem = self.tableWidget_main.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("DeviceValueTable", u"0", None));
        ___qtablewidgetitem1 = self.tableWidget_main.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("DeviceValueTable", u"1", None));
        ___qtablewidgetitem2 = self.tableWidget_main.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("DeviceValueTable", u"2", None));
        ___qtablewidgetitem3 = self.tableWidget_main.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("DeviceValueTable", u"3", None));
        ___qtablewidgetitem4 = self.tableWidget_main.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("DeviceValueTable", u"4", None));
        ___qtablewidgetitem5 = self.tableWidget_main.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("DeviceValueTable", u"5", None));
        ___qtablewidgetitem6 = self.tableWidget_main.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("DeviceValueTable", u"6", None));
        ___qtablewidgetitem7 = self.tableWidget_main.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("DeviceValueTable", u"7", None));
        ___qtablewidgetitem8 = self.tableWidget_main.horizontalHeaderItem(9)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("DeviceValueTable", u"A", None));
        ___qtablewidgetitem9 = self.tableWidget_main.horizontalHeaderItem(10)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("DeviceValueTable", u"B", None));
        ___qtablewidgetitem10 = self.tableWidget_main.horizontalHeaderItem(11)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("DeviceValueTable", u"C", None));
        ___qtablewidgetitem11 = self.tableWidget_main.horizontalHeaderItem(12)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("DeviceValueTable", u"D", None));
        ___qtablewidgetitem12 = self.tableWidget_main.horizontalHeaderItem(13)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("DeviceValueTable", u"E", None));
        ___qtablewidgetitem13 = self.tableWidget_main.horizontalHeaderItem(14)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("DeviceValueTable", u"F", None));
    # retranslateUi

