from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("右键菜单示例")
        self.setGeometry(100, 100, 400, 300)  # 设置窗口的位置和大小

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        # 创建动作
        action1 = QAction('主菜单动作', self)
        action2 = QAction('子菜单动作1', self)
        action3 = QAction('子菜单动作2', self)

        # 创建子菜单
        subMenu = QMenu('子菜单', self)
        subMenu.addAction(action2)
        subMenu.addAction(action3)

        # 将动作和子菜单添加到主菜单
        contextMenu.addAction(action1)
        contextMenu.addMenu(subMenu)

        # 显示菜单
        contextMenu.exec_(event.globalPos())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
