#!/usr/bin/env python
import os
import sys
import base64
import jinja2
import logging
import traceback
from   PyQt5.Qt                 import Qt
from   PyQt5.QtWidgets          import * #QAction, QApplication, QComboBox, QColorDialog, QFileDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QSpinBox, QSlider, QShortcut, QDoubleSpinBox, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from   PyQt5.QtCore             import *
from   PyQt5.QtGui              import * #QIcon, QPixmap, QKeySequence
from   PyQt5.QtWebEngineWidgets import QWebEngineView     as QWebView,QWebEnginePage as QWebPage
from   PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings


ParameterLabelWidth = 100
logger = logging.getLogger('logger')
logger.addHandler(logging.FileHandler('debug.log'))
def exc_handler(exctype, value, tb):
	logger.exception(''.join(traceback.format_exception(exctype, value, tb)))
	sys.__excepthook__(exctype, value, tb)
sys.excepthook = exc_handler

class DashWidget(QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowTitle("POROTECH Animate control")
		self.setWindowIcon(PorotechIcon().icon)
		self.currentAnimatePath     = ""
		self.currentAnumateSetting  = None
		self.currentFloatWinSetting = None
		self.configPath             = "./config"
		self.fileOpenWidget         = FileOpenWidget()
		self.animateControlWidget   = AnimateControlWidget()
		self.testParameterWidget    = TestParameterWidget()
		self.statusBarWidget        = StatusBarWidget()
		self.h1                     = QHBoxLayout()
		self.v1                     = QVBoxLayout()
		self.v2                     = QVBoxLayout()
		
		self.h1.addWidget(self.fileOpenWidget)
		self.h1.addLayout(self.v1)
		self.v1.addWidget(self.animateControlWidget)
		self.v1.addWidget(self.testParameterWidget)
		self.v2.addLayout(self.h1)
		self.v2.addWidget(self.statusBarWidget)
		self.v2.setContentsMargins(0,0,0,0)
		self.setLayout(self.v2)
		self.initSignal()
		self.loadConfig()
		self.show()

	def initSignal(self):
		#self.fileOpenWidget.AnimateChoosed.connect(self.animateControlWidget.setDisplayAnimate)
		self.fileOpenWidget.AnimateChoosed.connect(self.testParameterWidget.readHTML)
		self.testParameterWidget.htmlChanged.connect(self.animateControlWidget.setDisplayAnimate)
		self.fileOpenWidget.setOpenFolder("./animation")
		self.animateControlWidget.animateWindow.onTopStatusChanged.connect(self.raise_)
		QShortcut(QKeySequence("Escape"), self, activated = self.on_Escape)
		QShortcut(QKeySequence("F11"),    self, activated = self.on_F11)
		QShortcut(QKeySequence("F12"),    self, activated = self.on_F12)

	@pyqtSlot()
	def on_Escape(self):
		self.animateControlWidget.animateWindow.show() if self.animateControlWidget.animateWindow.isHidden() else self.animateControlWidget.animateWindow.hide()

	@pyqtSlot()
	def on_F11(self):
		self.animateControlWidget.animateWindow.setOnTop(not(self.animateControlWidget.animateWindow.onTopStatus()))

	@pyqtSlot()
	def on_F12(self):
		self.animateControlWidget.animateWindow.show() if self.animateControlWidget.animateWindow.isHidden() else self.animateControlWidget.animateWindow.hide()


	def loadConfig(self):
		try:
			if os.path.isfile(self.configPath):
				with open(self.configPath) as f:
					for command in f.readlines():
						eval(command)
		except:
			print("cannot load config file")

	def updateConfig(self):
		with open(self.configPath, 'w') as f:
			f.write("self.animateControlWidget.setValues(%s)" % self.animateControlWidget.getValues())


	def closeEvent(self, event):
		self.updateConfig()
		self.animateControlWidget.animateWindow.close()

		event.accept()

class StatusBarWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.lockStatue  = False
		self.h1          = QHBoxLayout()
		self.lockButton  = QPushButton("Lock")
		self.statusLabel = QLabel("[lock status]")
		self.footerLabel = QLabel("POROTECH 2022")

		self.statusLabel.setFixedHeight(16)
		self.footerLabel.setFixedHeight(16)
		self.lockButton.setFixedHeight(16)
		self.lockButton.setFixedWidth(16)

		self.footerLabel.setAlignment(Qt.AlignRight)

		self.h1.setContentsMargins(0,0,0,0)
		self.h1.addWidget(self.lockButton)
		self.h1.addWidget(self.statusLabel)
		self.h1.addWidget(self.footerLabel)

		self.setLayout(self.h1)

class FileOpenWidget(QWidget):
	FilePathChoosed = pyqtSignal(str)
	AnimateChoosed  = pyqtSignal(str)
	def __init__(self):
		super().__init__()
		self.filePathLabel    = QLabel("Animate file path:")
		self.filePathEdit     = QLineEdit()
		self.fileBrowseButtom = QPushButton("Open")
		self.fileAnimateList  = QListWidget()
		self.h1               = QHBoxLayout()
		self.h2               = QHBoxLayout()
		self.v1               = QVBoxLayout()
		self.v1.addLayout(self.h1)
		self.v1.addLayout(self.h2)
		self.h1.addWidget(self.filePathLabel)
		self.h2.addWidget(self.filePathEdit)
		self.h2.addWidget(self.fileBrowseButtom)
		self.v1.addWidget(self.fileAnimateList)

		self.fileBrowseButtom.clicked.connect(self.browseClicked)
		self.setLayout(self.v1)
		self.initSignal()


	def initSignal(self):
		self.fileAnimateList.clicked.connect(lambda i : self.AnimateChoosed.emit(self.fileAnimateList.item(i.row()).path))

	def browseClicked(self):
		filePath = QFileDialog.getExistingDirectory (self, "Open Folder", ".", options=QFileDialog.ShowDirsOnly)
		self.setOpenFolder(filePath)

	def setOpenFolder(self, filePath):
		if filePath :
			self.fileAnimateList.clear()
			filePath = os.path.abspath(filePath).replace("\\", "/")
			self.FilePathChoosed.emit(filePath)
			self.filePathEdit.setText(filePath)
			for fileName in sorted(os.listdir(filePath)):
				fullPath = filePath + "/" + fileName
				fileType = fileName.rsplit('.', 1)[-1]

				if os.path.isfile(fullPath) and fileType.lower() == "html":
					self.fileAnimateList.addItem(AnimateListItem(fileName.rsplit('.', 1)[0], fullPath))
			self.AnimateChoosed.emit(self.fileAnimateList.item(0).path)

class AnimateListItem(QListWidgetItem):
	def __init__(self, text, path):
		super().__init__(text)
		self.path = path

class AnimateControlWidget(QWidget):

	def __init__(self):
		super().__init__()
		self.animateWindow    = AnimateWindow()
		self.moveCenterButtom = WindowControlPushButtom("")
		self.moveLeftButtom   = WindowControlPushButtom("←")
		self.moveRightButtom  = WindowControlPushButtom("→")
		self.moveUpButtom     = WindowControlPushButtom("↑")
		self.moveDownButtom   = WindowControlPushButtom("↓")

		self.moveULButtom     = WindowControlPushButtom("↖")
		self.moveURButtom     = WindowControlPushButtom("↗")
		self.moveDLButtom     = WindowControlPushButtom("↙")
		self.moveDRButtom     = WindowControlPushButtom("↘")

		self.widthIncButtom   = WindowControlPushButtom("◁ ▷")
		self.widthDecButtom   = WindowControlPushButtom("▷ ◁")
		self.heightIncButtom  = WindowControlPushButtom("▷")
		self.heightDecButtom  = WindowControlPushButtom("◁")
		self.posXSpin         = QSpinBox()
		self.posYSpin         = QSpinBox()
		self.posWSpin         = QSpinBox()
		self.posHSpin         = QSpinBox()
		self.posControlLayout = QGridLayout()
		self.posSpinLayout    = QGridLayout()
		self.mainLayout       = QVBoxLayout()
		self.hotKeyF11Combo   = QComboBox()
		self.hotKeyF12Combo   = QComboBox()
		self.posXLabel 		  = QLabel("Window location X")
		self.posYLabel		  = QLabel("Window location Y")
		self.posWLabel        = QLabel("Window Width")
		self.posHLabel        = QLabel("Window Height")
		self.hotKeyLabelF11   = QLabel("[F11] Always on top")
		self.hotKeyLabelF12   = QLabel("[F12] Show window")

		self.moveCenterButtom.setDisabled(True)
		self.hotKeyF11Combo.addItems(["True", "False"])
		self.hotKeyF12Combo.addItems(["True", "False"])

		self.posControlArray  = [
			[  self.moveULButtom,     self.moveUpButtom,    self.moveURButtom], 
			[self.moveLeftButtom, self.moveCenterButtom, self.moveRightButtom],
			[  self.moveDLButtom,   self.moveDownButtom,    self.moveDRButtom]
		]

		self.posSpinArray     = [
			[ self.hotKeyLabelF11, self.hotKeyF11Combo],
			[ self.hotKeyLabelF12, self.hotKeyF12Combo],
			[      self.posXLabel,       self.posXSpin],
			[      self.posYLabel,       self.posYSpin],
			[      self.posWLabel,       self.posWSpin],
			[      self.posHLabel,       self.posHSpin],
		]
		
		self.posXSpin.setAlignment(Qt.AlignCenter)
		self.posYSpin.setAlignment(Qt.AlignCenter)
		self.posWSpin.setAlignment(Qt.AlignCenter)
		self.posHSpin.setAlignment(Qt.AlignCenter)



		self.posXSpin.setMaximum(4000)
		self.posYSpin.setMaximum(4000)
		self.posWSpin.setMaximum(4000)
		self.posHSpin.setMaximum(4000)
		self.posWSpin.setMinimum(1)
		self.posHSpin.setMinimum(1)

		if ParameterLabelWidth:
			self.posXLabel.setFixedWidth(ParameterLabelWidth)
			self.posYLabel.setFixedWidth(ParameterLabelWidth)
			self.posWLabel.setFixedWidth(ParameterLabelWidth)
			self.posHLabel.setFixedWidth(ParameterLabelWidth)
			self.hotKeyLabelF11.setFixedWidth(ParameterLabelWidth)
			self.hotKeyLabelF12.setFixedWidth(ParameterLabelWidth)

		self.posXSpin.valueChanged.connect(lambda val : self.setDisplayX(val, False))
		self.posYSpin.valueChanged.connect(lambda val : self.setDisplayY(val, False))
		self.posWSpin.valueChanged.connect(lambda val : self.setDisplayW(val, False))
		self.posHSpin.valueChanged.connect(lambda val : self.setDisplayH(val, False))
		self.hotKeyF11Combo.currentIndexChanged.connect(lambda val : self.setDisplayOntop ([True, False][val]))
		self.hotKeyF12Combo.currentIndexChanged.connect(lambda val : self.setDisplayVisibility ([True, False][val]))

		self.populateGrid(self.posControlLayout, self.posControlArray)
		self.populateGrid(   self.posSpinLayout,    self.posSpinArray)

		self.posControlHLayout = QHBoxLayout()
		self.addHotkeyLayout   = QVBoxLayout()
		self.posSpinVLayout    = QVBoxLayout()

		self.posControlHLayout.addStretch()
		self.posControlHLayout.addLayout(self.posControlLayout)
		self.posControlHLayout.addStretch()
		self.posSpinVLayout.addSpacing(25)
		self.posSpinVLayout.addLayout(self.posSpinLayout)
		self.posSpinVLayout.addStretch()

		self.mainLayout.addLayout(self.posControlHLayout)
		self.mainLayout.addLayout(self.addHotkeyLayout)
		self.mainLayout.addLayout(self.posSpinVLayout)

		self.moveLeftButtom.clicked.connect ( lambda : self.setDisplayX( self.animateWindow.pos().x() - 1))
		self.moveRightButtom.clicked.connect( lambda : self.setDisplayX( self.animateWindow.pos().x() + 1))
		self.moveUpButtom.clicked.connect   ( lambda : self.setDisplayY( self.animateWindow.pos().y() - 1))
		self.moveDownButtom.clicked.connect ( lambda : self.setDisplayY( self.animateWindow.pos().y() + 1))

		self.moveULButtom.clicked.connect   ( lambda : self.setDisplayXY(self.animateWindow.pos().x() - 1, self.animateWindow.pos().y() - 1))
		self.moveDLButtom.clicked.connect   ( lambda : self.setDisplayXY(self.animateWindow.pos().x() - 1, self.animateWindow.pos().y() + 1))
		self.moveURButtom.clicked.connect   ( lambda : self.setDisplayXY(self.animateWindow.pos().x() + 1, self.animateWindow.pos().y() - 1))
		self.moveDRButtom.clicked.connect   ( lambda : self.setDisplayXY(self.animateWindow.pos().x() + 1, self.animateWindow.pos().y() + 1))

		self.widthDecButtom.clicked.connect ( lambda : self.setDisplayW( self.animateWindow.width()   - 1))
		self.widthIncButtom.clicked.connect ( lambda : self.setDisplayW( self.animateWindow.width()   + 1))
		self.heightDecButtom.clicked.connect( lambda : self.setDisplayH( self.animateWindow.height()  - 1))
		self.heightIncButtom.clicked.connect( lambda : self.setDisplayH( self.animateWindow.height()  + 1))

		self.setDisplayXY(  0,   0)
		self.setDisplayWH(105, 105)
		self.setLayout(self.mainLayout)

	def populateGrid(self, gridLayout, itemArray):
		for row in range(len(itemArray)):
			for column in range(len(itemArray[row])):
				item = itemArray[row][column]
				if item:
					gridLayout.addWidget(item, row, column)

	def setDisplayAnimate(self, filePath):
		self.animateWindow.setDisplayAnimate(filePath)
		self.animateWindow.show()

	def setDisplayXYWH(self, valX : int, valY : int, valW : int, valH : int, updateSpinBox : bool = True ):
		self.setDisplayX(valX, updateSpinBox)
		self.setDisplayY(valY, updateSpinBox)
		self.setDisplayW(valW, updateSpinBox)
		self.setDisplayH(valH, updateSpinBox)
		self.animateWindow.show()

	def setDisplayXY(self, valX : int, valY : int, updateSpinBox : bool = True ):
		self.setDisplayX(valX, updateSpinBox)
		self.setDisplayY(valY, updateSpinBox)
		self.animateWindow.show()

	def setDisplayWH(self, valW : int, valH : int, updateSpinBox : bool = True ):
		self.setDisplayW(valW, updateSpinBox)
		self.setDisplayH(valH, updateSpinBox)
		self.animateWindow.show()

	def setDisplayX(self, val : int, updateSpinBox : bool = True ):
		self.animateWindow.setDisplayX(val)
		if updateSpinBox:
			self.posXSpin.setValue(val)
			self.animateWindow.show()

	def setDisplayY(self, val : int, updateSpinBox : bool = True ):
		self.animateWindow.setDisplayY(val)
		if updateSpinBox:
			self.posYSpin.setValue(val)
			self.animateWindow.show()

	def setDisplayW(self, val : int, updateSpinBox : bool = True ):
		self.animateWindow.setDisplayW(val)
		if updateSpinBox:
			self.posWSpin.setValue(val)
			self.animateWindow.show()

	def setDisplayH(self, val : int, updateSpinBox : bool = True ):
		self.animateWindow.setDisplayH(val)
		if updateSpinBox:
			self.posHSpin.setValue(val)
			self.animateWindow.show()

	def setDisplayOntop(self, val : bool, updateSpinBox : bool = True ):
		self.blockSignals(True)
		self.animateWindow.setOnTop(val)
		self.blockSignals(False)

	def setDisplayVisibility(self, val : bool, updateSpinBox : bool = True ):
		self.animateWindow.setDisplayVisibility(val)
		

	def getValues(self):
		return {
			"x"          : self.posXSpin.value(),
			"y"          : self.posYSpin.value(),
			"w"          : self.posWSpin.value(),
			"h"          : self.posHSpin.value(),
			"onTop"      : True if self.hotKeyF11Combo.currentIndex() == 0 else False,
			"visibility" : True if self.hotKeyF12Combo.currentIndex() == 0 else False,
		}


	def setValues(self, values : dict, internal : bool = False):
		self.blockSignals(internal)
		if "onTop" in values:
			self.setDisplayOntop(values["onTop"])

		if "visibility" in values:
			self.setDisplayVisibility(values["visibility"])

		if "x" in values:
			self.setDisplayX(values["x"])

		if "y" in values:
			self.setDisplayY(values["y"])

		if "w" in values:
			self.setDisplayW(values["w"])

		if "h" in values:
			self.setDisplayH(values["h"])
		self.blockSignals(not(internal))
		
	def closeEvent(self, event):
		self.animateWindow.close()
		event.accept()

class WindowControlPushButtom(QPushButton):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setAutoRepeat(True)
		self.setAutoRepeatInterval(5)
		self.setFixedSize(QSize(40, 40))
class BackgroundWindow(QMainWindow):
	onTopStatusChanged = pyqtSignal(bool)
	def __init__(self):
		super().__init__()

	def init_frameless(self):
		self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint  | Qt.SubWindow )
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		
class AnimateWindow(QMainWindow):
	onTopStatusChanged = pyqtSignal(bool)
	def __init__(self):
		super().__init__()
		self.status  = True
		self.display = AnimateWidget()
		self.setWindowTitle("POROTECH")
		self.setWindowIcon(PorotechIcon().icon)
		self.setCentralWidget (self.display)
		
		self.setContentsMargins(0, 0, 0, 0)
		self.setDisplayArea(0, 0, 105, 105)
		self.init_frameless()
		self.initSignal()
		self.show()

	def initSignal(self):
		self.display.visibilityChangeRqst.connect(lambda : self.hide())
		self.display.stayOnTopChangeRqst.connect(lambda : self.setOnTop(not(self.onTopStatus())))  
		QShortcut(QKeySequence("Escape"), self, activated = self.on_Escape)
		QShortcut(QKeySequence("F11"),    self, activated = self.on_F11)
		QShortcut(QKeySequence("F12"),    self, activated = self.on_F12)

	def init_frameless(self):
		self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint  | Qt.SubWindow )
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		
	@pyqtSlot()
	def on_Escape(self):
		self.show() if self.isHidden() else self.hide()

	@pyqtSlot()
	def on_F11(self):
		self.setOnTop(not(self.onTopStatus()))

	@pyqtSlot()
	def on_F12(self):
		self.show() if self.isHidden() else self.hide()


	def onTopStatus(self):
		return (self.windowFlags() & Qt.WindowStaysOnTopHint) == Qt.WindowStaysOnTopHint

	@pyqtSlot(bool)
	def setDisplayVisibility(self, status : bool):
		_ = self.show() if status else self.hide()
			

	@pyqtSlot(bool)
	def setOnTop(self, status : bool):
		if status:
			self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowStaysOnTopHint  | Qt.SubWindow )
		else:
			self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint )
		self.show()
		self.onTopStatusChanged.emit(status)


	def setDisplayArea(self, x : int, y : int, w : int, h : int):
		self.move(x, y)
		self.setFixedSize(QSize(w, h))
		self.display.setDisplaySize(w, h)

	def setDisplayAnimate(self, filePath):
		self.display.setDisplayAnimate(filePath)

	def setDisplayX(self, val : int):
		self.move(val, self.pos().y())

	def setDisplayY(self, val : int):
		self.move(self.pos().x(), val)

	def setDisplayW(self, val : int):
		val = val if val >= 1 else 1
		self.setFixedSize(QSize(val, self.height()))
		self.display.setDisplaySize(val, self.height())
		
	def setDisplayH(self, val : int):
		val = val if val >= 1 else 1
		self.setFixedSize(QSize(self.width(), val))
		self.display.setDisplaySize(self.width(), val)

	def getDisplayArea(self):
		pos  = self.pos()
		size = self.size()

		return {
			"x"          : pos.x(),
			"y"          : pos.y(),
			"w"          : self.width(),
			"h"          : self.height(),
			"onTop"      : self.onTopStatus(),
			"visibility" : False if self.isHidden() else True,
		}

