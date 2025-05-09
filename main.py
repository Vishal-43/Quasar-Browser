import sys
import os
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QAction, QToolBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class BrowserTab(QWidget):
    def __init__(self, home_url):
        super().__init__()
        self.layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.setUrl(home_url)
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Quasar Browser")
        self.setWindowIcon(QIcon.fromTheme("applications-internet"))
        self.setMinimumSize(1200, 700)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.setCentralWidget(self.tabs)

        # Navigation bar
        nav_bar = QToolBar("Navigation")
        nav_bar.setMovable(False)
        nav_bar.setIconSize(QSize(24, 24))
        self.addToolBar(nav_bar)

        self.back_btn = QAction(QIcon.fromTheme("go-previous"), "←", self)
        self.back_btn.triggered.connect(self.go_back)
        nav_bar.addAction(self.back_btn)

        self.forward_btn = QAction(QIcon.fromTheme("go-next"), "→", self)
        self.forward_btn.triggered.connect(self.go_forward)
        nav_bar.addAction(self.forward_btn)

        self.reload_btn = QAction(QIcon.fromTheme("view-refresh"), "↻", self)
        self.reload_btn.triggered.connect(self.reload_page)
        nav_bar.addAction(self.reload_btn)

        self.home_btn = QAction(QIcon.fromTheme("go-home"), "🏠", self)
        self.home_btn.triggered.connect(self.go_home)
        nav_bar.addAction(self.home_btn)

        # New Tab Button (with lambda to avoid passing unwanted bool)
        self.new_tab_btn = QAction(QIcon.fromTheme("tab-new"), "+", self)
        self.new_tab_btn.triggered.connect(lambda: self.add_new_tab())
        nav_bar.addAction(self.new_tab_btn)

        nav_bar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # Theme toggle
        self.dark_mode = False
        self.theme_btn = QAction("🌙", self)
        self.theme_btn.triggered.connect(self.toggle_theme)
        nav_bar.addAction(self.theme_btn)

        self.add_new_tab(self.get_home_url(), "New Tab")

    def get_home_url(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "index.html"))
        return QUrl.fromLocalFile(path)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = self.get_home_url()
        browser_tab = BrowserTab(qurl)
        i = self.tabs.addTab(browser_tab, label)
        self.tabs.setCurrentIndex(i)
        browser_tab.browser.setUrl(qurl)
        browser_tab.browser.urlChanged.connect(
            lambda qurl, browser_tab=browser_tab: self.update_urlbar(qurl, browser_tab)
        )
        browser_tab.browser.loadFinished.connect(
            lambda _, i=i, browser_tab=browser_tab: self.tabs.setTabText(i, browser_tab.browser.page().title())
        )

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        current_browser = self.current_browser()
        current_browser.setUrl(q)

    def update_urlbar(self, q, browser_tab):
        if browser_tab == self.current_browser_tab():
            self.url_bar.setText(q.toString())
            self.url_bar.setCursorPosition(0)

    def current_browser(self):
        return self.current_browser_tab().browser

    def current_browser_tab(self):
        return self.tabs.currentWidget()

    def go_back(self):
        self.current_browser().back()

    def go_forward(self):
        self.current_browser().forward()

    def reload_page(self):
        self.current_browser().reload()

    def go_home(self):
        self.current_browser().setUrl(self.get_home_url())

    def toggle_theme(self):
        if not self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e2f; }
                QToolBar { background-color: #2e2e3f; color: white; }
                QLineEdit { background-color: #444; color: white; padding: 6px; border-radius: 5px; }
                QTabWidget::pane { border: 0; }
                QTabBar::tab { background: #2e2e3f; color: white; padding: 10px; border-radius: 5px; }
                QTabBar::tab:selected { background: #444; }
            """)
            self.theme_btn.setText("☀️")
        else:
            self.setStyleSheet("")
            self.theme_btn.setText("🌙")
        self.dark_mode = not self.dark_mode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Browser")
    window = Browser()
    window.show()
    sys.exit(app.exec_())
