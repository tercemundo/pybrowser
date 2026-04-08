!/usr/bin/env python3
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QTabWidget, 
    QWidget, QVBoxLayout, QProgressBar, QStatusBar, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
import sys


class BrowserTab(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.loadStarted.connect(self.on_load_started)
        self.loadFinished.connect(self.on_load_finished)
        self.loadProgress.connect(self.on_load_progress)
        self.load(QUrl("https://www.google.com"))
        
    def on_load_started(self):
        self.main_window.loading = True
        
    def on_load_finished(self, success):
        self.main_window.loading = False
        self.main_window.update_url_bar()
        self.main_window.setWindowTitle(self.title() + " - PyBrowser")
        
    def on_load_progress(self, progress):
        self.main_window.progress_bar.setValue(progress)
        
    def createWindow(self, type):
        new_tab = self.main_window.add_new_tab()
        return new_tab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyBrowser")
        self.setGeometry(100, 100, 1200, 800)
        
        self.loading = False
        self.setup_ui()
        self.show()
        
    def setup_ui(self):
        # Barra de pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.setCentralWidget(self.tabs)
        
        # Barra de herramientas
        nav_bar = QToolBar("Navegación")
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)
        
        # Botones de navegación
        btn_back = QAction("←", self)
        btn_back.triggered.connect(lambda: self.current_tab().back())
        btn_back.setShortcut(QKeySequence.StandardKey.Back)
        nav_bar.addAction(btn_back)
        
        btn_forward = QAction("→", self)
        btn_forward.triggered.connect(lambda: self.current_tab().forward())
        btn_forward.setShortcut(QKeySequence.StandardKey.Forward)
        nav_bar.addAction(btn_forward)
        
        btn_reload = QAction("↻", self)
        btn_reload.triggered.connect(lambda: self.current_tab().reload())
        btn_reload.setShortcut(QKeySequence.StandardKey.Refresh)
        nav_bar.addAction(btn_reload)
        
        btn_home = QAction("🏠", self)
        btn_home.triggered.connect(self.go_home)
        nav_bar.addAction(btn_home)
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)
        
        # Botón nueva pestaña
        btn_new_tab = QAction("+", self)
        btn_new_tab.triggered.connect(self.add_new_tab)
        btn_new_tab.setShortcut("Ctrl+T")
        nav_bar.addAction(btn_new_tab)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        # Añadir primera pestaña
        self.add_new_tab()
        
        # Menú contextual
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def add_new_tab(self, url=None):
        tab = BrowserTab(self)
        if url:
            tab.load(QUrl(url))
            
        index = self.tabs.addTab(tab, "Nueva pestaña")
        self.tabs.setCurrentIndex(index)
        
        tab.titleChanged.connect(lambda title, i=index: self.tabs.setTabText(i, title[:20] + "..." if len(title) > 20 else title))
        tab.iconChanged.connect(lambda icon, i=index: self.tabs.setTabIcon(i, icon))
        
        return tab
        
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            
    def current_tab(self):
        return self.tabs.currentWidget()
        
    def update_url_bar(self):
        if self.current_tab():
            url = self.current_tab().url().toString()
            self.url_bar.setText(url)
            
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://", "file://")):
            if "." in url and not " " in url:
                url = "https://" + url
            else:
                url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
                
        self.current_tab().load(QUrl(url))
        
    def go_home(self):
        self.current_tab().load(QUrl("https://www.google.com"))
        
    def show_context_menu(self, position):
        menu = QMenu()
        new_tab_action = menu.addAction("Nueva pestaña")
        new_tab_action.triggered.connect(self.add_new_tab)
        
        close_tab_action = menu.addAction("Cerrar pestaña")
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        
        menu.exec(self.mapToGlobal(position))
        
    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_W:
                self.close_tab(self.tabs.currentIndex())
                event.accept()
            elif event.key() == Qt.Key.Key_L:
                self.url_bar.setFocus()
                self.url_bar.selectAll()
                event.accept()
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PyBrowser")
    app.setWindowIcon(QIcon.fromTheme("web-browser"))
    
    # Configurar perfil del navegador
    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
    profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies)
    
    window = MainWindow()
    sys.exit(app.exec())