class AnimateWidget(QWidget):
	visibilityChangeRqst = pyqtSignal()
	stayOnTopChangeRqst  = pyqtSignal()
	def __init__(self):
		super().__init__()
		self.animatePath = ""
		self.webView     = AnimateWebView()
		self.layout      = QHBoxLayout()
		self.setCursor(Qt.BlankCursor)
		self.layout.setContentsMargins(0,0,0,0)
		self.layout.addWidget(self.webView)
		self.setLayout(self.layout)
		self.webView.visibilityChangeRqst.connect(self.visibilityChangeRqst.emit)
		self.webView.stayOnTopChangeRqst.connect(self.stayOnTopChangeRqst.emit)

	def setDisplaySize(self, w : int, h : int):
		self.webView.setFixedSize(QSize(w, h))
		self.setDisplayAnimate(self.animatePath)

	def setDisplayAnimate(self, filePath):
		if os.path.isfile(filePath):
			self.webView.load(QUrl(filePath))
		else:
			self.webView.setHtml(filePath)
		self.animatePath = filePath

class AnimateWebView(QWebView):
	visibilityChangeRqst = pyqtSignal()
	stayOnTopChangeRqst  = pyqtSignal()
	def __init__(self, parent=None):
		super(AnimateWebView, self).__init__(parent)
		self.setStyleSheet("""
			QMenu{
				background-color : #333333;
				color            : #000000;
			}

			QMenu::item:selected{
				background-color : #000000;
				color            : #333333;
			}
			""")

	def contextMenuEvent(self, event):
		menu = self.page().createStandardContextMenu()
		menu.clear ()
		visibilityAction = QAction("[F12] hide/show",          self)
		stayOnTopAction  = QAction("[F11] toggle stay on top", self)
		visibilityAction.triggered.connect(self.visibilityChangeRqst.emit)
		stayOnTopAction.triggered.connect(self.stayOnTopChangeRqst.emit)
		menu.addAction (visibilityAction)
		menu.addAction (stayOnTopAction)
		menu.exec_(event.globalPos())

