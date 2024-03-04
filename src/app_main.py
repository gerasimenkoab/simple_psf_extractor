import logging
import logging.config
import os
from controller.main_controller import MainAppController


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
    startApplication()