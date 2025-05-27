import customtkinter
from ib_insync import *
ib = IB() # Define ib globally

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
root =  customtkinter.CTk()
root.geometry("500x800")

# System message label
system_message = customtkinter.CTkLabel(master=root, text="IBKR Trading Interface Program", text_color="white", wraplength=450)
system_message.pack(pady=10)

def display_message(msg, color="white"):
    ### Update the system message label dynamically
    system_message.configure(text=msg, text_color=color)
## Connect/Disconnect to IB Gateway
def connect_ib():
    
    # Clear previous messages
    display_message("", color="white")
    
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
        display_message(missing_message, color="red")
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
        display_message(f"⚠️ Order submission failed: {str(e)}", color="yellow")
## Update Connect Re-Connect Button
def update_button_status():
    ### Updates the button text and color based on connection status.
    if ib.isConnected():
        connect_reconnect_button.configure(text="Connected", fg_color="green")
    else:
        connect_reconnect_button.configure(text="Disconnected", fg_color="red")

    # Re-check status every 1 second
    root.after(1000, update_button_status)
## Initial ORB Order -> This contains entry price and stop price
def initial_ORB_order():
    
    # Clear previous messages
    display_message("", color="white") 
    
    # Get input values
    value_risk = risk.get().strip()
    value_name = name.get().strip()
    value_entry = entry.get().strip()
    value_stop = stop.get().strip()

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
        display_message(missing_message, color="red")
        return  # Stop execution if fields are missing
    
    try:
        stock = Stock(symbol=value_name, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock)
        
        # Convert str values to numeric
        value_risk = float(value_risk)
        value_entry = float(value_entry)
        value_stop = float(value_stop)
        
        # Calculate position
        budget = (value_risk * 100)/(((value_entry-value_stop)/value_entry)*100)
        position = round(budget/value_entry)
        
        # Create orders
        order_BUY = Order(totalQuantity=position, auxPrice=value_entry, orderType='STP', action='BUY')
        order_SELL = Order(totalQuantity=position, auxPrice=value_stop, orderType='STP', action='SELL')
        
        # Place orders
        trade_BUY = ib.placeOrder(stock, order_BUY)
        trade_SELL = ib.placeOrder(stock, order_SELL)
        
        # Update labels with Order IDs
        orderId_entry_label.configure(text=f"Order ID Entry: {trade_BUY.order.orderId}")
        orderId_stop_label.configure(text=f"Order ID Stop: {trade_SELL.order.orderId}")
        
        display_message(f"✅ Orders submitted: {value_name}, Entry={value_entry}, Stop={value_stop}, Position={position}", color="green")

    except Exception as e:
        display_message(f"⚠️ Order submission failed: {str(e)}", color="yellow")
        #print(f"Orders have been successfully submitted: Name={value_name}, Entry={value_entry}, Stop price={value_stop}, Position={position}")
## Limit Order -> This executes a Sell Limit order at profit levels
def limit_order():
    # Clear previous messages
    display_message("", color="white") 
    
    # Get input values
    value_risk = risk.get().strip()
    value_name = name.get().strip()
    value_entry = entry.get().strip()
    value_stop = stop.get().strip()
    value_limit = limit.get().strip()

    missing_fields = []
    if not value_risk:
        missing_fields.append("Risk in USD")
    if not value_name:
        missing_fields.append("Ticker name")
    if not value_entry:
        missing_fields.append("Entry")
    if not value_stop:
        missing_fields.append("Stop loss")
    if not value_limit:
        missing_fields.append("Limit price")

    if missing_fields:
        missing_message = f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields."
        display_message(missing_message, color="red")
        return  # Stop execution if fields are missing
        
    try:
        stock_limit = Stock(symbol=value_name, exchange='SMART', currency='USD')
        ib.qualifyContracts(stock_limit)
        
        # Convert str values to numeric
        value_limit = float(value_limit)
        value_risk = float(value_risk)
        value_entry = float(value_entry)
        value_stop = float(value_stop)
        
        # Calculate position
        budget = (value_risk * 100)/(((value_entry-value_stop)/value_entry)*100)
        position = round(budget/value_entry)
        
        # Create orders
        order_SELL_LMT = Order(totalQuantity=position, lmtPrice=value_limit, orderType='LMT', action='SELL')
        
        # Place orders
        trade_SELL_LMT = ib.placeOrder(stock_limit, order_SELL_LMT)
        
        # Update labels with Order IDs
        orderId_limit_label.configure(text=f"Order ID Entry: {trade_SELL_LMT.order.orderId}")
        
        display_message(f"✅ Orders submitted: {value_name}, Limit Price={value_limit}, Position={position}", color="green")

    except Exception as e:
        display_message(f"⚠️ Order submission failed: {str(e)}", color="yellow")
## Sell Market Order -> This executes a Sell Market order 
def market_order():
    
    stock = Stock(symbol = 'TSLA', exchange = 'SMART', currency = 'USD')
    ib.qualifyContracts(stock)
    order = Order(totalQuantity = 10, orderType = 'MKT', action = 'SELL')
    trade = ib.placeOrder(stock, order)
    
    # Clear previous messages
    display_message("", color="white") 
    
    # Get input values
    value_risk = risk.get().strip()
    value_name = name.get().strip()
    value_entry = entry.get().strip()
    value_stop = stop.get().strip()
    value_limit = limit.get().strip()

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
        display_message(missing_message, color="red")
        return  # Stop execution if fields are missing  
    
    try:
          
        # Convert str values to numeric
        value_limit = float(value_limit)
        value_risk = float(value_risk)
        value_entry = float(value_entry)
        value_stop = float(value_stop)
        
        # Calculate position
        budget = (value_risk * 100)/(((value_entry-value_stop)/value_entry)*100)
        position = round(budget/value_entry)
        
        # Create orders
        stock_MKT = Stock(symbol = value_name, exchange = 'SMART', currency = 'USD')
        ib.qualifyContracts(stock_MKT)
        order_MKT = Order(totalQuantity = position, orderType = 'MKT', action = 'SELL')
        
        # Place orders
        trade_SELL_MKT = ib.placeOrder(stock_MKT, order_MKT)
        
        # Getting average filled price
        avg_filled_price = trade_SELL_MKT.orderStatus.avgFillPrice
        
        display_message(f"✅ Order submitted: {value_name}, Market Price={avg_filled_price}, Position={position}", color="green")

    except Exception as e:
        
        display_message(f"⚠️ Order submission failed: {str(e)}", color="yellow")
