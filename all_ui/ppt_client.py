# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ppt_client.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(299, 194)
        Form.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.horizontalLayout_2 = QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label1 = QLabel(Form)
        self.label1.setObjectName(u"label1")
        self.label1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label1)

        self.label2 = QLabel(Form)
        self.label2.setObjectName(u"label2")

        self.verticalLayout_2.addWidget(self.label2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.label3 = QLabel(Form)
        self.label3.setObjectName(u"label3")

        self.verticalLayout_2.addWidget(self.label3, 0, Qt.AlignmentFlag.AlignHCenter)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.Button1 = QPushButton(Form)
        self.Button1.setObjectName(u"Button1")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Button1.sizePolicy().hasHeightForWidth())
        self.Button1.setSizePolicy(sizePolicy)
        self.Button1.setIconSize(QSize(15, 16))

        self.horizontalLayout.addWidget(self.Button1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"ppt\u667a\u80fd\u52a9\u624b\u5ba2\u6237\u7aef", None))
        self.label1.setText(QCoreApplication.translate("Form", u"\u5f53\u524d\u672a\u542f\u52a8\u7a0b\u5e8f\uff01", None))
        self.label2.setText(QCoreApplication.translate("Form", u"\u5f53\u524d\u65e0\u624b\u52bf", None))
        self.label3.setText(QCoreApplication.translate("Form", u"\u76ee\u524d\u4e0d\u5728ppt\u5de5\u4f5c\u533a", None))
        self.Button1.setText(QCoreApplication.translate("Form", u"\u542f\u52a8\u7a0b\u5e8f", None))
    # retranslateUi

