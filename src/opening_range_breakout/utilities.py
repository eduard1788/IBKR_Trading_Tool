import customtkinter
from ib_insync import *
from typing import Union, List
import math
from typing import Dict, Any
from time import sleep
import pandas as pd
from tkinter import filedialog
import openpyxl
from common import validate_info_stp_button

ib = IB() # Define ib globally

# Connect to the IB Gateway or TWS
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
root =  customtkinter.CTk()
root.geometry("500x800")

accounts = ["U3297495", "U4572134", "U7514316", "DU1717711", "DU2883726"]

####################################################
######### Initializing widget dictionaries #########
####################################################

stp_name_entries = {}
stp_risk_USD_entries = {}
stp_entry_entries = {}
stp_loss_entries = {}
stp_buttons = {}
lmt_entry_entries = {}
lmt_buttons = {}
mkt_buttons = {}
orderId_entry_labels = {}
orderId_stop_labels = {}
orderId_lmt_labels = {}
checkbox_r_vars = {}
checkboxs_r = {}
checkbox_s_vars = {}
checkboxs_s = {}
checkbox_sh_vars = {}
checkboxs_sh = {}
position_entries = {}
cancel_entry_entries = {}
cancel_buttons = {}

def update_button_status():
    ### Updates the button text and color based on connection status.
    if ib.isConnected():
        connect_reconnect_button.configure(text="Connected", fg_color="green")
    else:
        connect_reconnect_button.configure(text="Disconnected", fg_color="red")
    # Re-check status every 1 second
    root.after(1000, update_button_status)

def connect_ib():
    # Clear previous messages
    display_message(system_message, "")
    # Get connection parameters
    value_port = port.get().strip()
    value_client = client_id.get().strip()
    
    missing_fields = []
    if not value_port:
        missing_fields.append("Port Number")
    if not value_client:
        missing_fields.append("Client ID")
    if missing_fields:
        missing_message = f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields."
        display_message(system_message, missing_message, color="red")
        return  # Stop execution if fields are missing
    try:
        value_port = int(value_port)
        value_client = int(value_client)
        global ib
        if not ib.isConnected():
            util.startLoop()
            ib.connect('127.0.0.1', value_port, clientId=value_client)
        else:
            ib.disconnect()
        update_button_status()  # Update button after connection attempt
    except Exception as e:
        display_message(system_message, f"⚠️ Connection attempt failed: {str(e)}", color="yellow")

def show_order_wait(message):
    display_message(system_message, message, color="yellow")

def confirm_operation(message: str, on_yes, on_no = None):
    """
    Displays a confirmation dialog with the given message.
    Calls on_yes if the user confirms, and on_no if the user cancels.
    """
    confirm_win = customtkinter.CTkToplevel(root)
    confirm_win.title("Confirm Operation")
    confirm_win.geometry("600x300")
    confirm_win.grab_set()  # Make the window modal

    label = customtkinter.CTkLabel(confirm_win, text=message, wraplength=400, justify="left")
    label.pack(pady=15)

    button_frame = customtkinter.CTkFrame(confirm_win)
    button_frame.pack(pady=5)

    def yes_action():
        confirm_win.destroy()
        on_yes()

    def no_action():
        confirm_win.destroy()
        if on_no:
            on_no()
    
    yes_btn = customtkinter.CTkButton(button_frame, text="Yes", command=yes_action, fg_color="green")
    yes_btn.pack(side="left", padx=10)
    no_btn = customtkinter.CTkButton(button_frame, text="No", command=no_action, fg_color="red")
    no_btn.pack(side="left", padx=10)

################################################################################################
######### Create labels, entries, checkbox, drop-downs, and buttons in the grid layout #########
################################################################################################

def create_frame_grid_position(master, pady: int = 20, padx: int = 60, fill: str = "both", expand: bool = True):
    frame = customtkinter.CTkFrame(master=master)
    frame.pack(pady=pady, padx=padx, fill=fill, expand=expand)
    return frame

def create_label_grid_position(frame: customtkinter.CTkFrame, text, row=0, column=0, padx=5, pady=5, sticky="w"):
    label = customtkinter.CTkLabel(master=frame, text=text)
    label.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return label

def create_entry_grid_position(frame: customtkinter.CTkFrame, text, row=0, column=0, padx=5, pady=5, sticky="w"):
     entry_name = customtkinter.CTkEntry(master=frame, placeholder_text=text)
     entry_name.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
     return entry_name

def create_button_grid_position(frame: customtkinter.CTkFrame, text: str, function, row: int = 0, column: int = 0, padx: int = 5, pady: int = 5, sticky: str = "w", width: int = 140, height: int = 28,):
    button = customtkinter.CTkButton(master=frame, text=text, command=function)
    button.grid(row=row, column=column, padx=5, pady=5, sticky="w")
    return button

