# ui.py

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QTabWidget, QToolBar, QLineEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QSslCertificate, QSslConfiguration, QSslSocket
import os
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Importing ui.py")

class CustomWebEnginePage(QWebEnginePage):
    def certificateError(self, error):
        logging.info("CustomWebEnginePage: Handling certificate error...")
        cert = error.certificate()
        
        # Only accept certificates from our CA
        ssl_config = QSslConfiguration.defaultConfiguration()
        ca_certs = ssl_config.caCertificates()
        
        for ca_cert in ca_certs:
            if cert.isIssuedBy(ca_cert):
                logging.info("Certificate issued by trusted CA.")
                return True
        
        logging.warning("Certificate not issued by trusted CA.")
        return False

class MainWindow(QMainWindow):
    def __init__(self, ca_cert_path):
        logging.info("Initializing MainWindow...")
        super(MainWindow, self).__init__()
        self.setWindowTitle('PyBrowser')

        logging.info("Creating custom profile for the browser...")
        # Create custom profile for the browser
        self.profile = QWebEngineProfile("proxy_profile")
        
        # Load and add our CA certificate
        logging.info("Loading CA certificate...")
        try:
            with open(ca_cert_path, 'rb') as f:
                cert_data = f.read()
                cert = QSslCertificate(cert_data)
                self.profile.installClientCertificate(cert_data)
            logging.info("CA certificate loaded and installed.")
        except Exception as e:
            logging.error(f"Failed to load CA certificate: {e}")
            raise

        # Configure SSL
        logging.info("Configuring SSL settings...")
        ssl_config = QSslConfiguration.defaultConfiguration()
        ssl_config.setProtocol(QSslConfiguration.TlsV1_2OrLater)
        QSslConfiguration.setDefaultConfiguration(ssl_config)
        logging.info("SSL configuration set.")

        # Create tab widget
        logging.info("Creating tab widget...")
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        # Create toolbar
        logging.info("Creating toolbar...")
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Add navigation buttons
        logging.info("Adding navigation buttons to toolbar...")
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
        logging.info("Adding URL bar to toolbar...")
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Add first tab
        logging.info("Adding initial browser tab...")
        self.add_tab()

    def add_tab(self):
        logging.info("Adding new tab...")
        browser = QWebEngineView()
        page = QWebEnginePage(self.profile, browser)
        browser.setPage(page)
        browser.setUrl(QUrl('https://chat.openai.com'))

        self.tabs.addTab(browser, 'New Tab')
        self.tabs.setCurrentWidget(browser)

        browser.titleChanged.connect(
            lambda title, browser=browser: self.tabs.setTabText(self.tabs.indexOf(browser), title))
        browser.urlChanged.connect(
            lambda url, browser=browser: self.update_url(url) if self.tabs.currentWidget() == browser else None)
        
        logging.info("Tab added and signals connected.")

    def close_tab(self, index):
        logging.info(f"Closing tab at index: {index}")
        if self.tabs.count() < 2:
            logging.info("Only one tab left. Closing application.")
            self.close()
        else:
            browser_widget = self.tabs.widget(index)
            browser_widget.deleteLater()
            self.tabs.removeTab(index)
            logging.info(f"Tab {index} closed.")

    def current_browser(self):
        return self.tabs.currentWidget()

    def navigate_home(self):
        logging.info("Navigating to home URL.")
        self.current_browser().setUrl(QUrl('https://chat.openai.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        logging.info(f"Navigating to URL: {url}")
        if 'http' not in url:
            url = 'https://' + url
        self.current_browser().setUrl(QUrl(url))

    def update_url(self, q):
        if self.sender() == self.current_browser():
            logging.info(f"Updating URL bar to: {q.toString()}")
            self.url_bar.setText(q.toString())
            self.url_bar.setCursorPosition(0)
