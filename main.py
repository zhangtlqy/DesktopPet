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
        self.isTop = True  # 是否置顶
        self.act = [QAction('')]*7  # 右键动作菜单
        # 动作类属性
        self.actSwitch = True  # 做动作开关
        # 声音类属性
        self.soundSwitch = True    # 声音开关
        self.soundMode = 2          # 声音播放模式:1.唠嗑模式 2.口号模式
        self.soundNumber = [0, 0, 0]
        for f in os.listdir('audio'):
            if (f.startswith('hh1')):
                self.soundNumber[1] += 1
            elif (f.startswith('hh2')):
                self.soundNumber[2] += 1
        self.is_play = False        # 是否正在播放声音
        self.player = QMediaPlayer()  # 创建QMediaPlayer对象
        self.player.stateChanged.connect(self.checkPlayState)
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)  # 每帧循环
        self.timer.start(150)

    # 初始化UI
    def initUI(self):
        self.w = 1600
        self.h = 700
        self.size = 200  # 缩放比例
        self.setGeometry(self.w, self.h, 200, 200)  # 设置窗口位置和大小
        self.action = 1  # 动作编号
        self.frameNumber = 0  # 动作帧数
        for f in os.listdir('pic'):
            if (f.startswith('hh1') and f.endswith('.png')):
                self.frameNumber += 1
        self.frame = 1  # 当前帧数
        self.lbl = QLabel(self)
        self.pm = [QPixmap('pic\hh11.png')]*(self.frameNumber+1)
        for f in range(1, self.frameNumber+1):
            self.pm[f] = QPixmap('pic\hh' + str(self.action)+str(f) + '.png')
            self.pm[f] = self.pm[f].copy(QRect(600, 75, 600, 500))
        self.lbl.setPixmap(self.pm[1].scaled(self.size, self.size))
        # 背景透明等效果
        self.setWindowTitle('HuaHuo')
        self.setWindowIcon(QIcon('pic\hh_icon.png'))
        self.setWindowIconText('HuaHuo')
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
        self.repaint()

    # 窗口置顶

    def setTop(self):
        if self.isTop:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.isTop = False
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.isTop = True
        self.show()

    # 播放声音
    def playSound(self):
        if self.soundSwitch:
            self.player.setMedia(QMediaContent(
                QUrl.fromLocalFile('audio/hh'+str(self.soundMode) +
                                   str(random.randint(1, self.soundNumber[self.soundMode]))+'.WAV')))
            self.player.play()  # 开始播放

    # 检查播放状态
    def checkPlayState(self):
        self.is_play = not QMediaPlayer.StoppedState

    # 更改做动作开关
    def actReverse(self):
        self.actSwitch = not self.actSwitch

    # 更改声音开关
    def soundReverse(self):
        self.soundSwitch = not self.soundSwitch

    # 切换声音模式
    def switchSoundMode(self):
        self.playmode = 2 if self.playmode == 1 else 1

    # 更改窗口大小
    def windowResize(self, size):
        self.setGeometry(self.w, self.h, 2*size, 2*size)
        self.size = size*2

    # 进行动作
    def doAction(self):
        if self.actSwitch:
            # 读取图片不同的地址，实现动画效果
            if self.frame < self.frameNumber:
                self.frame += 1
            else:
                self.frame = 1
        self.lbl.setPixmap(self.pm[self.frame].scaled(
            self.size, self.size))
        self.lbl.setGeometry(0, 0, self.size, self.size)

    # 右键菜单
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        self.act[1] = QAction(
            '停止动作'if self.actSwitch else '开始动作', triggered=self.actReverse)
        self.act[2] = QAction(
            '关闭声音' if self.soundSwitch else '打开声音', triggered=self.soundReverse)
        self.act[3] = QAction(
            '100%', triggered=lambda: self.windowResize(100), checkable=True)
        self.act[4] = QAction(
            '75%', triggered=lambda: self.windowResize(75), checkable=True)
        self.act[5] = QAction(
            '50%', triggered=lambda: self.windowResize(50), checkable=True)
        self.act[6] = QAction('切换至唠嗑模式' if self.soundMode ==
                              2 else '切换至口号模式', triggered=self.switchSoundMode)
        menu.addAction(self.act[1])
        menu.addAction(self.act[2])
        menu.addSeparator()
        subMenu = QMenu('显示比例')
        subMenu.addAction(self.act[3])
        subMenu.addAction(self.act[4])
        subMenu.addAction(self.act[5])
        menu.addMenu(subMenu)
        menu.exec_(event.globalPos())  # 显示菜单

    # 系统托盘
    def tray(self):
        tp = QSystemTrayIcon(self)
        tp.setIcon(QIcon('pic\hh_icon.png'))
        self.actTop = QAction('置顶', self, triggered=self.setTop)
        self.actTop.setCheckable(True)
        actQuit = QAction('退出', self, triggered=self.quit)
        tpMenu = QMenu(self)
        tpMenu.addAction(self.actTop)
        tpMenu.addAction(actQuit)
        tp.setContextMenu(tpMenu)
        tp.show()

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
        # self.show()
        # 菜单打勾
        if (self.size == 200):
            self.act[3].setChecked(True)
            self.act[4].setChecked(False)
            self.act[5].setChecked(False)
        elif (self.size == 150):
            self.act[3].setChecked(False)
            self.act[4].setChecked(True)
            self.act[5].setChecked(False)
        elif (self.size == 100):
            self.act[3].setChecked(False)
            self.act[4].setChecked(False)
            self.act[5].setChecked(True)
        self.actTop.setChecked(True if self.isTop else False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myPet = DesktopPet()
    sys.exit(app.exec_())
