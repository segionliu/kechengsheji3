import time
from ui import Ui_MainWindow
import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import cv2
import numpy as np
import threading
import socket
import sys
from queue import Queue
import cv2
from detect import *


provincelist = [
    "皖", "沪", "津", "渝", "冀",
    "晋", "蒙", "辽", "吉", "黑",
    "苏", "浙", "京", "闽", "赣",
    "鲁", "豫", "鄂", "湘", "粤",
    "桂", "琼", "川", "贵", "云",
    "西", "陕", "甘", "青", "宁",
    "新"]

wordlist = [
    "A", "B", "C", "D", "E",
    "F", "G", "H", "J", "K",
    "L", "M", "N", "P", "Q",
    "R", "S", "T", "U", "V",
    "W", "X", "Y", "Z", "0",
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9"]


def get_all_file(path):  # 获取所有文件
    all_file = []
    for f in os.listdir(path):  # listdir返回文件中所有目录
        f_name = os.path.join(path, f)
        all_file.append(f_name)
    return all_file


# 主界面类， 主要使用是使用PyQt5创建界面
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        self.images_pathes = []
        self.images_rets = []
        self.images_real_res = []
        self.iamges_cs = []
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.firmware_dir = None
        self.lineEdit.setFont(QFont("Timers", 28, QFont.Bold))
        self.pushButton.clicked.connect(self.last_image)  # 设置按键响应函数
        self.pushButton_2.clicked.connect(self.next_image)
        self.pushButton_3.clicked.connect(self.batch_pics)
        self.pushButton_4.clicked.connect(self.single_pic)  # 设置按键响应函数
        self.cur_index = -1
        self.right_count = 0

    def last_image(self):
        print("last")
        if self.cur_index <= 0:
            QtWidgets.QMessageBox.warning(self, "title", "没有上一张了！")
            return

        self.cur_index = self.cur_index - 1

        frame = cv2.imread(self.images_pathes[self.cur_index])
        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(show_image))

        retStr, retCs = self.images_rets[self.cur_index], self.iamges_cs[self.cur_index]

        palte_rect = frame[retCs[0][1]:retCs[1][1], retCs[0][0]:retCs[1][0]]
        palte_rect = cv2.resize(palte_rect, (240, 60))
        show_rect = cv2.cvtColor(palte_rect, cv2.COLOR_BGR2RGB)
        # show_rect = palte_rect
        show_image_rect = QImage(show_rect.data, show_rect.shape[1], show_rect.shape[0], QImage.Format_RGB888)
        self.label_2.setPixmap(QPixmap.fromImage(show_image_rect))
        self.lineEdit.setText(retStr)
        pass

    def next_image(self):
        print("next")
        if len(self.images_pathes) == 0 or self.cur_index + 1 >= len(self.images_pathes):
            QtWidgets.QMessageBox.warning(self, "title", "没有下一张了！")
            return

        self.cur_index = self.cur_index + 1

        frame = cv2.imread(self.images_pathes[self.cur_index])
        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(show_image))

        retStr, retCs = self.images_rets[self.cur_index], self.iamges_cs[self.cur_index]

        palte_rect = frame[retCs[0][1]:retCs[1][1], retCs[0][0]:retCs[1][0]]
        palte_rect = cv2.resize(palte_rect, (240, 60))
        show_rect = cv2.cvtColor(palte_rect, cv2.COLOR_BGR2RGB)
        # show_rect = palte_rect
        show_image_rect = QImage(show_rect.data, show_rect.shape[1], show_rect.shape[0], QImage.Format_RGB888)
        self.label_2.setPixmap(QPixmap.fromImage(show_image_rect))
        self.lineEdit.setText(retStr)

        pass


    def get_real(self, imgname):
        _, _, box, points, label, brightness, blurriness = imgname.split('-')
        # --- 读取车牌号
        label = label.split('_')
        # 省份缩写
        province = provincelist[int(label[0])]
        # 车牌信息
        words = [wordlist[int(i)] for i in label[1:]]
        # 车牌号
        label = province + ''.join(words)
        return label


    def batch_pics(self):
        print("batch...")
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件夹", os.getcwd())  # 起始路径

        if directory == '':
            return

        print(directory)
        paths = get_all_file(directory)
        for p in paths:
            img_name = os.path.basename(p).split('.')[0]
            real_str = self.get_real(img_name)
            self.images_real_res.append(real_str)
            retStr, retCs = detect_image(p)

            if retStr == real_str:
                self.right_count = self.right_count + 1

            self.images_pathes.append(p)
            self.images_rets.append(retStr)
            self.iamges_cs.append(retCs)

        if len(self.images_pathes) > 0:
            frame = cv2.imread(self.images_pathes[0])
            show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(show_image))

            retStr, retCs = self.images_rets[0], self.iamges_cs[0]

            palte_rect = frame[retCs[0][1]:retCs[1][1], retCs[0][0]:retCs[1][0]]
            palte_rect = cv2.resize(palte_rect, (240, 60))
            show_rect = cv2.cvtColor(palte_rect, cv2.COLOR_BGR2RGB)
            # show_rect = palte_rect
            show_image_rect = QImage(show_rect.data, show_rect.shape[1], show_rect.shape[0], QImage.Format_RGB888)
            self.label_2.setPixmap(QPixmap.fromImage(show_image_rect))
            self.lineEdit.setText(retStr)
            self.cur_index = 0
            self.lineEdit_2.setText(str(self.right_count / len(self.images_pathes)))
        pass

    def single_pic(self):
        self.image_path = QFileDialog.getOpenFileNames(self, '选择文件', os.getcwd(), "All Files(*);;jpg Files(*)")
        if len(self.image_path[0]) == 0:
            return
        self.image_file_name = self.image_path[0][0]

        frame = cv2.imread(self.image_file_name)

        show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        show_image = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(show_image))

        retStr, retCs = detect_image(self.image_file_name)

        palte_rect = frame[retCs[0][1]:retCs[1][1], retCs[0][0]:retCs[1][0]]
        palte_rect = cv2.resize(palte_rect, (240, 60))
        show_rect = cv2.cvtColor(palte_rect, cv2.COLOR_BGR2RGB)
        # show_rect = palte_rect
        show_image_rect = QImage(show_rect.data, show_rect.shape[1], show_rect.shape[0], QImage.Format_RGB888)
        self.label_2.setPixmap(QPixmap.fromImage(show_image_rect))

        self.lineEdit.setText(retStr)

        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
    myWin.show()
    sys.exit(app.exec_())
