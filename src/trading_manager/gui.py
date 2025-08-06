import customtkinter
from .ibkr_client import IBKRClientAPI

class TradingApp:
    def __init__(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        self.root = customtkinter.CTk()
        self.root.geometry("500x800")
        self.ib_client = IBKRClientAPI()
        self.setup_widgets()

    def setup_widgets(self):
        # Example: Add widgets and layout here
        pass

    def run(self):
        self.root.mainloop()