class TestParameterWidget(QWidget):
	htmlChanged = pyqtSignal(str)
	def __init__(self, filePath = ""):
		super().__init__()
		self.htmlTemplate     = ""
		self.htmlRendered     = ""
		#self.animateWindow    = AnimateWindow()
		self.itemArray        = []
		self.paramDict        = {}
		self.itemLayout       = QVBoxLayout()
		self.mainLayout       = QVBoxLayout()
		self.mainLayout.addLayout(self.itemLayout)
		self.mainLayout.addStretch()
		self.setLayout(self.mainLayout)
		#self.htmlChanged.connect(lambda html : self.animateWindow.setDisplayAnimate(html))
		self.readHTML(filePath)
		
	def readHTML(self, filePath):
		self.htmlTemplate     = ""
		self.htmlRendered     = ""
		self.itemArray        = []
		self.paramDict        = {}

		for i in reversed(range(self.itemLayout.count())): 
			self.itemLayout.itemAt(i).widget().setParent(None)

		if os.path.isfile(filePath):
			with open(filePath) as f:
				content = f.readlines()
				if "paramEnabled" in content[0]:
					for index in range(len(content)):
						line = content[index]
						if "/* parameter" in line:
							parameterArray   = line.replace("*/", "").split(";")
							declareSeparator = "=" if "=" in parameterArray[0] else ":"
							variableDeclare  = parameterArray[0].split(declareSeparator)[0]
							templateText     = parameterArray[2].strip()
							uiCaller         = parameterArray[3].strip()
							endOfLine        = parameterArray[-1]

							if ("'" in parameterArray[0] or '"' in parameterArray[0]):
								templateText = "\'" + templateText + "\'"

							content[index]   = ("%s %s %s; %s" % (variableDeclare, declareSeparator, templateText, endOfLine))
							eval(uiCaller)
					
					for i in content:
						self.htmlTemplate += i

				else:
					for i in content:
						self.htmlRendered += i
				self.renderHTML()

	def addParamItem(self, item):
		self.paramDict[item.name] = item.value()
		item.valueChanged.connect(lambda value : self.setDictValue(item.name, value))
		self.itemArray.append(item)
		self.itemLayout.addWidget(item)


	def SpaceParameterItem(self, *args, **kwargs):
		item = SpaceParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addStrParamItem(self, *args, **kwargs):
		item = StrParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addIntParamItem(self, *args, **kwargs):
		item = IntParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addIntSlideParamItem(self, *args, **kwargs):
		item = IntSlideParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addFloatParamItem(self, *args, **kwargs):
		item = FloatParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addColorParamItem(self, *args, **kwargs):
		item = ColorParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addDictParameterItem(self, *args, **kwargs):
		item = DictParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addListParamItem(self, *args, **kwargs):
		item = ListParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def addBoolParamItem(self, *args, **kwargs):
		item = BoolParameterWidget(*args, **kwargs)
		self.addParamItem(item)

	def setDictValue(self, name, value):
		self.paramDict[name] = value
		self.renderHTML()

	def renderHTML(self):
		self.htmlRendered =  jinja2.Environment().from_string(self.htmlTemplate).render(self.paramDict) if self.htmlTemplate else self.htmlRendered
		self.htmlChanged.emit(self.htmlRendered)

class SpaceParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name:str = "", height :int = -1):
		super().__init__()
		self.name         = name
		self.height       = 0
		self.mainLayout   = QVBoxLayout()
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.setHeight(height)
		self.setLayout(self.mainLayout)

	def setHeight(self, val : int):
		if val == -1:
			self.mainLayout.addStretch()

		if val > 0:
			self.mainLayout.addSpacing(val)

		self.height = val
		self.valueChanged.emit(str(val))

	def value(self):
		return self.height

class ColorParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name:str = "", defaultVal:str = "#000000"):
		super().__init__()
		self.name         = name
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueEdit    = QLineEdit()
		self.colorBox     = QPushButton()
		self.colorChooser = QColorDialog()
		self.rSpin        = QSpinBox()
		self.gSpin        = QSpinBox()
		self.bSpin        = QSpinBox()		

		self.colorBox.setFixedSize(QSize(16, 16))
		self.rSpin.setAlignment(Qt.AlignCenter)
		self.gSpin.setAlignment(Qt.AlignCenter)
		self.bSpin.setAlignment(Qt.AlignCenter)

		self.rSpin.setMaximum(255)
		self.gSpin.setMaximum(255)
		self.bSpin.setMaximum(255)

		self.rSpin.setMinimum(0)
		self.gSpin.setMinimum(0)
		self.bSpin.setMinimum(0)

		self.setHEXValue(defaultVal)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.colorBox)
		self.mainLayout.addWidget(self.rSpin)
		self.mainLayout.addWidget(self.gSpin)
		self.mainLayout.addWidget(self.bSpin)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.mainLayout)
		self.colorBox.clicked.connect(lambda : self.colorChooser.show())
		self.colorChooser.colorSelected.connect(lambda color: self.setHEXValue(color.name()))
		self.rSpin.valueChanged.connect(lambda : self.valueChanged.emit(self.value()))
		self.gSpin.valueChanged.connect(lambda : self.valueChanged.emit(self.value()))
		self.bSpin.valueChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		colorHEXValue = '#%02x%02x%02x' % (self.rSpin.value(), self.gSpin.value(), self.bSpin.value())
		self.colorBox.setStyleSheet("QPushButton{background-color : %s}" % (colorHEXValue))
		return colorHEXValue


	def setHEXValue(self, val):
		r, g, b = tuple(int(val.replace("#", "")[i:i+2], 16) for i in (0, 2, 4))
		self.rSpin.setValue(r)
		self.gSpin.setValue(g)
		self.bSpin.setValue(b)

class FloatParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name : str = "", minVal : float = 0, maxVal : float = 100, inc : float = 0.1, prefix : str = "", suffix : str = "", defaultVal : float = 0):
		super().__init__()
		self.name         = name
		self.prefix       = prefix
		self.suffix       = suffix
		self.inc          = inc
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueSpin    = QDoubleSpinBox()
		self.valueSpin.setAlignment(Qt.AlignCenter)
		self.valueSpin.setSingleStep(inc)
		self.valueSpin.setPrefix (prefix)
		self.valueSpin.setSuffix (suffix)
		self.valueSpin.setMinimum(minVal)
		self.valueSpin.setMaximum(maxVal)
		self.valueSpin.setValue(defaultVal)

		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueSpin)
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.mainLayout)
		self.valueSpin.valueChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		return self.prefix + str(self.valueSpin.value()) + self.suffix

class IntParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name : str = "", minVal : int = 0, maxVal : int = 100, inc : int = 1, prefix : str = "", suffix : str = "", defaultVal : int = 0):
		super().__init__()
		self.name         = name
		self.prefix       = prefix
		self.suffix       = suffix
		self.inc          = inc
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueSpin    = QSpinBox()
		self.valueSpin.setAlignment(Qt.AlignCenter)
		self.valueSpin.setSingleStep(inc)
		self.valueSpin.setPrefix (prefix)
		self.valueSpin.setSuffix (suffix)
		self.valueSpin.setRange (minVal, maxVal)
		self.valueSpin.setValue(defaultVal)
		
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueSpin)
		self.setLayout(self.mainLayout)
		self.valueSpin.valueChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		return self.prefix + str(self.valueSpin.value()) + self.suffix

class IntSlideParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name : str = "", minVal : int = 0, maxVal : int = 100, inc : int = 1, prefix : str = "", suffix : str = "", defaultVal : int = 0):
		super().__init__()
		self.name         = name
		self.prefix       = prefix
		self.suffix       = suffix
		self.inc          = inc
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueSlide   = QSlider()
		self.valueSpin    = QSpinBox()

		self.valueSlide.setOrientation(Qt.Horizontal)
		self.valueSpin.setAlignment(Qt.AlignCenter)
		
		self.valueSpin.setSingleStep(inc)
		self.valueSpin.setPrefix (prefix)
		self.valueSpin.setSuffix (suffix)

		self.valueSlide.setRange (minVal, maxVal)
		self.valueSpin.setRange (minVal, maxVal)
		

		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueSlide)
		self.mainLayout.addWidget(self.valueSpin)
		self.setLayout(self.mainLayout)

		self.valueSlide.valueChanged.connect( self.updateSpin)
		self.valueSpin.valueChanged.connect(  self.updateScroll)
		self.valueSpin.setValue(defaultVal)

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def updateScroll(self, value):
		self.valueSlide.blockSignals(True)
		self.valueSlide.setValue(value)
		self.valueChanged.emit(self.value())
		self.valueSlide.blockSignals(False)

	def updateSpin(self, value):
		self.valueSpin.blockSignals(True)
		self.valueSpin.setValue(value)
		self.valueChanged.emit(self.value())
		self.valueSpin.blockSignals(False)

	def value(self):
		return self.prefix + str(self.valueSpin.value()) + self.suffix

class StrParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name : str = "", defaultVal : str = ""):
		super().__init__()
		self.name         = name
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueEdit    = QLineEdit()
		self.valueEdit.setText(defaultVal)
		
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueEdit)
		self.setLayout(self.mainLayout)
		self.valueEdit.textChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		return  self.valueEdit.text()

class DictParameterWidget(QWidget):
	valueChanged = pyqtSignal(object)
	def __init__(self, name : str = "",  dictValue : dict = {}, defaultVal : str = ""):
		super().__init__()
		self.name         = name
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueBox     = QComboBox()
		self.dictValue    = dictValue

		self.valueBox.addItems(dictValue.keys())
		self.valueBox.setCurrentIndex(self.valueBox.findText(defaultVal))
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueBox)
		self.setLayout(self.mainLayout)
		self.valueBox.currentIndexChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		return self.dictValue[self.valueBox.currentText()]

class ListParameterWidget(QWidget):
	valueChanged = pyqtSignal(str)
	def __init__(self, name : str = "",  valueList : list = [], defaultVal : str = ""):
		super().__init__()
		self.name         = name
		self.mainLayout   = QHBoxLayout()
		self.nameLabel    = QLabel(name)
		self.valueBox     = QComboBox()

		self.valueBox.addItems(valueList)
		self.valueBox.setCurrentIndex(self.valueBox.findText(defaultVal))
		self.mainLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout.addWidget(self.nameLabel)
		self.mainLayout.addWidget(self.valueBox)
		self.setLayout(self.mainLayout)
		self.valueBox.currentIndexChanged.connect(lambda : self.valueChanged.emit(self.value()))

		if ParameterLabelWidth:
			self.nameLabel.setFixedWidth(ParameterLabelWidth)

	def value(self):
		return self.valueBox.currentText()

