import logging
import logging.config
import os
from main.app_main_controller import MainAppController
from multiprocessing import freeze_support


def startApplication():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    try:
        logging_conf_path = os.path.join(os.path.dirname(__file__), 'logging.conf')
        logging.config.fileConfig(logging_conf_path)
    except FileNotFoundError as e:
        print("Logging.conf file missing." + str(e))
        return
    logger = logging.getLogger(__name__)

    MainAppController().Run()
    

if __name__=="__main__":
    # IMPORTANT: freeze_support() is needed to prevent multiply windows opening when prepare distribution by pyinstaller
    # also for this purposw multiprocessing manager singleton class was created to avoid intersections of 
    # multiprocessing event loop and tkinter eventloop
    freeze_support()
    startApplication()