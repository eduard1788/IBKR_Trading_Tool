import customtkinter
from typing import Union, List
from .constants import *

def draw_widgets(columns: int = 1, master: customtkinter.CTkFrame = None):

    from .ibkr_client import IBKRClientAPI
    ib_client = IBKRClientAPI()

    for col in range(columns):
        ticker_label = create_label_grid_position(master, f"Symbol # {col+1}", row=0, column=col)

        checkbox_r_var = customtkinter.BooleanVar(value=False) 
        checkbox_r_vars[col] = checkbox_r_var
        checkbox_r = create_checkbox_grid_position(master, text = "Position-based", tracking_variable = checkbox_r_var, row = 1, column = col, width = 1, height =1)
        checkboxs_r[col] = checkbox_r

        checkbox_s_var = customtkinter.BooleanVar(value=False) 
        checkbox_s_vars[col] = checkbox_s_var
        checkbox_s = create_checkbox_grid_position(master, text = "Not include STP loss", tracking_variable = checkbox_s_var, row = 2, column = col, width = 1, height =1)
        checkboxs_s[col] = checkbox_s

        checkbox_sh_var = customtkinter.BooleanVar(value=False) 
        checkbox_sh_vars[col] = checkbox_sh_var
        checkbox_sh = create_checkbox_grid_position(master, text = "Sell position", tracking_variable = checkbox_sh_var, row = 3, column = col, width = 1, height =1)
        checkboxs_sh[col] = checkbox_sh

        spacer_1 = create_label_grid_position(master, text="", row=4, column=col)
        stp_name = create_entry_grid_position(master, "Name", row=5, column=col)
        stp_name_entries[col] = stp_name

        stp_risk_USD = create_entry_grid_position(master, "Risk in USD", row=6, column=col)
        stp_risk_USD_entries[col] = stp_risk_USD

        positions = create_entry_grid_position(master, "Position", row=7, column=col)
        position_entries[col] = positions

        #orderId_entry_label = create_label_grid_position(master, "Order ID Entry:", row=8, column=col)
        #orderId_entry_labels[col] = orderId_entry_label

        stp_entry = create_entry_grid_position(master, "Entry", row=8, column=col)
        stp_entry_entries[col] = stp_entry

        #orderId_stop_label = create_label_grid_position(master, "Order ID Stop:", row=10, column=col)
        #orderId_stop_labels[col] = orderId_stop_label

        stp_loss = create_entry_grid_position(master, "Stop Loss", row=9, column=col)
        stp_loss_entries[col] = stp_loss

        stp_button = create_button_grid_position(master, "Summit STP Order",lambda c=col: ib_client.stp_order(c), row=10, column=col)
        stp_buttons[col] = stp_button

        #orderId_lmt_label = create_label_grid_position(master, "Order ID Limit:", row=13, column=col)
        #orderId_lmt_labels[col] = orderId_lmt_label

        spacer_2 = create_label_grid_position(master, text="", row=11, column=col)
        lmt_entry = create_entry_grid_position(master, "Limit Price", row=12, column=col)
        lmt_entry_entries[col] = lmt_entry

        lmt_button = create_button_grid_position(master, "Summit Limit Order", lambda c=col: IBKRClientAPI.lmt_order(c), row=13, column=col)
        lmt_buttons[col] = lmt_button

        spacer_3 = create_label_grid_position(master, text="", row=14, column=col)
        orderid_entry = create_entry_grid_position(master, "order ID", row=15, column=col)
        orderid_entries[col] = orderid_entry

        modify_button = create_button_grid_position(master, "Modify Order", lambda c=col: IBKRClientAPI.modify_order(c), row=16, column=col)
        modify_buttons[col] = modify_button

        cancel_button = create_button_grid_position(master, "Cancel Order", lambda c=col: IBKRClientAPI.cancel_order(c), row=17, column=col)
        cancel_buttons[col] = cancel_button

        spacer_4 = create_label_grid_position(master, text="", row=18, column=col)
        mkt_button = create_button_grid_position(master, "Submit Sell MKT Order", lambda c=col: IBKRClientAPI.mkt_order(c), row=19, column=col)
        mkt_buttons[col] = mkt_button

def create_frame_grid_position(master, pady: int = 20, padx: int = 60, fill: str = "both", expand: bool = True):
    frame = customtkinter.CTkFrame(master=master)
    frame.pack(pady=pady, padx=padx, fill=fill, expand=expand)
    return frame

def create_label_grid_position(master: customtkinter.CTkFrame, text, row=0, column=0, padx=5, pady=5, sticky="w"):
    label = customtkinter.CTkLabel(master=master, text=text)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return label

def create_entry_grid_position(master: customtkinter.CTkFrame, text, row=0, column=0, padx=5, pady=5, sticky="w"):
    entry_name = customtkinter.CTkEntry(master=master, placeholder_text=text)
    entry_name.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return entry_name

def create_button_grid_position(master: customtkinter.CTkFrame, text: str, function, row: int = 0, column: int = 0, padx: int = 5, pady: int = 5, sticky: str = "w", width: int = 140, height: int = 28,):
    button = customtkinter.CTkButton(master=master, text=text, command=function)
    button.grid(row=row, column=column, padx=5, pady=5, sticky="w")
    return button

def create_checkbox_grid_position(master: customtkinter.CTkFrame, text: str, tracking_variable: customtkinter.BooleanVar, row: int = 0, column: int = 0, padx: int = 5, pady: int = 5, sticky: str = "w", width: int =16, height: int = 16):
    checkbox = customtkinter.CTkCheckBox(master=master, text=text, variable=tracking_variable, width=width, height=height)
    checkbox.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return checkbox

def create_dropdown_relative_position(master: customtkinter.CTkFrame, variable: customtkinter.StringVar, values: any, padx: int = 5, pady: int = 5, side: str = 'right'):
    dropdown = customtkinter.CTkOptionMenu(master = master, variable = variable, values = values)
    dropdown.pack(padx=padx, pady=pady, side=side)
    return dropdown

    """_summary_
    Corner	       relx	     rely	 anchor
    Top Left	    0	      0	     'nw'
    Top Right	    1	      0	     'ne'
    Bottom Left	    0	      1	     'sw'
    Bottom Right	1	      1	     'se'
    """         

def create_frame_relative_position(master, fg_color: str = "transparent", relx: int = 1, rely: int = 0, anchor: str = "ne"):
    frame = customtkinter.CTkFrame(master=master, fg_color=fg_color)
    frame.place(relx=relx, rely=rely, anchor=anchor)
    return frame

def create_entry_relative_position(master: customtkinter.CTkFrame, placeholder_text: str, side: str = "right", width: int = 120):
    entry = customtkinter.CTkEntry(master=master, placeholder_text=placeholder_text, width=width)
    entry.pack(side=side)
    return entry

def create_button_relative_position(master: customtkinter.CTkFrame, text: str, command, side: str = "right", width: int = 80, height: int = 30, fg_color: str = "red"):
    button = customtkinter.CTkButton(master=master, text=text, command=command, width=width, height=height, fg_color=fg_color)
    button.pack(side=side)
    return button

def display_message(master: customtkinter.CTkLabel, msg: Union[str, List[str]], color: str = "white"):
    master.configure(text=msg, text_color=color)
