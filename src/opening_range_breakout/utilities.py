import customtkinter
from ib_insync import *
from typing import Union, List
ib = IB() # Define ib globally


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
checkbox_vars = {}
checkboxs = {}


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

def create_entry_relative_position(master: customtkinter.CTkFrame, placeholder_text: str, side: str = "right"):
    entry = customtkinter.CTkEntry(master=master, placeholder_text=placeholder_text)
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


########################################################################################
######### Dynamically Creating labels, entries, and buttons in the grid layout #########
########################################################################################

def draw_widgets(columns: int = 1, frame: customtkinter.CTkFrame = None):
    for col in range(columns):
        ticker_label = create_label_grid_position(frame, f"Symbol # {col+1}", row=0, column=col)

        checkbox_var = customtkinter.BooleanVar(value=False) 
        checkbox_vars[col] = checkbox_var
        checkbox = create_checkbox_grid_position(frame, text = "Save", tracking_variable = checkbox_var, row = 1, column = col, width = 1, height =1)
        checkboxs[col] = checkbox

        stp_name = create_entry_grid_position(frame, "Name", row=2, column=col)
        stp_name_entries[col] = stp_name

        stp_risk_USD = create_entry_grid_position(frame, "Risk in USD", row=3, column=col)
        stp_risk_USD_entries[col] = stp_risk_USD

        orderId_entry_label = create_label_grid_position(frame, "Order ID Entry:", row=4, column=col)
        orderId_entry_labels[col] = orderId_entry_label

        stp_entry = create_entry_grid_position(frame, "Entry", row=5, column=col)
        stp_entry_entries[col] = stp_entry

        orderId_stop_label = create_label_grid_position(frame, "Order ID Stop:", row=6, column=col)
        orderId_stop_labels[col] = orderId_stop_label

        stp_loss = create_entry_grid_position(frame, "Stop Loss", row=7, column=col)
        stp_loss_entries[col] = stp_loss

        stp_button = create_button_grid_position(frame, "Summit STP Order", lambda c=col: stp_order(c, 'U3297495'), row=8, column=col)
        stp_buttons[col] = stp_button

        spacer_1 = create_label_grid_position(frame, text="", row=9, column=col)
        lmt_entry = create_entry_grid_position(frame, "Limit Price", row=10, column=col)
        lmt_entry_entries[col] = lmt_entry

        lmt_button = create_button_grid_position(frame, "Summit Limit Order", frame, row=11, column=col)
        lmt_buttons[col] = lmt_button

        spacer_2 = create_label_grid_position(frame, text="", row=12, column=col)
        mkt_button = create_button_grid_position(frame, "Submit Sell MKT Order", frame, row=13, column=col)
        mkt_buttons[col] = mkt_button

        spacer_3 = create_label_grid_position(frame, text="", row=14, column=col)


#################################################
################# Action Buttons ################
#################################################

def on_stp_button_press(col):
    name = stp_name_entries[col].get()
    risk = stp_risk_USD_entries[col].get()
    entry = stp_entry_entries[col].get()
    stop = stp_loss_entries[col].get()
    print(f"STP Button pressed in column {col}: Name={name}, Risk={risk}, Entry={entry}, Stop={stop}")

def stp_order(col: int, account_num):
    # Clear previous messages
    display_message(system_message, "", color="white") 
    # Get input values
    risk = stp_risk_USD_entries[col].get()
    name = stp_name_entries[col].get()
    entry = stp_entry_entries[col].get()
    stop = stp_loss_entries[col].get()

    missing_fields = []
    if not risk:
        missing_fields.append("Risk in USD")
    if not name:
        missing_fields.append("Ticker name")
    if not entry:
        missing_fields.append("Entry")
    if not stop:
        missing_fields.append("Stop loss")

    if missing_fields:
        missing_message = f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields."
        display_message(system_message, missing_message, color="red")
        return  # Stop execution if fields are missing
                # Adjust to send STP buy and sell orders individually when not all fields are filled
    try:
        # Set values for stock
        stock = Stock(symbol=name, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock)
        # Convert str values to numeric
        risk = float(risk)
        entry = float(entry)
        stop = float(stop)
        # Calculate position
        budget = (risk * 100)/(((entry-stop)/entry)*100)
        position = round(budget/entry)
        # Create orders
        order_BUY = Order(totalQuantity=position, auxPrice=entry, orderType='STP', action='BUY')
        order_SELL = Order(totalQuantity=position, auxPrice=stop, orderType='STP', action='SELL')
        # Set account number for orders
        order_BUY.account = account_num
        order_SELL.account = account_num
        # Place orders
        trade_BUY = ib.placeOrder(stock, order_BUY)
        trade_SELL = ib.placeOrder(stock, order_SELL)
        # Update labels with Order IDs
        orderId_entry_labels[col].configure(text=f"Order ID Entry: {trade_BUY.order.orderId}")
        orderId_stop_labels[col].configure(text=f"Order ID Stop: {trade_SELL.order.orderId}")
        
        display_message(system_message, f"✅ Orders submitted: {name}, Entry={entry}, Stop={stop}, Position={position}", color="green")

    except Exception as e:
        display_message(system_message, f"⚠️ Order submission failed: {str(e)}", color="yellow")
        #print(f"Orders have been successfully submitted: Name={value_name}, Entry={value_entry}, Stop price={value_stop}, Position={position}")



