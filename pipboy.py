import sys, os, io, subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, 
     QLabel, QMainWindow,QPushButton,
    QStackedWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QButtonGroup, QSizePolicy, QFrame, QProgressBar, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QIcon, QFontDatabase, QPixmap, QColor, QMovie, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer, QTime, QUrl, QDate, QRect,QCoreApplication
import pygame
from random import randint
import psutil
from gpiozero import Button, LED, RotaryEncoder
import time


os.environ["QT_QPA_PLATFORMTHEME"] = ""
try: 
    import folium
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except:
    print("using map image")
try:
   
    encoder = RotaryEncoder(26, 20) 
    encoder_2 = RotaryEncoder(19, 16)
except:
    encoder = None
    encoder_2 = None
    print("Encoders weren't detected")
try:
    button = Button(5, pull_up=True)
    shutdown_btn = Button(21,pull_up=True, hold_time=2.0)

    led_radio = LED(6) 
    led_radio.on()     
    led_rads = LED(12)      
except:
    button = None
    shutdown_btn = None
    led_rads = None
    led_radio = None
if shutdown_btn is not None:
    shutdown_btn.when_held = lambda: subprocess.Popen(
        ["sudo", "shutdown", "-h", "now"]
    ) 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.initUI()
       
        # self.boot = Bootup()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.setWindowFlags(Qt.CustomizeWindowHint)

        sound_path = os.path.join(BASE_DIR, "audio", "ok_fixed.wav")
        self.nav_click = pygame.mixer.Sound(sound_path)
        self.nav_click.set_volume(1)

        sound_path = os.path.join(BASE_DIR, "audio", "ui_pipboy_highlight.wav")
        self.map_click_sound = pygame.mixer.Sound(sound_path)

        sound_path = os.path.join(BASE_DIR, "audio", "ui_static_d_04.wav")
        self.static = pygame.mixer.Sound(sound_path)
        self.static.set_volume(1)

        sound_path = os.path.join(BASE_DIR, "audio", "ui_static_c_02.wav")
        self.static_short = pygame.mixer.Sound(sound_path)
        self.static_short.set_volume(1)

        sound_path = os.path.join(BASE_DIR, "audio", "ui_pipboy_select.wav")
        self.subnav_click = pygame.mixer.Sound(sound_path)
        self.subnav_click.set_volume(1)

        sound_path = os.path.join(BASE_DIR, "audio", "rads_fixed.wav")
        self.rads_sound = pygame.mixer.Sound(sound_path)

        self.game_running = False

        try:
            self.rotary_value = encoder.steps
        except:
            self.rotary_value = 0
        try:
            self.rotary_2_value = encoder_2.steps
        except:
            self.rotary_2_value = 0
        QApplication.setOverrideCursor(Qt.BlankCursor)
        self.show()


    def initUI(self):
        self.setWindowTitle("pipboy")
        self.setFixedSize(480, 320)
        self.current_time = QTime.currentTime()
        central_widget = QWidget()
        self.hp = 259
        self.totalhp = 259
        self.battery = psutil.sensors_battery()

        self.setCentralWidget(central_widget)
        # self.setWindowFlags(Qt.CustomizeWindowHint)
        self.pages = QStackedWidget()
        
        self.setWindowIcon(QIcon("images/vault.png"))
        self.setStyleSheet("""
            QMainWindow {
               background-color: qlineargradient(
                        x1:0, y1:0, x2:0, y2:1,
                        stop:0 #001300,
                        stop:0.25 #000500,
                        stop:0.5 #000000,
                        stop:0.75 #000500,
                        stop:1 #001300
                    );
            }
            """)
        settings = QLabel(self)
        pixmap = QPixmap("images/settings.png")
        pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        settings.setPixmap(pixmap)
        settings.setScaledContents(True)
        settings.setFixedSize(30,30)

        battery = QLabel(self)
        pixmap = QPixmap("images/id.png")
        pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        battery.setPixmap(pixmap)
        battery.setScaledContents(True)
        battery.setFixedSize(30,30)

       

