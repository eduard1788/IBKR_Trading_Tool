import customtkinter
from .ibkr_client import IBKRClientAPI
from .widgets import *
from .constants import *

class TradingApp:
    def __init__(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        self.root = customtkinter.CTk()
        self.root.geometry("500x800")
        self.ib_client = IBKRClientAPI()

    def prompt_num_columns(self):
        input_dialog = customtkinter.CTkInputDialog(
            text="Enter the number of columns for the grid layout:",
            title="Grid Columns"
        )
        num_columns = input_dialog.get_input()
        if num_columns is None or not num_columns.isdigit() or int(num_columns) < 1:
            raise ValueError("Invalid number of columns entered.")
        return int(num_columns)

    def setup_widgets(self, num_columns, frame):
        # Create the frame first
        draw_widgets(num_columns, frame)

    def run(self):
        print("Starting TradingApp...")

        frame = create_frame_grid_position(self.root)
        num_columns = self.prompt_num_columns()
        self.setup_widgets(num_columns=num_columns, frame=frame)

        system_message = customtkinter.CTkLabel(master=self.root, text="", text_color="white", wraplength=450)
        system_message.pack(pady=10)

        button_frame = create_frame_relative_position(master = self.root, relx = 1, rely = 0)
        button_frame_2 = create_frame_relative_position(master = self.root, relx = 0, rely = 0, anchor='nw')

        dropdown_var = customtkinter.StringVar(value="Select account")
        accounts_menu = create_dropdown_relative_position(master=button_frame, variable=dropdown_var, values=accounts)

        port = create_entry_relative_position(master=button_frame, placeholder_text="Conn Port", side="right", width=60)
        client_id = create_entry_relative_position(master=button_frame, placeholder_text="Client ID", side="right", width=60)
        connect_reconnect_button = create_button_relative_position(master=button_frame, text="Disconnected", command=IBKRClientAPI.connect, side="left")

        load_excel_button = create_button_relative_position(master=button_frame_2, text="Load Excel Files", command=IBKRClientAPI.connect, side="right", width=120, fg_color="gray")

        open_orders_btn = create_button_relative_position(master=button_frame_2, text="Show Open Orders", command=IBKRClientAPI.connect, side="left", width=120, fg_color="gray")

        self.root.mainloop()
