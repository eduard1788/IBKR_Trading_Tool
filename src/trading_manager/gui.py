import customtkinter
from .ibkr_client import IBKRClientAPI
from .widgets import *
from .constants import *

class TradingApp:

    def __init__(self):
        self.ib_client = IBKRClientAPI()

    def setup_widgets(self, num_columns, frame):
        draw_widgets(num_columns, frame)

    def run(self):
        print("Starting TradingApp...")
        num_columns = self.ib_client.prompt_num_columns()
        self.setup_widgets(num_columns=num_columns, frame=self.ib_client.frame)
        self.ib_client.root.mainloop()
