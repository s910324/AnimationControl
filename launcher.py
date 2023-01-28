from animate_control import *

try:
	app    = QApplication(sys.argv)
	window = DashWidget()
	window.show()
	sys.exit(app.exec_())
	
except:
    logging.error("LOG", exc_info=True)

