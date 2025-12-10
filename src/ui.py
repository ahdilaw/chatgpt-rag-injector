# ui.py

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTabWidget, QToolBar, QLineEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QUrl

class CustomWebEnginePage(QWebEnginePage):
    def certificateError(self, error):
        # Accept all SSL certificate errors
        return True

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('PyBrowser')

        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add navigation buttons
        back_btn = QAction('⮜', self)
        back_btn.triggered.connect(lambda: self.current_browser().back())
        toolbar.addAction(back_btn)

        forward_btn = QAction('⮞', self)
        forward_btn.triggered.connect(lambda: self.current_browser().forward())
        toolbar.addAction(forward_btn)

        reload_btn = QAction('⟳', self)
        reload_btn.triggered.connect(lambda: self.current_browser().reload())
        toolbar.addAction(reload_btn)

        home_btn = QAction('⌂', self)
        home_btn.triggered.connect(self.navigate_home)
        toolbar.addAction(home_btn)

        add_tab_btn = QAction('+', self)
        add_tab_btn.triggered.connect(self.add_tab)
        toolbar.addAction(add_tab_btn)

        # Add URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Add first tab
        self.add_tab()

    def add_tab(self):
        browser = QWebEngineView()
        page = CustomWebEnginePage(browser)
        browser.setPage(page)
        browser.setUrl(QUrl('https://chat.openai.com'))

        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)

        browser.titleChanged.connect(
            lambda title, browser=browser: self.tabs.setTabText(self.tabs.indexOf(browser), title))
        browser.urlChanged.connect(
            lambda url, browser=browser: self.update_url(url) if self.tabs.currentWidget() == browser else None)

    def close_tab(self, index):
        if self.tabs.count() < 2:
            self.close()
        else:
            browser_widget = self.tabs.widget(index)
            browser_widget.deleteLater()
            self.tabs.removeTab(index)

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_home(self):
        self.current_browser().setUrl(QUrl('https://chat.openai.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if 'http' not in url:
            url = 'https://' + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        if self.sender() == self.current_browser():
            self.url_bar.setText(q.toString())
            self.url_bar.setCursorPosition(0)