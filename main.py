import sys
import os
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent


class DesktopPet(QWidget):
    # 初始化
    def __init__(self):
        super(DesktopPet, self).__init__()
        self.initUI()
        self.tray()
        # 控制类属性
        self.is_follow_mouse = False  # 是否正在拖拽
        self.mouse_drag_pos = self.pos()  # 拖拽位置
        self.msgBox = QMessageBox()
        self.msg = False  # 是否显示消息
        # 动作类属性
        self.act_switch = False  # 做动作开关
        # 声音类属性
        self.sound_switch = True    # 声音开关
        self.playmode = 1           # 声音播放模式:1.唠嗑模式 2.口号模式
        self.is_play = False        # 是否正在播放声音
        self.player = QMediaPlayer()  # 创建QMediaPlayer对象
        self.player.stateChanged.connect(self.checkPlayState)
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)  # 每帧循环
        self.timer.start(100)

    # 初始化UI
    def initUI(self):
        self.w = 100
        self.h = 700
        self.size = 200  # 缩放比例
        self.setGeometry(self.w, self.h, 200, 200)  # 设置窗口位置和大小
        self.action = 1  # 动作编号
        self.frame_number = 0  # 动作帧数
        for f in os.listdir('pic'):
            if (f.startswith('hh1') and f.endswith('.png')):
                self.frame_number += 1
        self.frame = 1  # 当前帧数
        self.lbl = QLabel(self)
        self.pm = [QPixmap('pic\hh11.png')]*(self.frame_number+1)
        for f in range(1, self.frame_number+1):
            self.pm[f] = QPixmap('pic\hh' + str(self.action)+str(f) + '.png')
            self.pm[f] = self.pm[f].copy(QRect(600, 75, 600, 500))
        self.lbl.setPixmap(self.pm[1].scaled(self.size, self.size))
        # 背景透明等效果
        self.setWindowTitle('HuaHuo')
        self.setWindowIcon(QIcon('pic\hh_icon.png'))
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
        self.repaint()

    # 系统托盘
    def tray(self):
        tp = QSystemTrayIcon(self)
        tp.setIcon(QIcon('pic\hh_icon.png'))
        ation_quit = QAction('退出', self, triggered=self.quit)
        tpMenu = QMenu(self)
        tpMenu.addAction(ation_quit)
        tp.setContextMenu(tpMenu)
        tp.show()

    # 显示消息
    def showMessage(self, title, message):
        self.msg = True
        self.msgBox.setWindowTitle(title)
        self.msgBox.setText(message)
        self.msgBox.setIcon(QMessageBox.Information)
        self.msgBox.show()

    # 播放声音
    def playSound(self):
        if self.sound_switch:
            self.player.setMedia(QMediaContent(
                QUrl.fromLocalFile("audio/hh11.WAV")))
            self.player.play()  # 开始播放
        else:
            self.showMessage('提示', '声音已关闭，无法播放音频!')

    # 检查播放状态
    def checkPlayState(self):
        self.is_play = not QMediaPlayer.StoppedState

    # 更改做动作开关
    def actReverse(self):
        self.act_switch = not self.act_switch

    # 更改声音开关
    def soundReverse(self):
        self.sound_switch = not self.sound_switch

    # 更改窗口大小
    def windowResize(self, size):
        self.setGeometry(self.w, self.h, 2*size, 2*size)
        self.size = size*2

    # 进行动作
    def doAction(self):
        if self.act_switch:
            # 读取图片不同的地址，实现动画效果
            if self.frame < self.frame_number:
                self.frame += 1
            else:
                self.frame = 1
        self.lbl.setPixmap(self.pm[self.frame].scaled(
            self.size, self.size))
        self.lbl.setGeometry(0, 0, self.size, self.size)

    # 右键菜单
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act1 = menu.addAction('停止/开始动作')
        act2 = menu.addAction('关闭/开启声音')
        act3 = menu.addAction('显示比例100%')
        act4 = menu.addAction('显示比例75%')
        act5 = menu.addAction('显示比例50%')
        act6 = menu.addAction('退出')
        act1.triggered.connect(self.actReverse)
        act2.triggered.connect(self.soundReverse)
        act3.triggered.connect(lambda: self.windowResize(100))
        act4.triggered.connect(lambda: self.windowResize(75))
        act5.triggered.connect(lambda: self.windowResize(50))
        act6.triggered.connect(self.quit)
        menu.exec_(event.globalPos())

    # 鼠标事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # 左键按下
            self.is_follow_mouse = True
            self.mouse_drag_pos = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_follow_mouse:
            self.move(event.globalPos() - self.mouse_drag_pos)
            xy = self.pos()
            self.w, self.h = xy.x(), xy.y()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.is_play:
            self.player.stop()
        else:
            self.playSound()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    # 托盘退出
    def quit(self):
        self.close()
        sys.exit()

    # 主循环
    def loop(self):
        self.doAction()
        self.repaint()
        # self.size = size*2
        # if self.msg:
        #     self.msgBox.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myPet = DesktopPet()
    sys.exit(app.exec_())