#----------stat------------
        self.stat = QPushButton("STAT", self)
        self.stat_page = QWidget()
        self.stat.clicked.connect(self.stat_click)

        stat_layout = QVBoxLayout(self.stat_page)

        self.stat_stack = QStackedWidget()

        self.status_page = QWidget()
        self.connect_page = QWidget()
        self.diagnosticcs_page = QWidget()

        status_layout = QVBoxLayout(self.status_page)
        connect_layout = QVBoxLayout(self.connect_page)
        diagnostics_layout = QVBoxLayout(self.diagnosticcs_page)

        #status
        self.status_gif = QLabel()
        self.status_gif.setAlignment(Qt.AlignCenter)

        self.status_movie = QMovie("images/pipboy_stat.gif")
        self.status_gif.setMovie(self.status_movie)
        self.status_movie.setScaledSize(QSize(165, 135))

        status_layout.addWidget(self.status_gif)

        self.status_movie.start()

       
        #connect
        self.connect_gif = QLabel()
        self.connect_gif.setAlignment(Qt.AlignCenter)

        self.connect_movie = QMovie("images/progress-bar.gif")
        self.connect_gif.setMovie(self.connect_movie)

        self.connect_movie.setScaledSize(QSize(190, 140))

        connect_layout.addWidget(self.connect_gif)

        self.connect_movie.start()

        #diagnostics
        self.diag_gif = QLabel()
        self.diag_label = QLabel()

        self.diag_label.setText("Please wait")
        self.diag_label.setAlignment(Qt.AlignCenter)

        self.diag_gif.setAlignment(Qt.AlignCenter)

        self.diag_movie = QMovie("images/vault-tec.gif")
        self.diag_gif.setMovie(self.diag_movie)

        self.diag_movie.setScaledSize(QSize(160, 110))

        diagnostics_layout.addWidget(self.diag_gif)
        diagnostics_layout.addWidget(self.diag_label)

        self.diag_movie.start()

         
        self.stat_stack.addWidget(self.status_page)
        self.stat_stack.addWidget(self.connect_page)
        self.stat_stack.addWidget(self.diagnosticcs_page)


        # Submenu 
        self.status = QPushButton("STATUS")
        self.connect = QPushButton("CONNECT")
        self.diagnosticcs = QPushButton("DIAGNOSTICS")

        for btn in [self.status, self.connect, self.diagnosticcs]:
            btn.setCheckable(True)
            btn.setProperty("class", "subnav")
            btn.clicked.connect(self.play_subnav_sound)
        

        # Buttons
        submenu_layout = QHBoxLayout()
        submenu_layout.addWidget(self.status)
        submenu_layout.addWidget(self.connect)
        submenu_layout.addWidget(self.diagnosticcs)
        submenu_layout.addStretch()

    
        stat_layout.addLayout(submenu_layout)
        stat_layout.addWidget(self.stat_stack)


        self.stat_group = QButtonGroup(self)
        self.stat_group.setExclusive(True)

        self.stat_group.addButton(self.status)
        self.stat_group.addButton(self.connect)
        self.stat_group.addButton(self.diagnosticcs)

        self.status.clicked.connect(self.show_status_page)

        self.connect.clicked.connect(self.show_connect_page)
         

        self.diagnosticcs.clicked.connect(
            lambda: self.stat_stack.setCurrentIndex(2)
        )

        # Default page
        self.status.setChecked(True)
        self.show_status_page()
