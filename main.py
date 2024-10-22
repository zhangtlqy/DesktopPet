import sys
import os
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import math
pi = math.atan(1)*4


def sinr(x):
    return math.sin(x/180*pi)


def cosr(x):
    return math.cos(x/180*pi)


def atanr(x):
    return math.atan(x)*180/pi


actionNumber = 3  # 动作数量
actionRotate = 1  # 旋转动作
actionRightFly = 2  # 向右飞行动作
actionLeftFly = 3  # 向左飞行动作
actionReturn = 4    # 变回娃娃          #TODO:未实现
flyTimerTime = 30000  # 飞行间隔时间
flySpeed = 20  # 飞行速度
actNumber = 11  # 动作数量


screenApp = QApplication([])  # 创建应用程序实例
screen = screenApp.primaryScreen()  # 获取当前主屏幕对象
screenSize = screen.size()  # 获取屏幕尺寸
screenWidth = screenSize.width()  # 获取屏幕宽度 1920
screenHeight = screenSize.height()  # 获取屏幕高度 1080


class DesktopPet(QWidget):
    # 初始化
    def __init__(self):
        super(DesktopPet, self).__init__()
        # 控制类属性
        self.is_follow_mouse = False  # 是否正在拖拽
        self.mouse_drag_pos = self.pos()  # 拖拽位置
        self.isTop = False  # 是否置顶
        self.act = [QAction('')]*(actNumber+1)  # 右键动作菜单
        # 动作类属性
        self.actSwitch = True  # 做动作开关
        self.flySwitch = True  # 飞行开关
        self.isFly = False  # 是否正在飞行
        self.flyRegion = 1  # 飞行区域 1-四周 2-全屏
        # 声音类属性
        self.soundSwitch = True    # 声音开关
        self.soundMode = 3          # 声音播放模式:1.唠嗑模式 2.口号模式 3.随机模式
        self.soundNumber = [0, 0, 0]
        for f in os.listdir('audio'):
            if (f.startswith('hh1')):
                self.soundNumber[1] += 1
            elif (f.startswith('hh2')):
                self.soundNumber[2] += 1
        self.isPlay = False        # 是否正在播放声音
        self.player = QMediaPlayer()  # 创建QMediaPlayer对象
        self.player.stateChanged.connect(self.checkPlayState)
        # UI
        self.initUI()
        self.tray()
        # 计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)  # 每帧循环
        self.timer.start(150)
        self.flyTimer = QTimer()
        self.flyTimer.timeout.connect(self.startFly)  # 飞行定时器
        self.flyTimer.start(flyTimerTime)  # 30秒钟一次

    # 初始化UI
    def initUI(self):
        self.x = 1600
        self.y = 700
        self.xd = self.x  # 飞行目标位置
        self.yd = self.y
        self.phi = 0  # 飞行方向角
        self.size = 200  # 缩放比例
        self.setGeometry(self.x, self.y, self.size, self.size)  # 设置窗口位置和大小
        self.action = 1  # 动作编号
        self.frameNumber = [0]*(actionNumber+1)  # 动作帧数
        for f in os.listdir('pic'):
            if (f.startswith('hh1') and f.endswith('.png')):
                self.frameNumber[1] += 1
            if (f.startswith('hh2') and f.endswith('.png')):
                self.frameNumber[2] += 1
            if (f.startswith('hh3') and f.endswith('.png')):
                self.frameNumber[3] += 1
        self.frame = 1  # 当前帧数
        self.lbl = QLabel(self)
        self.pm = [[QPixmap('pic\hh11.png') for i in range(self.frameNumber[1]+1)]
                   for j in range(actionNumber+1)]  # 动作图片
        width = [0, 600, 460, 460]
        height = [0, 500, 450, 450]
        xoffset = [0, 600, 460, 1280-460-460]
        yoffset = [0, 75, 0, 0]
        for a in range(1, actionNumber+1):
            for f in range(1, self.frameNumber[a]+1):
                self.pm[a][f] = QPixmap('pic\hh' + str(a)+str(f) + '.png')
                self.pm[a][f] = self.pm[a][f].copy(
                    QRect(xoffset[a], yoffset[a], width[a], height[a]))
        self.lbl.setPixmap(self.pm[self.action]
                           [self.frame].scaled(self.size, self.size))
        # 背景透明等效果
        self.setWindowTitle('HuaHuo')
        self.setWindowIcon(QIcon('pic\hh_icon.png'))
        self.setWindowIconText('HuaHuo')
        # self.setTop()   # 窗口置顶
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.isTop = True
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.show()
        self.repaint()

    # 窗口置顶
    def setTop(self):
        if self.isTop:
            self.setWindowFlags(self.xindowFlags() & ~Qt.WindowStaysOnTopHint)
            self.isTop = False
        else:
            self.setWindowFlags(self.xindowFlags() | Qt.WindowStaysOnTopHint)
            self.isTop = True
        self.show()

    # 播放声音
    def playSound(self):
        if self.soundSwitch:
            if self.soundMode < 3:  # 非随机模式
                x = self.soundMode
            else:
                x = 1 if random.randint(
                    1, self.soundNumber[1]+self.soundNumber[2]) <= self.soundNumber[1] else 2
            y = random.randint(1, self.soundNumber[x])
            print('Play: audio/hh'+str(x) + str(y)+'.WAV')
            self.player.setMedia(QMediaContent(
                QUrl.fromLocalFile('audio/hh'+str(x) + str(y)+'.WAV')))
            self.player.play()  # 开始播放
            self.isPlay = True

    # 检查播放状态
    def checkPlayState(self):
        self.isPlay = (self.player.state() == QMediaPlayer.PlayingState)

    # 更改做动作开关
    def actReverse(self):
        self.actSwitch = not self.actSwitch

    # 更改声音开关
    def soundReverse(self):
        self.soundSwitch = not self.soundSwitch
        if not self.soundSwitch:
            self.player.stop()
            self.isPlay = False

    # 切换声音模式
    def switchSoundMode(self, mode):
        self.soundMode = mode

    # 更改飞行开关
    def flyReverse(self):
        self.flySwitch = not self.flySwitch

    # 更改飞行区域
    def switchFlyRegion(self, region):
        self.flyRegion = region

    # 更改窗口大小
    def windowResize(self, size):
        self.setGeometry(self.x, self.y, 2*size, 2*size)
        self.size = size*2

    # 触发飞行
    def startFly(self):
        if (self.flySwitch):
            if self.flyRegion == 1:
                loopcnt = 0  # 迭代变量，控制循环次数有限
                while abs(self.x-self.xd) < 40 or (abs(self.x-self.xd) > 200 and abs(self.y-self.yd) > 150):
                    self.xd = random.randint(
                        0, self.size)+(screenWidth-2*self.size)*random.randint(0, 1)
                    self.yd = random.randint(
                        0, self.size)+(screenHeight-2*self.size)*random.randint(0, 1)
                    loopcnt += 1
                    if (loopcnt > 50):
                        break
            elif self.flyRegion == 2:
                while abs(self.x-self.xd) < 50:
                    self.xd = random.randint(0, 1800)
                self.yd = random.randint(100, 900)
            self.phi = atanr((self.yd-self.y)/(self.xd-self.x))
            self.action = 2 if self.xd > self.x else 3
            self.flyTimer.stop()

    # 飞行结束
    def stopFly(self):
        self.action = 1
        self.flyTimer.start(flyTimerTime)

    # 进行动作，每帧执行一次
    def doAction(self):
        if self.frame > self.frameNumber[self.action]:
            self.frame = 1
        if self.actSwitch:
            # 切换帧，实现动画效果
            if self.frame < self.frameNumber[self.action]:
                self.frame += 1
            else:
                self.frame = 1
            # action 2,3飞行位移
            if self.action == 2:
                self.y += int(flySpeed*sinr(self.phi)+1)
                self.x += int(flySpeed*cosr(self.phi)+1)
                if self.x >= self.xd:
                    self.stopFly()  # 飞行结束
            elif self.action == 3:
                self.y -= int(flySpeed*sinr(self.phi)+1)
                self.x -= int(flySpeed*cosr(self.phi)+1)
                if self.x <= self.xd:
                    self.stopFly()  # 飞行结束
        self.setGeometry(self.x, self.y, self.size, self.size)
        self.lbl.setPixmap(self.pm[self.action][self.frame].scaled(
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
        self.act[6] = QAction(
            '唠嗑模式', triggered=lambda: self.switchSoundMode(1), checkable=True)
        self.act[7] = QAction(
            '口号模式', triggered=lambda: self.switchSoundMode(2), checkable=True)
        self.act[8] = QAction(
            '随机模式', triggered=lambda: self.switchSoundMode(3), checkable=True)
        self.act[9] = QAction(
            '禁止飞行' if self.flySwitch else '允许飞行', triggered=self.flyReverse)
        self.act[10] = QAction(
            '四周飞行', triggered=lambda: self.switchFlyRegion(1), checkable=True)
        self.act[11] = QAction(
            '全屏飞行', triggered=lambda: self.switchFlyRegion(2), checkable=True)
        menu.addAction(self.act[1])
        menu.addAction(self.act[2])
        menu.addAction(self.act[9])
        regionMenu = QMenu('飞行区域')
        regionMenu.addAction(self.act[10])
        regionMenu.addAction(self.act[11])
        menu.addMenu(regionMenu)
        menu.addSeparator()
        displayMenu = QMenu('显示比例')
        displayMenu.addAction(self.act[3])
        displayMenu.addAction(self.act[4])
        displayMenu.addAction(self.act[5])
        menu.addMenu(displayMenu)
        soundMenu = QMenu('声音模式')
        soundMenu.addAction(self.act[6])
        soundMenu.addAction(self.act[7])
        soundMenu.addAction(self.act[8])
        menu.addMenu(soundMenu)
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

    # 菜单更新打勾
    def updateMenus(self):
        for a in range(3, 11):
            self.act[a].setChecked(False)
        if (self.size == 200):  # 更新显示比例
            self.act[3].setChecked(True)
        elif (self.size == 150):
            self.act[4].setChecked(True)
        elif (self.size == 100):
            self.act[5].setChecked(True)
        if self.soundMode == 1:  # 更新声音模式
            self.act[6].setChecked(True)
        elif self.soundMode == 2:
            self.act[7].setChecked(True)
        elif self.soundMode == 3:
            self.act[8].setChecked(True)
        if self.flyRegion == 1:  # 更新飞行区域
            self.act[10].setChecked(True)
        elif self.flyRegion == 2:
            self.act[11].setChecked(True)
        self.actTop.setChecked(True if self.isTop else False)  # 更新置顶

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
            self.x, self.y = xy.x(), xy.y()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if self.isPlay:
            self.player.stop()
            self.isPlay = False
        else:
            self.playSound()

    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        if not (self.x == self.xd):
            self.phi = atanr((self.yd-self.y)/(self.xd-self.x))  # 更新飞行方向角

    # 托盘退出
    def quit(self):
        self.close()
        sys.exit()

    # 主循环
    def loop(self):
        self.checkPlayState()
        self.doAction()
        self.repaint()
        self.updateMenus()  # 菜单打勾


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myPet = DesktopPet()
    sys.exit(app.exec_())
