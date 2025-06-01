import customtkinter
from ib_insync import *
from typing import Union, List
ib = IB() # Define ib globally
import math

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
checkbox_vars = {}
checkboxs = {}


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

def display_message(frame: customtkinter.CTkLabel, msg: Union[str, list[str]], color: str = "white"):
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


########################################################################
######### Create buttons and entries in the connectivity frame #########
########################################################################
dropdown_var = customtkinter.StringVar(value="Select account")
accounts_menu = create_dropdown_relative_position(master=button_frame, variable=dropdown_var, values=accounts)

port = create_entry_relative_position(master=button_frame, placeholder_text="Conn Port", side="right")
client_id = create_entry_relative_position(master=button_frame, placeholder_text="Client ID", side="right")
connect_reconnect_button = create_button_relative_position(master=button_frame, text="Disconnected", command=connect_ib, side="left")


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

        stp_button = create_button_grid_position(frame, "Summit STP Order",lambda c=col: link_order(c), row=8, column=col)
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
    risk = float(stp_risk_USD_entries[col].get())
    name = float(stp_name_entries[col].get())
    entry = float(stp_entry_entries[col].get())
    stop = float(stp_loss_entries[col].get())

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

def initial_ORB_order(col: int):
    
    # Clear previous messages
    display_message(system_message, "", color="white") 
    
    # Get input values
    value_risk = float(stp_risk_USD_entries[col].get())
    value_name = stp_name_entries[col].get()
    value_entry = float(stp_entry_entries[col].get())
    value_stop = float(stp_loss_entries[col].get())

    account = dropdown_var.get()
    transmit = checkbox_vars[col].get()

    # Debugging line
    print(f"Initial ORB Button pressed in column {col+1}: Name={value_name}, Risk={value_risk}, Entry={value_entry}, Stop={value_stop}, Account={account}, Transmit={transmit}")
    
    missing_fields = []
    if not value_risk:
        missing_fields.append("Risk in USD")
    if not value_name:
        missing_fields.append("Ticker name")
    if not value_entry:
        missing_fields.append("Entry")
    if not value_stop:
        missing_fields.append("Stop loss")

    if missing_fields:
        missing_message = f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields."
        display_message(system_message, missing_message, color="red")
        return  # Stop execution if fields are missing
    
    try:
        stock = Stock(symbol=value_name, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock)
        
        # Calculate position
        budget = round((value_risk * 100)/(((value_entry-value_stop)/value_entry)*100), 2)
        position = math.floor(budget/value_entry)
        print(f"Calculated budget: {budget}, Position: {position}") # Debugging line
        # Create orders
        order_BUY = Order(totalQuantity=position, auxPrice=value_entry, orderType='STP', action='BUY')
        order_SELL = Order(totalQuantity=position, auxPrice=value_stop, orderType='STP', action='SELL')
        
        # Place orders
        trade_BUY = ib.placeOrder(stock, order_BUY)
        trade_SELL = ib.placeOrder(stock, order_SELL)
        
        # Update labels with Order IDs
        orderId_entry_labels[col].configure(text=f"Order ID Entry: {trade_BUY.order.orderId}")
        orderId_stop_labels[col].configure(text=f"Order ID Stop: {trade_SELL.order.orderId}")
        
        display_message(system_message, f"✅ Orders submitted: {value_name}, Entry={value_entry}, Stop={value_stop}, Position={position}", color="green")

    except Exception as e:
        display_message(system_message, f"⚠️ Order submission failed: {str(e)}", color="yellow")
        #print(f"Orders have been successfully submitted: Name={value_name}, Entry={value_entry}, Stop price={value_stop}, Position={position}")