def create_checkbox_grid_position(frame: customtkinter.CTkFrame, text: str, tracking_variable: customtkinter.BooleanVar, row: int = 0, column: int = 0, padx: int = 5, pady: int = 5, sticky: str = "w", width: int =16, height: int = 16):
    checkbox = customtkinter.CTkCheckBox(master=frame, text=text, variable=tracking_variable, width=width, height=height)
    checkbox.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
    return checkbox

def create_dropdown_relative_position(master: customtkinter.CTkFrame, variable: customtkinter.StringVar, values: any, padx: int = 5, pady: int = 5, side: str = 'right'):
    dropdown = customtkinter.CTkOptionMenu(master = master, variable = variable, values = values)
    dropdown.pack(padx=padx, pady=pady, side=side)
    return dropdown

def create_frame_relative_position(master, fg_color: str = "transparent", relx: int = 1, rely: int = 0, anchor: str = "ne"):
    frame = customtkinter.CTkFrame(master=master, fg_color=fg_color)
    frame.place(relx=1, rely=0, anchor="ne")
    return frame

def create_entry_relative_position(master: customtkinter.CTkFrame, placeholder_text: str, side: str = "right", width: int = 120):
    entry = customtkinter.CTkEntry(master=master, placeholder_text=placeholder_text, width=width)
    entry.pack(side=side)
    return entry

def create_button_relative_position(master: customtkinter.CTkFrame, text: str, command, side: str = "right", width: int = 80, height: int = 30, fg_color: str = "red"):
    button = customtkinter.CTkButton(master=master, text=text, command=command, width=width, height=height, fg_color=fg_color)
    button.pack(side=side)
    return button

def display_message(frame: customtkinter.CTkLabel, msg: Union[str, List[str]], color: str = "white"):
    frame.configure(text=msg, text_color=color)

################################################################
###########           System message label           ###########
################################################################

system_message = customtkinter.CTkLabel(master=root, text="", text_color="white", wraplength=450)
system_message.pack(pady=10)


#############################################################
######### Create the main frame for the grid layout #########
#############################################################

frame = create_frame_grid_position(root)

#############################################################
######### Frame for buttons in the top-right corner #########
#############################################################

button_frame = create_frame_relative_position(master = root, relx = 1, rely = 0)


