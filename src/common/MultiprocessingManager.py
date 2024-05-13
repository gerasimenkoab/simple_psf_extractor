from multiprocessing import Manager
 # IMPORTANT: freeze_support() call in main app is needed to prevent multiply windows opening when prepare distribution by pyinstaller
    # also for this purposw multiprocessing manager singleton class was created to avoid intersections of 
    # multiprocessing event loop and tkinter eventloop
class SingletonManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.manager = Manager()
        return cls._instance
    
    # context manager support
    def __enter__(self):
        return self.manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.manager.shutdown()
        return False  # Propagate exceptions