class BoolParameterWidget(ListParameterWidget):
	def __init__(self, name : str = "",  defaultVal : bool = False):
		super(BoolParameterWidget, self).__init__(name, ["true", "false"], "false")
		pass

class PorotechIcon(object):
	def __init__(self):
		super().__init__()
		self.icon = self.iconFromBase64(b"iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jnm+48GgAAA69JREFUSIm1lttPXFUUxn9rnzMzzHCGywwEKNMEG5DpcGs0EsHEWh9Ka7y96Etj4oO26QvR9EG03q2miZWkqUlN9E/QGG+kIVZEglQzWqBAUy8hKFQHGG0bQgszzPIBZsQRa4Dhe9vfWfv8ztrZ59tbVJX1Klz92ZuqPA5MI/p1ypf3KaGqMz92VS/cbJ5ZNwlQEKAEiKDyhJQ7TxnP1cnww98fq390zMkpLEsJ8dlhoERFjyYS18fChy/duzWwAs+3iJSnh+L3/EF5/pnwK5PtOYG58uafw9aQwv0Uej9AmALAMnHdUVSB4kI5mQ2UjWyQbO3Z86U9VVzwtAkHH8Jt3bXqUVIrvPsuHQqezRksrZ0vTrWopZ+gBMVtx7Q6MIFttieW7J0/P8LVXGyQjC6+WjkgmAcJ+vq1NujCNs1AhdtOdkCOO0sr/GHyGZTjq6z4wjU7lNPO0nJm7E7gdwCRuZjb+81oUej9ti3pDKC+q7/Ddo8eEJOoYzkE3tuSzgBcnsHvxCTqV0AArVsGU7HGsqwyu6eq4XVVsdJOYan7hduj0cRmYXZh158mob3psWUkaaMclOVQBSB+JdEJTG8WZlLjQdttdq+yLhtFfvvHFy2mdm0WBGBbVlOW9asR0T4AY5j3FnKuoJKWXMBqJNXsFR0A5lesAemra9znBPRlcdEA+EBnC1Nz26t6xm9sFPTshcZiUZkA/EswF1MGL6vpMMnSwOfiIrQMApCSa8Z5fpONnQD8ABY42wSne9f5fnNPT09SkdPpKrF0omiHtEwcbGjdCKV7pKE1YqSG1ZtMpRNWsvGn+2o88wve8y6HmfxyrRWhDIgb5IHKd4YH1gPCmI+B4KISiy4xnoDkG43DdyuqmbgaP1DfbPulH7DTk/P89OeXS7dvzn2Cl6Lz/8GA4ab8xTw5ci7J3hto5jxTSExbqdbHai9EM52l9cuhhnYRTgIYm+miKrVAgkDc8vOWFBBdEteozzFXrjuJgNFUUypg1VpePQoEFpX4QJKkLq8MIO17I4On0u//VxBPHq5/UlXeLr6FEbG4LVNYJqNiUQcgAXrJYzeAeOiVoGR+3lnVoZEliYAcWQ2CNe4godMj7/pKdb9YlGZMS2JiEVlrBXWRO0AzwVAiEgzZ7M8GrQkDCL428sW8TyOqcgyYweEH/k7vLBo+TcqQwizocbcuRCK3Dp1dq/T/z7NTNZ6FAl9byk61IXInyjYJ6kW8UocSU/jKOPqRp2Suj6qbB8FfcZpVXdo/DbkAAAAASUVORK5CYII=")

	def iconFromBase64(self, base64):
		pixmap = QPixmap()
		pixmap.loadFromData(QByteArray.fromBase64(base64))
		icon = QIcon(pixmap)
		return icon
		


if __name__ == '__main__':
	app    = QApplication(sys.argv)
	window = DashWidget()
	window.show()
	sys.exit(app.exec_())