def load_excel_files():
    # Open file dialog for file1
    file1_path = filedialog.askopenfilename(title="Select the first Excel file", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file1_path:
        display_message(system_message, "No file selected for file1.", color="yellow")
        return

    # Read all sheets from file1
    try:
        file1_sheets = pd.read_excel(file1_path, sheet_name=None)
        if len(file1_sheets) < 4:
            display_message(system_message, "File1 does not have at least 4 sheets.", color="red")
            return
        # Store each sheet as a dataframe
        file1_dfs = list(file1_sheets.values())[:4]
    except Exception as e:
        display_message(system_message, f"Error reading file1: {e}", color="red")
        return
    #debugging stored dataframes
    # Debugging line to print the loaded dataframes
    display_message(system_message, f"File1 loaded successfully with {len(file1_dfs)} sheets.", color="green")
    # Print each dataframe's name and shape
    for i, df in enumerate(file1_dfs):
        display_message(system_message, f"Sheet {i+1}: {df.shape[0]} rows, {df.shape[1]} columns", color="white")

    """
    # Open file dialog for file2
    file2_path = filedialog.askopenfilename(title="Select the second Excel file", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file2_path:
        display_message(system_message, "No file selected for file2.", color="yellow")
        return

    # Read all sheets from file2
    try:
        file2_sheets = pd.read_excel(file2_path, sheet_name=None)
        if len(file2_sheets) < 4:
            display_message(system_message, "File2 does not have at least 4 sheets.", color="red")
            return
        file2_dfs = list(file2_sheets.values())[:4]
    except Exception as e:
        display_message(system_message, f"Error reading file2: {e}", color="red")
        return

    display_message(system_message, "Both files loaded successfully!", color="green")
    # Now file1_dfs and file2_dfs are lists of 4 dataframes each
    # You can use them as needed in your app
    """

########################################################################
######### Create buttons and entries in the connectivity frame #########
########################################################################
dropdown_var = customtkinter.StringVar(value="Select account")
accounts_menu = create_dropdown_relative_position(master=button_frame, variable=dropdown_var, values=accounts)

port = create_entry_relative_position(master=button_frame, placeholder_text="Conn Port", side="right", width=60)
client_id = create_entry_relative_position(master=button_frame, placeholder_text="Client ID", side="right", width=60)
connect_reconnect_button = create_button_relative_position(master=button_frame, text="Disconnected", command=connect_ib, side="left")

load_excel_button = create_button_relative_position(master=button_frame, text="Load Excel Files", command=load_excel_files, side="left", width=120, fg_color="blue")

########################################################################################
######### Dynamically Creating labels, entries, and buttons in the grid layout #########
########################################################################################

def draw_widgets(columns: int = 1, frame: customtkinter.CTkFrame = None):
    for col in range(columns):
        ticker_label = create_label_grid_position(frame, f"Symbol # {col+1}", row=0, column=col)

        checkbox_r_var = customtkinter.BooleanVar(value=False) 
        checkbox_r_vars[col] = checkbox_r_var
        checkbox_r = create_checkbox_grid_position(frame, text = "Position-based", tracking_variable = checkbox_r_var, row = 1, column = col, width = 1, height =1)
        checkboxs_r[col] = checkbox_r

        checkbox_s_var = customtkinter.BooleanVar(value=False) 
        checkbox_s_vars[col] = checkbox_s_var
        checkbox_s = create_checkbox_grid_position(frame, text = "Not include stp loss", tracking_variable = checkbox_s_var, row = 2, column = col, width = 1, height =1)
        checkboxs_s[col] = checkbox_s

        checkbox_sh_var = customtkinter.BooleanVar(value=False) 
        checkbox_sh_vars[col] = checkbox_sh_var
        checkbox_sh = create_checkbox_grid_position(frame, text = "Short position", tracking_variable = checkbox_sh_var, row = 3, column = col, width = 1, height =1)
        checkboxs_sh[col] = checkbox_sh

        spacer_1 = create_label_grid_position(frame, text="", row=4, column=col)
        stp_name = create_entry_grid_position(frame, "Name", row=5, column=col)
        stp_name_entries[col] = stp_name

        stp_risk_USD = create_entry_grid_position(frame, "Risk in USD", row=6, column=col)
        stp_risk_USD_entries[col] = stp_risk_USD

        positions = create_entry_grid_position(frame, "Position", row=7, column=col)
        position_entries[col] = positions

        orderId_entry_label = create_label_grid_position(frame, "Order ID Entry:", row=8, column=col)
        orderId_entry_labels[col] = orderId_entry_label

        stp_entry = create_entry_grid_position(frame, "Entry", row=9, column=col)
        stp_entry_entries[col] = stp_entry

        orderId_stop_label = create_label_grid_position(frame, "Order ID Stop:", row=10, column=col)
        orderId_stop_labels[col] = orderId_stop_label

        stp_loss = create_entry_grid_position(frame, "Stop Loss", row=11, column=col)
        stp_loss_entries[col] = stp_loss

        stp_button = create_button_grid_position(frame, "Summit STP Order",lambda c=col: main_order(c), row=12, column=col)
        stp_buttons[col] = stp_button

        orderId_lmt_label = create_label_grid_position(frame, "Order ID Limit:", row=13, column=col)
        orderId_lmt_labels[col] = orderId_lmt_label

        lmt_entry = create_entry_grid_position(frame, "Limit Price", row=14, column=col)
        lmt_entry_entries[col] = lmt_entry

        lmt_button = create_button_grid_position(frame, "Summit Limit Order", frame, row=15, column=col)
        lmt_buttons[col] = lmt_button

        cancel_entry = create_entry_grid_position(frame, "order ID", row=16, column=col)
        cancel_entry_entries[col] = cancel_entry

        cancel_button = create_button_grid_position(frame, "Summit Cancel Order", frame, row=17, column=col)
        cancel_buttons[col] = cancel_button

        mkt_button = create_button_grid_position(frame, "Submit Sell MKT Order", frame, row=18, column=col)
        mkt_buttons[col] = mkt_button

#################################################
################# Action Buttons ################
#################################################

def get_values(col: int) -> Dict[str, Any]:
    
    results_dict = {
        "symbol": stp_name_entries[col].get(),
        "entry": stp_entry_entries[col].get(),
        "stop": stp_loss_entries[col].get(),
        "risk_USD": stp_risk_USD_entries[col].get(),
        "position": position_entries[col].get(),
        "position_based": checkbox_r_vars[col].get(),
        "not_stp_loss": checkbox_s_vars[col].get(),
        "short_pos": checkbox_sh_vars[col].get(),
        "limit": lmt_entry_entries[col].get(),
        "account":  dropdown_var.get()
    }
    return results_dict

# Updgrade with parameters limited to specific values to avoid errors.
# e.g. Literal['BUY', 'SELL'] for action, Literal['STP', 'LMT'] for order_type, etc.
def set_order(action: str, quantity: int, order_type: str, price: float, tif: str, account: str, transmit:bool, parentId: int = 0):
    order = Order(
    action=action,
    totalQuantity=quantity,
    orderType=order_type,
    auxPrice=price,
    # Look for all options for TIF (Time in Force) and limit the options
    # https://interactivebrokers.github.io/tws-api/classIBApi_1_1
    tif=tif,
    parentId=parentId,
    account=account,
    # The parent order must be FALSE (Do not transmit yet — needed to link children)
    # The child order must be TRUE (last in the chain, transmits all orders) 
    transmit=transmit 
    )
    return order

def get_parent_child_event(symbol, parent_order, child_order, stp_flag):
    if stp_flag:
        # Only send the parent order, do not send the child order
        stock = Stock(symbol=symbol, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock)

        parent_trade = ib.placeOrder(stock, parent_order)
        ib.sleep(1)  # Wait for the order to be processed
        position = parent_order.totalQuantity
        return symbol, parent_trade.order.orderId, None, position
    else:
        # Select the contract based on the symbol
        stock = Stock(symbol=symbol, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock)

        parent_trade = ib.placeOrder(stock, parent_order)
        ib.sleep(1)  # Wait for the order to be processed
        parent_id = parent_trade.order.orderId
        child_order.parentId = parent_id
        # Set OCA group so one cancels the other
        oca_group = f"OCA_{symbol}_{parent_id}"
        parent_order.ocaGroup = oca_group
        child_order.ocaGroup = oca_group
        parent_order.ocaType = 1  # CANCEL_WITH_BLOCK
        child_order.ocaType = 1
        # Place the SELL order
        child_trade = ib.placeOrder(stock, child_order)

        # Get position (quantity) from parent or child order
        position = parent_order.totalQuantity  # or child_order.totalQuantity

        return symbol, parent_trade.order.orderId, child_trade.order.orderId, position

def main_order(col: int):
    
    ######################
    #   1. Get values    #
    ######################
    values = get_values(col)
    
    #######################
    # 2. Input validation #
    #######################

    valid, order, flag_fields_ok, missing_fileds = validate_info_stp_button(values)
    
    if not valid:
        display_message(system_message, f"⚠️ {order}", color="red")
        return
        
    if not flag_fields_ok:
        display_message(system_message, f"⚠️ Missing: {', '.join(missing_fileds)}. Please fill in all fields.", color="red")
        return
    
    
    def cancel():
        display_message(system_message, "Operation cancelled by user", color="yellow")
    
    def proceed():

        #types_dict = {k: type(v) if v is not None else None for k, v in values.items()}
        #print(f"Values in column {types_dict}")


        starting_message = f"Submitting a {order}..."
        show_order_wait(starting_message)
        sleep(2)
        print(valid)
        print(order)
        print(flag_fields_ok)
        print(missing_fileds)

        if values['position_based']:
            quantity = int(values['position'])
            entry = float(values['entry'])
            stop = float(values['stop'])
        else:
            risk = float(values['risk_USD'])
            entry = float(values['entry'])
            stop = float(values['stop'])
            budget = abs((risk * 100)/(((float(entry-stop)/entry))*100))
            quantity = abs(math.floor(budget/float(entry)))
        
        ######################
        #   2. Get orders    #
        ######################

        if values["short_pos"]:
            # sell order is the parent, buy order is the child
            if values['not_stp_loss']:
                parent_order = set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = True)
                child_order = None
            else:
                parent_order = set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = False)
                child_order = set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = stop, tif = 'GTC', account = values['account'], transmit = True)
        else:
            # buy order is the parent, sell order is the child
            if values['not_stp_loss']:
                parent_order = set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = True)
                child_order = None
            else:
                parent_order = set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = False)
                child_order = set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = stop, tif = 'GTC', account = values['account'], transmit = True)

        ######################
        #   3. Send order    #
        ######################

        # Show waiting message
        message = "Waiting for order to be registered..."
        show_order_wait(message)
        sleep(3)
        # Send the parent and child orders
        stp_flag = values['not_stp_loss']
        if values['not_stp_loss']:
            name, parent_order_id, child_order_id, position = get_parent_child_event(symbol = values['symbol'], parent_order = parent_order, child_order = child_order, stp_flag = stp_flag)
            # Show order transmission result message
            display_message(system_message, f"Symbol: {name}, BUY order ID: {parent_order_id} / SELL order ID: {child_order_id}, position: {position}", color="green")
        else:
            name, parent_order_id, child_order_id, position = get_parent_child_event(symbol = values['symbol'], parent_order = parent_order, child_order = child_order, stp_flag = stp_flag)
            # Show order transmission result message
            display_message(system_message, f"Symbol: {name}, BUY order ID: {parent_order_id} / SELL order ID: {child_order_id}, position: {position}", color="green")
            
    mes = "Are you sure you want to submit this order?\n"
    order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nRisk USD: {values['risk_USD']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    confirm_operation(mes + order_summary, on_yes = proceed, on_no = cancel)