def test_button(col: int):
    # Clear previous messages
    display_message(system_message, "", color="white")
    # Get input values
    name = stp_name_entries[col].get()
    risk = float(stp_risk_USD_entries[col].get())
    entry = float(stp_entry_entries[col].get())
    stop = float(stp_loss_entries[col].get())
    lmt = float(lmt_entry_entries[col].get())
    account = dropdown_var.get()
    transmit = checkbox_vars[col].get()

    # Create a stock contract
    stock = Stock(symbol=name, exchange='SMART', currency='USD')
    ib.qualifyContracts(stock)

    budget = (risk * 100)/(((entry-stop)/entry)*100)
    position = math.floor(budget/entry)

    # Create orders
    order_BUY = Order(totalQuantity=position, auxPrice=entry, orderType='STP', action='BUY')
    order_SELL = Order(totalQuantity=position, auxPrice=stop, orderType='STP', action='SELL')

    # Set account number for orders
    order_BUY.account = account
    order_SELL.account = account

    # Set transmit flag for bracket order logic
    order_BUY.transmit = False  # Do not transmit yet
    order_SELL.transmit = True  # Transmit both orders together

    # Place orders
    trade_BUY = ib.placeOrder(stock, order_BUY)
    trade_SELL = ib.placeOrder(stock, order_SELL)
    # Update labels with Order IDs
    orderId_entry_labels[col].configure(text=f"Order ID Entry: {trade_BUY.order.orderId}")
    orderId_stop_labels[col].configure(text=f"Order ID Stop: {trade_SELL.order.orderId}")

    # I need to print these with display_message function
    display_message(system_message, f"Test Button pressed in column {col}: Name={name}, Risk={risk}, Entry={entry}, Stop={stop}, Position={position}, Budget={budget}, Account={account}, Save={transmit}")
    return None

def link_order(col: int):
    # Specify contract
    symbol = stp_name_entries[col].get()
    entry_val = stp_entry_entries[col].get()
    stop_val = stp_loss_entries[col].get()
    risk_val = stp_risk_USD_entries[col].get()

    # Input validation
    missing_fields = []
    if not symbol:
        missing_fields.append("Ticker name")
    if not entry_val:
        missing_fields.append("Entry price")
    if not stop_val:
        missing_fields.append("Stop loss")
    if not risk_val:
        missing_fields.append("Risk in USD")
    if missing_fields:
        display_message(system_message, f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields.", color="red")
        return

    stock = Stock(symbol=symbol, exchange='SMART', currency='USD')
    ib.qualifyContracts(stock)

    # Define your values
    account = dropdown_var.get()        # your actual account number
    entry_price = float(entry_val)         # your STP Buy price
    stop_price = float(stop_val)         # your STP Sell price
    risk = float(risk_val)  # FIX: ensure risk is float

    budget = (risk * 100)/(((entry_price-stop_price)/entry_price)*100)
    quantity = math.floor(budget/entry_price)

    # Define the STP BUY order (entry)
    buy_order = Order(
        action='BUY',
        totalQuantity=quantity,
        orderType='STP',
        auxPrice=entry_price,
        tif='GTC',              # Good-Til-Cancelled
        account=account,
        transmit=False          # Do not transmit yet — needed to link children
    )

    # Define the STP SELL order (risk management)
    sell_order = Order(
        action='SELL',
        totalQuantity=quantity,
        orderType='STP',
        auxPrice=stop_price,
        tif='GTC',
        parentId=0,             # will update this after placing the BUY order
        account=account,
        transmit=True           # last in the chain transmits all orders
    )

    # Place parent order
    trade_BUY = ib.placeOrder(stock, buy_order)

    # Wait until order has an ID
    print("Waiting for BUY order to be registered...")
    ib.sleep(10)  # Wait for the order to be registered
    parent_id = trade_BUY.order.orderId
    print(f"BUY order registered with ID: {parent_id}")

    # Update child with parentId
    sell_order.parentId = parent_id

    # Optional: Set OCA group so one cancels the other
    oca_group = f"OCA_{symbol}_{parent_id}"
    buy_order.ocaGroup = oca_group
    sell_order.ocaGroup = oca_group
    buy_order.ocaType = 1  # CANCEL_WITH_BLOCK
    sell_order.ocaType = 1

    # Place the SELL order
    trade_SELL = ib.placeOrder(stock, sell_order)

    # Monitor or wait for completion
    print(f"BUY order ID: {trade_BUY.order.orderId}")
    print(f"SELL order ID: {trade_SELL.order.orderId}")