#----------inv------------
        self.inv = QPushButton("INV", self)
        self.inv_page = QWidget()
        self.inv.clicked.connect(self.inv_click)

        inv_layout = QVBoxLayout(self.inv_page)

        self.inv_stack = QStackedWidget()

        self.attachments_page = QWidget()
        self.apparel_page = QWidget()
        self.aid_page = QWidget()

        attachments_layout = QHBoxLayout(self.attachments_page)
        apparel_layout = QVBoxLayout(self.apparel_page)
        self.aid_layout = QVBoxLayout(self.aid_page)

        #attachments
        self.attachments_main = QWidget()
        self.attachments_stack = QStackedWidget()
        attacments_main_layout = QVBoxLayout(self.attachments_main)
        
        self.rads = QPushButton("RAD METER", self)
        self.rads.setStyleSheet(""" background-color:rgba(0,200,0,0.4);
                                padding-left:10px;
                                padding-right:20px;
                                border: 1px solid rgb(0,200,0);
                                color: #00ee00;
                                margin-left:0;
                                """)
        self.rads.setFixedWidth(250)
        self.rads_img = QLabel()
        self.rads_img.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("images/rad.png")
        pixmap = pixmap.scaled(210, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.rads_img.setPixmap(pixmap)
        self.rads_img.setScaledContents(True)
        self.rads_img.setFixedSize(100,90)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.rads)
        button_layout.addSpacing(10)         
        button_layout.addWidget(self.rads_img)
        attacments_main_layout.addLayout(button_layout)
        
        
        self.rads_page = QWidget()
        
        
        self.attachments_gif = QLabel()
        self.attachments_gif.setAlignment(Qt.AlignCenter)
        self.attachments_movie = QMovie("images/rads2.gif")
        self.attachments_gif.setMovie(self.attachments_movie)
        self.attachments_movie.setScaledSize(QSize(250, 140))
        self.attachments_gif.setAlignment(Qt.AlignCenter)
        
        rad_layout = QVBoxLayout(self.rads_page)
        rad_layout.setContentsMargins(0, 0, 0, 0)

        rad_layout.addStretch()
        rad_layout.addWidget(
            self.attachments_gif,
            0,
            Qt.AlignCenter
        )
        self.attachments_stack.addWidget(self.attachments_main)
        self.attachments_stack.addWidget(self.rads_page)
        attachments_layout.addWidget(self.attachments_stack)
        self.rads.clicked.connect(self.show_rad_meter)

        self.attachments_movie.start()



        #apparel 
        self.apparel_img = QLabel()
        self.apparel_img.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("images/apparel.png")
        pixmap = pixmap.scaled(210, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.apparel_img.setPixmap(pixmap)
        self.apparel_img.setScaledContents(True)
        self.apparel_img.setFixedSize(190,150)
        
        apparel_layout.addWidget(self.apparel_img, alignment=Qt.AlignCenter)

        #aid
        self.aid_gifs = ["images/33.gif", "images/32.gif"]
        self.aid_gif = QLabel()
        self.aid_gif.setAlignment(Qt.AlignCenter)

        # Add pages to stack
        self.inv_stack.addWidget(self.attachments_page)
        self.inv_stack.addWidget(self.apparel_page)
        self.inv_stack.addWidget(self.aid_page)

        # Submenu buttons
        self.attachments = QPushButton("ATTACHMENTS")
        self.apparel = QPushButton("APPAREL")
        self.aid = QPushButton("AID")

        for btn in [self.attachments, self.apparel, self.aid]:
            btn.setCheckable(True)
            btn.setProperty("class", "subnav")
            btn.clicked.connect(self.play_subnav_sound)

        # Button row
        inv_submenu_layout = QHBoxLayout()
        inv_submenu_layout.addWidget(self.attachments)
        inv_submenu_layout.addWidget(self.apparel)
        inv_submenu_layout.addWidget(self.aid)
        inv_submenu_layout.addStretch()

        # Main layout
        inv_layout.addLayout(inv_submenu_layout)
        inv_layout.addWidget(self.inv_stack)

        self.inv_group = QButtonGroup(self)
        self.inv_group.setExclusive(True)

        self.inv_group.addButton(self.attachments)
        self.inv_group.addButton(self.apparel)
        self.inv_group.addButton(self.aid)

        # Page switching
        self.attachments.clicked.connect(
            lambda: self.inv_stack.setCurrentIndex(0)
        )

        self.apparel.clicked.connect(
            lambda: self.inv_stack.setCurrentIndex(1)
        )
        self.apparel.clicked.connect(self.hide_rad_meter)

        self.aid.clicked.connect(self.show_aid_page)

        # Default page
        self.show_attachments_page()
        self.attachments.setChecked(True)
#----------data------------
        self.data = QPushButton("DATA", self)
        self.data_page = QWidget()

        data_layout = QVBoxLayout(self.data_page)

        self.data_stack = QStackedWidget()

        self.clock_page = QWidget()
        self.stats_page = QWidget()
        self.maintenence_page = QWidget()

        self.data_stack.addWidget(self.clock_page)
        self.data_stack.addWidget(self.stats_page)
        self.data_stack.addWidget(self.maintenence_page)

        clock_layout = QHBoxLayout(self.clock_page)
        self.stats_layout = QVBoxLayout(self.stats_page)
        maintenence_layout = QHBoxLayout(self.maintenence_page)

        self.clock = QPushButton("CLOCK")
        self.stats = QPushButton("STATS")
        self.maintenence = QPushButton("MAINTENENCE")

        for btn in [self.clock, self.stats, self.maintenence]:
            btn.setCheckable(True)
            btn.setProperty("class", "subnav")
            btn.clicked.connect(self.play_subnav_sound)

        #----clock----
        self.clock_gif = QLabel()
        self.clock_gif.setAlignment(Qt.AlignCenter)

        self.clock_movie = QMovie("images/vaultboy.gif")
        self.clock_gif.setMovie(self.clock_movie)
        self.clock_gif.setFixedSize(120, 136)
        self.clock_movie.setScaledSize(QSize(110, 136))

        clock_layout.addWidget(self.clock_gif)

        self.clock_movie.start()

        self.clock_label = QLabel(self.current_time.toString('hh:mm'))
        self.clock_label.setStyleSheet("""
                        font-size:100px;
            """)
        self.clock_label.setAlignment(Qt.AlignCenter)
        clock_layout.addWidget(self.clock_label)

        #----stats----
        self.stats_gifs = ["images/approved.gif", "images/close-doors.gif"]
        self.stats_gif = QLabel()
        self.stats_gif.setAlignment(Qt.AlignCenter)

        #----maintenence----

        self.maintenence_button = QPushButton("BEGIN MAINTENENCE", self)
        maintenence_layout.addWidget(self.maintenence_button)
        self.maintenence_button.setStyleSheet(""" background-color:rgba(0,200,0,0.4);
                                padding-left:10px;
                                padding-right:10px;
                                border: 1px solid rgb(0,200,0);
                                color: #00ee00;
                                """)
        self.maintenence_button.setFixedWidth(250)
        self.maintenence_img = QLabel()
        self.maintenence_img.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("images/pipboy.png")
        pixmap = pixmap.scaled(210, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.maintenence_img.setPixmap(pixmap)
        self.maintenence_img.setScaledContents(True)
        self.maintenence_img.setFixedSize(100,90)
        maintenence_layout.addWidget(self.maintenence_img)
        self.maintenence_button.clicked.connect(self.show_game)

        



        data_submenu_layout = QHBoxLayout()
        data_submenu_layout.addWidget(self.clock)
        data_submenu_layout.addWidget(self.stats)
        data_submenu_layout.addWidget(self.maintenence)
        data_submenu_layout.addStretch()

        data_layout.addLayout(data_submenu_layout)
        data_layout.addWidget(self.data_stack)

        self.data_group = QButtonGroup(self)
        self.data_group.setExclusive(True)

        self.data_group.addButton(self.clock)
        self.data_group.addButton(self.stats)
        self.data_group.addButton(self.maintenence)

        self.clock.clicked.connect(
            lambda: self.data_stack.setCurrentIndex(0)
        )

        self.stats.clicked.connect(self.show_stats_page)

        self.maintenence.clicked.connect(
            lambda: self.data_stack.setCurrentIndex(2)
        )

        # Default page
        self.clock.setChecked(True)
        self.data_stack.setCurrentIndex(0)

        self.data.clicked.connect(self.data_click)

#----------map------------
        self.map = QPushButton("MAP", self)
        self.map_page = QWidget()
        map_layout = QHBoxLayout(self.map_page)
        self.map.clicked.connect(self.map_click)
       

        try:
            
            coordinates = (34.010090, -118.496948)
            m = folium.Map(
                title = 'Vault 33',
                zoom_start=7,
                location=coordinates,
                tiles="CartoDB dark_matter",
                zoom_control=False,
                attribution_control=False
                )
            #save map data
            data = io.BytesIO()
            m.save(data, close_file=False)

            #display map
            webView = QWebEngineView()
            map_layout.addWidget(webView)
            html = data.getvalue().decode()
            html = html.replace(
                "</head>",
                """
                <style>
                .leaflet-tile {
                    filter:
                        grayscale(100%)
                        sepia(100%)
                        hue-rotate(50deg)
                        saturate(900%);
                }

                body {
                    background: black;
                }
                </style>
                </head>
                """
            )
            webView.setHtml(html)
        except:
            self.map_img = QLabel()
            self.map_img.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap("images/map.png")
            pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.map_img.setPixmap(pixmap)
            self.map_img.setFixedSize(400,300)
            map_layout.addWidget(self.map_img)






#----------radio------------
        self.radio = QPushButton("RADIO", self)
        self.radio_page = QWidget()
        self.radio.clicked.connect(self.radio_click)

        radio_layout = QHBoxLayout(self.radio_page)
        self.radio_button = QPushButton("Play Radio", self)
        radio_layout.addWidget(self.radio_button)
        self.radio_button.setStyleSheet(""" background-color:rgba(0,200,0,0.4);
                                padding-left:10px;
                                padding-right:20px;
                                border: 1px solid rgb(0,200,0);
                                color: #00ee00;
                                """)
        self.radio_button.setFixedWidth(250)
        self.radio_img = QLabel()
        self.radio_img.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("images/radio.jpeg")
        pixmap = pixmap.scaled(290, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.radio_img.setPixmap(pixmap)
        self.radio_img.setScaledContents(True)
        self.radio_img.setFixedSize(160,160)
        radio_layout.addWidget(self.radio_img)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        music_folder = os.path.join(BASE_DIR, "music")
        self.radio_playlist = []

        for filename in sorted(os.listdir(music_folder)):
            if filename.lower().endswith((".wav")):
                path = os.path.join(music_folder, filename)
                self.radio_playlist.append(pygame.mixer.Sound(path))

                
        self.radio_button.clicked.connect(self.play_radio)



#pages
        self.pages.addWidget(self.stat_page)   
        self.pages.addWidget(self.inv_page)   
        self.pages.addWidget(self.data_page)   
        self.pages.addWidget(self.map_page)  
        self.pages.addWidget(self.radio_page) 

       

#----------bottom bar------------
        self.left_bottom = QLabel()
        self.middle_bottom = QLabel()
        self.right_bottom = QLabel()
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 0px;border-right: 0px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setFixedHeight(10)
        self.battery_bar.setFixedWidth(100)
        self.battery_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgb(0,238,0);
                text-align: center;
                background-color:black;
                color:black;
                font-family:monofonto;
                font-size:10px;
                height:5px;
            }
            QProgressBar::chunk {
                background-color: rgb(0,238,0);
                width: 10px;
            }
        """)
        try:
            self.battery = psutil.sensors_battery()
            percent = self.battery.percent if self.battery else 100
        except:
            percent = 100

        self.battery_bar.setValue(percent)

        self.calendar()
        timer = QTimer(self)
        timer.timeout.connect(self.calendar)
        timer.start(500)

        bottom = QHBoxLayout()
        bottom_bar = QWidget()
        bottom_bar.setStyleSheet("background-color: rgb(0, 50, 0);color: rgb(0,255,0);")

        bottom = QHBoxLayout(bottom_bar)
        bottom.setSpacing(10)
        bottom.setContentsMargins(5, 0, 5, 0)
        bottom.setAlignment(Qt.AlignLeft)

#----------nav------------    
        top = QHBoxLayout()
        top.setSpacing(0)
        top.setContentsMargins(0, 0, 0, 0)
        top.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        vertical_layout = QVBoxLayout()

        self.nav_btns = [self.stat, self.inv, self.data, self.map, self.radio]

#----------layout------------    
        group = QButtonGroup(self)
        group.setExclusive(True)

        group.addButton(self.stat)
        group.addButton(self.inv)
        group.addButton(self.data)
        group.addButton(self.map)
        group.addButton(self.radio)

        top.addWidget(settings)

        for btn in [self.stat, self.inv, self.data, self.map, self.radio]:
            btn.setProperty("class", "nav")
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setCheckable(True)
            top.addWidget(btn)
        
        
        top.addWidget(battery)

        bottom.addWidget(self.left_bottom)
        bottom.addWidget(self.middle_bottom)
        bottom.addWidget(self.battery_bar)
        bottom.addStretch()
        bottom.addWidget(self.right_bottom)

        
        
        vertical_layout.addLayout(top)
        vertical_layout.addWidget(self.pages)
        vertical_layout.addWidget(bottom_bar)
        # vertical_layout.addWidget(picture)
        self.data.setChecked(True)
        self.clock.setChecked(True)
        self.pages.setCurrentIndex(2)
        self.status.setChecked(True)
        central_widget.setLayout(vertical_layout)

        self.scanlines = QLabel(self)
        self.scanlines.setGeometry(0, 0, 480, 480)
        self.scanlines.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )
        self.scanline_movie = QMovie("images/scanline.gif")
        self.scanlines.setMovie(self.scanline_movie)

        self.scanline_movie.start()
        self.scanline_movie.setSpeed(250)

        self.scanlines.raise_()
        opacity = QGraphicsOpacityEffect()
        opacity.setOpacity(0.1) 

        self.scanlines.setGraphicsEffect(opacity)

        try:
            encoder.when_rotated = lambda: QTimer.singleShot(0, self.rotary_1_spin)
        except:
            pass
        try:
            encoder_2.when_rotated = lambda: QTimer.singleShot(0, self.rotary_2_spin)
        except:
            pass
        self.button_timer = QTimer()
        self.button_timer.timeout.connect(self.check_button)
        self.button_timer.start(20)
        
    def calendar(self):
        date = QDate.currentDate()
        # self.battery = psutil.sensors_battery()
        # date = date.addYears(270)
        self.current_time = QTime.currentTime()
        if(self.pages.currentIndex() == 2 or self.pages.currentIndex() == 3 ):
            self.left_bottom.setText(self.current_time.toString('hh:mm') + "  "+ "2296-"+ date.toString('MM-dd'))
            if(self.pages.currentIndex() == 3 ):
                self.clock_label.setText(self.current_time.toString('hh:mm'))
           
            

    def stat_click(self):
        self.stop_radio()
        self.hide_rad_meter()
        self.pages.setCurrentIndex(0)
        self.status.setChecked(True)
        self.show_status_page()
        self.left_bottom.setText("HP " + str(self.hp) + "/" + str(self.totalhp))
        self.middle_bottom.setText("Level 33")
        self.right_bottom.setText("")
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.nav_click.play()
        self.static_short.play()
        self.battery_bar.show()

    def inv_click(self):
        self.stop_radio()
        self.pages.setCurrentIndex(1)
        self.clock.setChecked(True)
        self.show_attachments_page()
        # self.left_bottom.setText("<img src='images/thing.png' width='15' height='15' style='margin-bottom:2px;'> 384/-1")
        self.left_bottom.setText("<img src='images/cap.png' width='15' height='15' style='margin-bottom:2px;'> 10000000+")
        self.middle_bottom.setText("")
        self.right_bottom.setText("<img src='images/gun.png' width='35' height='15' style='margin-bottom:2px;'>18")
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 0px;border-right: 0px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.static.play()
        self.nav_click.play()
        self.battery_bar.show()
    
    def data_click(self):
        self.stop_radio()
        self.hide_rad_meter()
        self.calendar()
        self.pages.setCurrentIndex(2)
        self.clock.setChecked(True)
        self.data_stack.setCurrentIndex(0)
        self.right_bottom.setText("")
        self.middle_bottom.setText("")
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 0px;border-right: 0px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.battery_bar.show()
        
        self.nav_click.play()
    def map_click(self):
        self.stop_radio()
        self.hide_rad_meter()
        self.calendar()
        self.pages.setCurrentIndex(3)
        self.middle_bottom.setText("")
        self.right_bottom.setText("<span style='background-color:rgb(0,238,0); color:black;'>LOCAL MAP</span>")
        self.nav_click.play()
        self.static.play()
        self.map_click_sound.play()
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 0px;border-right: 0px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.battery_bar.show()
    def radio_click(self):
        self.hide_rad_meter()
        self.pages.setCurrentIndex(4)
        # self.left_bottom.setText("")
        # self.middle_bottom.setText("")
        # self.right_bottom.setText("")
        self.nav_click.play()
        self.static.play()
        # self.left_bottom.setStyleSheet("padding-right: 10px;border-right: none;")
        # self.middle_bottom.setStyleSheet("padding-right: 10px;border-right:none;")
        # self.right_bottom.setStyleSheet("padding-right: 10px;")
        # self.battery_bar.hide()
        self.clock.setChecked(True)
        self.right_bottom.setText("")
        self.middle_bottom.setText("")
        self.left_bottom.setStyleSheet("padding-right: 10px;border-right: 2px solid rgb(0,0,0);")
        self.middle_bottom.setStyleSheet("padding-right: 0px;border-right: 0px solid rgb(0,0,0);")
        self.right_bottom.setStyleSheet("padding-right: 10px;")
        self.battery_bar.show()

    def show_status_page(self):
        self.stat_stack.setCurrentIndex(0)
        self.stat.setChecked(True)

        self.connect_movie.stop()

        self.status_movie.stop()
        self.status_movie.jumpToFrame(0)
        self.status_movie.start()

    def show_connect_page(self):
        self.connect.setChecked(True)
        self.stat_stack.setCurrentIndex(1)

        self.status_movie.stop()

        self.connect_movie.stop()
        self.connect_movie.jumpToFrame(0)
        self.connect_movie.start()

    def show_attachments_page(self):
        self.attachments.setChecked(True)
        self.attachments_stack.setCurrentWidget(self.attachments_main)
        self.inv_stack.setCurrentIndex(0)

    def show_rad_meter(self):
        self.attachments_movie.start()
        self.attachments_stack.setCurrentWidget(self.rads_page)
        self.rads_sound.play(-1)
        try: 
            led_rads.on()
        except:
            pass
    def hide_rad_meter(self):
        self.attachments_movie.stop()

        self.rads_sound.stop()

        self.attachments_stack.setCurrentWidget(
            self.attachments_main
        )
        try:
            led_rads.off()
        except:
            pass


    
    def show_aid_page(self):
        self.hide_rad_meter()
        i = randint(0, len(self.aid_gifs)-1)
        self.aid_movie = QMovie(self.aid_gifs[i])
        self.aid_gif.setMovie(self.aid_movie)
        self.aid_movie.setScaledSize(QSize(190, 130))

        self.aid_layout.addWidget(self.aid_gif)
        self.aid_movie.start()
        self.inv_stack.setCurrentIndex(2)

    def show_game(self):
        self.button_timer.stop()
        self.process = subprocess.Popen([sys.executable, "jumpgame.py"])
        self.game_running = True

    def end_game(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()

        self.game_running = False
        self.button_timer.start(20)
        self.process = None
        

    def show_stats_page(self):
        i = randint(0, len(self.stats_gifs)-1)
        self.stats_movie = QMovie(self.stats_gifs[i])
        self.stats_gif.setMovie(self.stats_movie)
        self.stats_movie.setScaledSize(QSize(200, 130))

        self.stats_layout.addWidget(self.stats_gif)
        self.stats_movie.start()
        self.data_stack.setCurrentIndex(1)

    def play_subnav_sound(self):
        self.subnav_click.play()
    
    def play_radio(self):
        self.stop_radio()
        i = randint(0, len(self.radio_playlist) - 1)
        self.current_song = self.radio_playlist[i]
        self.current_song.play()
    def stop_radio(self):
        try: 
            self.current_song.stop()
        except:
            pass

    


    def rotary_1_spin(self):
        steps = encoder.steps
        index = self.pages.currentIndex()
        if self.game_running is True:
            self.end_game()
            self.game_running = False
            return
            
        if steps > self.rotary_value:
            index = (index + 1) % 5
        else:
            index = (index - 1) % 5
        self.nav_btns[index].click()
        self.rotary_value = steps
    
    def rotary_2_spin(self):
        steps = encoder_2.steps
        if self.game_running is True:
            self.end_game()
            self.game_running = False
            return

        if self.pages.currentIndex() == 0:
            index = self.stat_stack.currentIndex()
            page = self.stat_stack
            btns = self.stat_group.buttons()
        elif self.pages.currentIndex() == 1:
            index = self.inv_stack.currentIndex()
            page = self.inv_stack
            btns = self.inv_group.buttons()
        elif self.pages.currentIndex() == 2:
            index = self.data_stack.currentIndex()
            page = self.data_stack
            btns = self.data_group.buttons()
        else:
            return
        count = page.count()
        if steps > self.rotary_2_value:
            index = (index + 1) % count
        else:
            index = (index - 1) % count
        btns[index].click() 
        self.rotary_2_value = steps
    def check_button(self):
        if button is None:
            return 
        if self.game_running is True:
            return
        if button.is_pressed:
            if self.pages.currentIndex()== 1 and self.inv_stack.currentIndex()==0:
                self.rads.click()
            elif self.pages.currentIndex() == 2 and self.data_stack.currentIndex() == 2:
                self.maintenence_button.click()
            elif self.pages.currentIndex() == 4:
                self.radio_button.click()




class Bootup(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(480,320)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint)
        layout = QVBoxLayout(self)
        self.label_anim = QLabel(self)
        self.setStyleSheet("background-color: black")
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.files = [
            os.path.join(BASE_DIR, "audio/bootupa.mp3"),
            os.path.join(BASE_DIR, "audio/bootupa.mp3"),
            os.path.join(BASE_DIR, "audio/bootupb.mp3"),
            os.path.join(BASE_DIR, "audio/bootupb.mp3"),
            os.path.join(BASE_DIR, "audio/bootupc.mp3"),
        ]
        self.current = 0
        
        

        self.movie= QMovie("images/bootup.gif")
        self.label_anim.setMovie(self.movie)
        self.label_anim.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_anim)
        timer = QTimer(self)
        self.play_next()
        self.movie.setSpeed(100)
        timer.singleShot(200, self.startAnim)

        timer.singleShot(24000, self.endAnim) #change num if the animation repeats
        
        self.show()
        self.raise_()
        self.activateWindow()

    def startAnim(self):
        self.movie.start()
       
        
    def endAnim(self):
        self.movie.stop()
        self.close()
    def play_next(self):
        if self.current < len(self.files):
            pygame.mixer.music.load(self.files[self.current])
            pygame.mixer.music.play()
            self.current += 1
            QTimer.singleShot(5000, self.play_next)  # adjust timin



       
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
            QLabel, QPushButton[class="nav"] {
                font-size: 20px;
                color: rgb(0, 238, 0);
            }
            QPushButton {
                border: none;
                padding: 0px;
                color: rgb(0, 150, 0);
                margin-top:0px;
                background-color: rgba(0,0,0,0);
        }
            QPushButton:checked{
                      color: rgb(0, 238, 0);}
            

                QPushButton[class="nav"] {
            border: none;
            border-bottom: 1px solid rgb(0,255,0);
            padding: 6px 17px;
            
            margin-top: 10px;
            background-color: rgba(0,0,0,0);
        }

            QPushButton[class="nav"]:hover {
                background-color: rgba(0, 112, 0, 0.7);
            }
           QPushButton[class="nav"]:checked {
            border-bottom: none;
            border-top: 1px solid rgb(0,255,0);
            border-right: 1px solid rgb(0,255,0);
            border-left: 1px solid rgb(0,255,0);

            background-color: rgba(0,0,0,0);

        }
            """)
    app.setFont(QFont("Monofonto", 20), "QLabel")
    app.setFont(QFont("Monofonto", 20), "QPushButton")
    window = MainWindow()
    window.show()
    
   
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()