## Modify Sell STP Order -> This modify the full stop order
def mod_stp_order():
    value_new_stp = new_stop.get().strip()

    if not value_new_stp:
        print("Missing: New STP price. Please fill in the field.")
    else:
        print(f"New STP price: {value_new_stp}")
   
## Initial ORB Orders objects

frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)


label1 = customtkinter.CTkLabel(master=frame, text="First Ticker Name")
label1.grid(row=0, column=0, padx=5, pady=5, sticky="w")
name = customtkinter.CTkEntry(master=frame, placeholder_text="Name")
name.grid(row=1, column=0, padx=5, pady=5, sticky="w")
risk = customtkinter.CTkEntry(master=frame, placeholder_text="Risk in USD")
risk.grid(row=2, column=0, padx=5, pady=5, sticky="w")

# Entry Frame

###entry_label = customtkinter.CTkLabel(master=frame, text="Entry:")
###entry_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry = customtkinter.CTkEntry(master=frame, placeholder_text="Entry")
entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

orderId_entry_label = customtkinter.CTkLabel(master=frame, text="Order ID Entry:")
orderId_entry_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Stop Frame

###stop_label = customtkinter.CTkLabel(master=frame, text="Stop Loss:")
###stop_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

stop = customtkinter.CTkEntry(master=frame, placeholder_text="Stop Loss")
stop.grid(row=4, column=0, padx=5, pady=5, sticky="w")

orderId_stop_label = customtkinter.CTkLabel(master=frame, text="Order ID Stop:")
orderId_stop_label.grid(row=4, column=1, padx=5, pady=5, sticky="w")

button = customtkinter.CTkButton(master = frame, text = "Submit ORB Order", command = initial_ORB_order)
button.grid(row=5, column=0, padx=5, pady=5, sticky="w")

#######################################
# Create a frame for top-right buttons#
#######################################
button_frame = customtkinter.CTkFrame(master=root, fg_color="transparent")
button_frame.place(relx=1, rely=0, anchor="ne")  # Places in the top-right corner

#########################
# Connection Parameters #
#########################
port = customtkinter.CTkEntry(master = button_frame, placeholder_text = "Conn Port")
port.pack(side="right")
client_id = customtkinter.CTkEntry(master = button_frame, placeholder_text = "Client ID")
client_id.pack(side="right")

#################
# Small Buttons #
#################
connect_reconnect_button = customtkinter.CTkButton(master=button_frame, text="Disconnected", width=80, height=30, 
                                                   fg_color="red", command=connect_ib)
connect_reconnect_button.pack(side="left")

## Space # 1
# Spacer label to push items down
spacer = customtkinter.CTkLabel(master = frame, text = "")
spacer.grid(row=6, column=0, padx=5, pady=5, sticky="w")  # This creates extra space

## Limit objects

limit = customtkinter.CTkEntry(master = frame, placeholder_text = "Limit Price")
limit.grid(row=7, column=0, padx=5, pady=5, sticky="w")
orderId_limit_label = customtkinter.CTkLabel(master=frame, text="Order ID Limit:")
orderId_limit_label.grid(row=7, column=1, padx=5, pady=5, sticky="w")
limit_button = customtkinter.CTkButton(master = frame, text = "Submit Limit Order", command = limit_order)
limit_button.grid(row=8, column=0, padx=5, pady=5, sticky="w")

## Space # 2
# Spacer label to push items down
spacer = customtkinter.CTkLabel(master = frame, text = "")
spacer.grid(row=9, column=0, padx=5, pady=5, sticky="w")  # This creates extra space

## Market objects
market_button = customtkinter.CTkButton(master = frame, text = "Submit Sell MKT Order", command = market_order)
market_button.grid(row=10, column=0, padx=5, pady=5, sticky="w")

## Space # 3
# Spacer label to push items down
spacer = customtkinter.CTkLabel(master = frame, text = "")
spacer.grid(row=11, column=0, padx=5, pady=5, sticky="w")  # This creates extra space

## Modify Sell Stop Order bjects
new_stop = customtkinter.CTkEntry(master = frame, placeholder_text = "New Stop Price")
new_stop.grid(row=12, column=0, padx=5, pady=5, sticky="w")

order_id_mod = customtkinter.CTkEntry(master = frame, placeholder_text = "Order ID", width=60)
order_id_mod.grid(row=12, column=1, padx=5, pady=5, sticky="w")

new_limit = customtkinter.CTkEntry(master = frame, placeholder_text = "New Limit Price")
new_limit.grid(row=13, column=0, padx=5, pady=5, sticky="w")

new_qty = customtkinter.CTkEntry(master = frame, placeholder_text = "New Quantity")
new_qty.grid(row=14, column=0, padx=5, pady=5, sticky="w")

mod_stop_button = customtkinter.CTkButton(master = frame, text = "Submit Modified Order", command = mod_stp_order)
mod_stop_button.grid(row=15, column=0, padx=5, pady=5, sticky="w")

# Start monitoring connection status
update_button_status()
# Start main program
root.mainloop()