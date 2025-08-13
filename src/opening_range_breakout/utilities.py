import customtkinter
from ib_insync import *
from typing import Union, List
import math
from typing import Dict, Any
from time import sleep
import pandas as pd
from tkinter import filedialog
import openpyxl
from common import *
from ib_utilities import fetch_open_orders_df
import xml.etree.ElementTree as ET
from datetime import datetime
import numpy as np

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
modify_buttons = {}
orderid_entries = {}

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

def show_open_orders_widget(master=None):
    # Create a new window or frame for the table
    orders_win = customtkinter.CTkToplevel(master or root)
    orders_win.title("Open Orders")
    orders_win.geometry("1100x400")

    # Add a refresh button
    def refresh_table():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        df = fetch_open_orders_df(ib)
        if df.empty:
            customtkinter.CTkLabel(scroll_frame, text="No open orders found.", text_color="yellow").grid(row=0, column=0)
            return
        # Add headers
        for j, col in enumerate(df.columns):
            customtkinter.CTkLabel(scroll_frame, text=col, font=("Arial", 12, "bold")).grid(row=0, column=j, padx=2, pady=2)
        # Add rows
        for i, row in df.iterrows():
            for j, value in enumerate(row):
                customtkinter.CTkLabel(scroll_frame, text=str(value), font=("Arial", 11)).grid(row=i+1, column=j, padx=2, pady=2)

    refresh_btn = customtkinter.CTkButton(orders_win, text="Refresh", command=refresh_table, fg_color="blue")
    refresh_btn.pack(pady=5)

    scroll_frame = customtkinter.CTkScrollableFrame(orders_win, width=1050, height=320)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    refresh_table()  # Initial load of the table

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
button_frame_2 = create_frame_relative_position(master = root, relx = 0, rely = 0, anchor='nw')

"""
Ideas:
Create function to provide file_path. This action keeps repeating in the code.
"""
def load_excel_files():
    # Open file dialog for file1
    file1_path = filedialog.askopenfilename(title="Select the file to update (.xlsx or xls)", filetypes=[("Excel files", "*.xlsx *.xls")])
    
    if not file1_path:
        display_message(system_message, "No file selected for updating!", color="red")
        return

    # Read all sheets from file1
    required_sheets = ['Summary', 'Stock Activity', 'Active Orders', 'Positions']
    
    try:
        # Read all required sheets into a dict of DataFrames
        load_sheets = pd.read_excel(file1_path, sheet_name=required_sheets)
        # Assign each DataFrame to a variable with the same name
        Summary = load_sheets['Summary']
        Stock_Activity = load_sheets['Stock Activity']
        Active_Orders = load_sheets['Active Orders']
        Positions = load_sheets['Positions']
        # Delete calculated columns
        Active_Orders.drop(columns='Total Liq Amount', inplace=True)
        Positions.drop(columns=['Action', 'Cost', 'Total Liq Amount', 'Capital Exposure'], inplace=True)
        # Store in a dictionary for later use
        sheets_file_update = {
            'Summary': Summary,
            'Stock Activity': Stock_Activity,
            'Active Orders': Active_Orders,
            'Positions': Positions
        }
        display_message(system_message, "File loaded successfully!", color="green")

        file2_path = filedialog.askopenfilename(title="Select XML file with trading activity", filetypes=[("XML files", "*.xml")])
        
        if file2_path:
            file_xml = ET.parse(file2_path)
            # ... continue processing ...
        else:
            # Handle case where user cancels
            display_message(system_message, "No file selected for trade operation.", color="yellow")

        file3_path = filedialog.askopenfilename(title="Select your updated GP file (.xlsx or xls)", filetypes=[("Excel files", "*.xlsx *.xls")])
        
        if not file1_path:
            display_message(system_message, "No GP file selected.", color="yellow")
            return

        gp_df = pd.read_excel(file3_path, sheet_name='gameplan')

        # Ask user for save path
        default_filename = f"trading_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel File As",
            initialfile=default_filename
                )
        
        if not save_path:
            display_message(system_message, "Save cancelled by user.", color="yellow")
            return

        get_ib_information(sheets_file_update, file_xml, gp_df, save_path, default_filename)

    except Exception as e:
        display_message(system_message, f"Error reading file or missing required sheets: {e}", color="red")
        return

def get_ib_information(sheets_file_update, file_xml, gp_df, save_path, default_filename):
    if not ib.isConnected():
        display_message(system_message, "⚠️ Not connected to IB. Please connect first.", color="red")
        return
    
    account_ids = ib.managedAccounts()

    # -----------------------------------------
    # ✅ 1. Fetch Account Information Summary #
    # -----------------------------------------
    # Use delayed market data
    ib.reqMarketDataType(3)

    # Fetch all account values once
    account_values = ib.accountValues()
    account_df = util.df(account_values)

    # Prepare list to hold per-account results
    all_account_data = []

    # Loop through each account
    for account_id in account_ids:
        def get_summary_value(tag):
            row = account_df.loc[(account_df['tag'] == tag) & (account_df['account'] == account_id)]
            return row['value'].values[0] if not row.empty else None

        # Manually calculate Unrealized PnL for this account
        positions = ib.positions()
        unrealized_total = 0.0

        for pos in positions:
            if pos.account != account_id:
                continue

            contract = pos.contract
            avg_cost = pos.avgCost
            quantity = pos.position

            ib.qualifyContracts(contract)
            ticker = ib.reqMktData(contract, snapshot=True)
            ib.sleep(1.5)  # Avoid pacing violations

            price = (
                getattr(ticker, "last", None) or
                getattr(ticker, "delayedLast", None) or
                getattr(ticker, "close", None) or
                getattr(ticker, "delayedClose", None)
            )

            if price is not None:
                unrealized_total += (price - avg_cost) * quantity

        # Save result for this account
        account_data = {
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Account': account_id,
            'Net Liquidation': get_summary_value('NetLiquidation'),
            'Cash Balance': get_summary_value('TotalCashValue'),
            'Realized PnL': get_summary_value('RealizedPnL'),
            'Unrealized PnL (manual)': unrealized_total,
            'Market Value (Equity)': get_summary_value('EquityWithLoanValue'),
            'Market Value (Cash)': get_summary_value('TotalCashValue')
        }

        all_account_data.append(account_data)

    # Final concatenated DataFrame
    summary_df = pd.DataFrame(all_account_data)

    for col in [
        'Net Liquidation',
        'Cash Balance',
        'Realized PnL',
        'Unrealized PnL (manual)',
        'Market Value (Equity)',
        'Market Value (Cash)'
    ]:
        summary_df[col] = pd.to_numeric(summary_df[col], errors='coerce')

    # --------------------------------------
    # ✅ 2. Fetch Trades (Stock Activities)
    # --------------------------------------
    root = file_xml.getroot()

    # 2. Extract records
    records = []
    for stmt in root.findall('.//FlexStatement'):
        account_id = stmt.get('accountId')
        confirms = stmt.find('TradeConfirms')
        if confirms is None:
            continue
        for elem in confirms:
            record = {'AccountId': account_id, 'RecordType': elem.tag}
            # Copy every attribute on the element
            record.update(elem.attrib)
            records.append(record)

    # 3. Build DataFrame
    df = pd.DataFrame(records)

    # 4. (Optional) Convert numeric fields
    numeric_cols = ['quantity', 'price', 'amount', 'netCash', 'commission']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # assume `df` is your parsed DataFrame
    # first, parse the relevant datetime columns
    df['dateTime'] = pd.to_datetime(df['dateTime'].str.replace(';', ' '), errors='coerce')
    df['orderTime'] = pd.to_datetime(df['orderTime'].str.replace(';', ' '), errors='coerce')

    # Ensure numeric columns are typed
    numeric_cols = ['quantity', 'price', 'amount', 'netCash', 'commission']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Split by record type
    df_summary = df[df.RecordType == 'SymbolSummary']   # one row per symbol summary
    df_orders  = df[df.RecordType == 'Order']            # the parent orders
    df_fills   = df[df.RecordType == 'TradeConfirm']     # the individual fills

    # 1) Aggregate fills per orderID + symbol
    fills_agg = (
        df_fills
        .groupby(['orderID', 'symbol'])
        .agg(
            FilledQty       = ('quantity', 'sum'),
            FillAmount      = ('amount',   'sum'),
            TotalCommission = ('commission','sum'),
            # you could also compute a weighted avg fill price:
            AvgFillPrice    = ('price', lambda x: (x * df_fills.loc[x.index,'quantity']).sum() / x.sum())
        )
        .reset_index()
    )

    # 2) Merge with orders
    orders_full = (
        df_orders
        .merge(fills_agg, on=['orderID','symbol'], how='left')
        .assign(
            OrderQty      = lambda d: d['quantity'],
            OrderPrice    = lambda d: d['price']
        )
        .rename(columns={
            'tradeDate': 'OrderDate',
            'trafficType': 'TransactionType'
        })
        # select/rename the columns you care about
        [['AccountId','symbol','orderID','OrderDate','OrderQty','OrderPrice',
        'FilledQty','AvgFillPrice','FillAmount','TotalCommission']]
    )
    orders_full['orderID'] = pd.to_numeric(orders_full['orderID'], errors='coerce')
    # 3) (Optional) Combine with summary for a top-level view
    # Group by accountId + symbol, summing quantity and amount
    symbol_totals = (
        df_summary
        .groupby(['accountId', 'symbol'], as_index=False)
        .agg(
            SummaryQty    = ('quantity', 'sum'),
            SummaryAmount = ('amount',   'sum')
        )
        # Rename accountId → AccountId for clarity (optional)
        .rename(columns={'accountId':'AccountId'})
    )


    # --------------------------------------
    # ✅ 3. Fetch Open Positions
    # --------------------------------------

    # Use delayed market data
    ib.reqMarketDataType(3)

    # Today's date
    today = datetime.now().strftime('%Y-%m-%d')

    # Store all position records here
    position_records = []

    # Loop through each account
    for account_id in account_ids:
        positions = ib.positions(account=account_id)

        for pos in positions:
            contract = pos.contract
            quantity = pos.position
            avg_cost = pos.avgCost

            # Fetch snapshot price
            ib.qualifyContracts(contract)
            ticker = ib.reqMktData(contract, snapshot=True)
            ib.sleep(1.0)  # Respect pacing limits

            # Handle missing/delayed data safely
            price = (
                getattr(ticker, 'last', None)
                or getattr(ticker, 'close', None)
                or getattr(ticker, 'delayedLast', None)
                or getattr(ticker, 'delayedClose', None)
                or 0.0
            )

            market_value = price * quantity
            unrealized_pnl = (price - avg_cost) * quantity
            realized_pnl = None  # Not exposed in positions API

            position_records.append({
                'Date': today,
                'Account': account_id,
                'Symbol': contract.symbol,
                'Quantity': quantity,
                'Average Cost': avg_cost,
                'Current Price': price,
                'Market Value': market_value,
                'Unrealized PnL': unrealized_pnl,
                'Realized PnL': realized_pnl,
                'Currency': contract.currency
            })
        # Create final DataFrame
        df_positions = pd.DataFrame(position_records)

    # --------------------------------------
    # ✅ 4. Fetch Active Orders
    # --------------------------------------
    # Prepare current date once
    today = datetime.now().strftime('%Y-%m-%d')

    # Fetch all open orders
    open_orders = ib.reqAllOpenOrders()

    # Container for all records
    order_records = []

    # Loop through each account
    for account_id in account_ids:
        for order in open_orders:
            order_obj = order.order

            # Filter by account
            if order_obj.account != account_id:
                continue

            contract = order.contract

            order_records.append({
                'Date':        today,
                'Account':     account_id,
                'Order ID':    order_obj.orderId,
                'Symbol':      contract.symbol,
                'Action':      order_obj.action,
                'Order Type':  order_obj.orderType,
                'Quantity':    order_obj.totalQuantity,
                'Lmt Price':   order_obj.lmtPrice,
                'Aux Price':   order_obj.auxPrice,
                'TIF':         order_obj.tif,
                'Transmit':    order_obj.transmit,
                'Status':      order.orderStatus.status
            })

    # Create final DataFrame
    df_orders = pd.DataFrame(order_records)

    # Ensure orderID is numeric in both DataFrames
    sheets_file_update['Stock Activity']['orderID'] = pd.to_numeric(sheets_file_update['Stock Activity']['orderID'], errors='coerce')
    orders_full['orderID'] = pd.to_numeric(orders_full['orderID'], errors='coerce')

    # Concatenate old and new DataFrames for each sheet
    concat_summary_df = pd.concat([sheets_file_update['Summary'], summary_df], ignore_index=True).drop_duplicates()
    concat_orders_full = pd.concat([sheets_file_update['Stock Activity'], orders_full], ignore_index=True).drop_duplicates()
    concat_orders = pd.concat([sheets_file_update['Active Orders'], df_orders], ignore_index=True).drop_duplicates()
    concat_position = pd.concat([sheets_file_update['Positions'], df_positions], ignore_index=True).drop_duplicates()
    
    concat_orders['multi'] = np.where(
    concat_orders['Action'] == "SELL",  # condition
    1,          # value if True
    -1            # value if False
)
    concat_orders['Total Liq Amount'] = ((concat_orders['Quantity'] * concat_orders['Aux Price']))* concat_orders['multi']
    concat_position['Action'] = np.where(
    concat_position['Quantity'] > 0,  # condition
    'SELL',          # value if True
    'BUY'            # value if False
)
    concat_orders.drop(columns='multi', inplace=True)
    concat_position['Order Type'] = 'STP'
    concat_position['Cost'] = concat_position['Quantity'] * concat_position['Average Cost']
    keys_to_merge = ['Date', 'Account', 'Symbol', 'Action', 'Order Type']
    total_amount_stploss = concat_orders.groupby(keys_to_merge)['Total Liq Amount'].sum().reset_index()
    concat_position = concat_position.merge(total_amount_stploss, on=keys_to_merge, how='left')
    concat_position['Capital Exposure'] = concat_position['Total Liq Amount'] - concat_position['Cost']
    
    # --------------------------------------
    # ✅ 5. Saving as excell file
    # --------------------------------------
    # Save to Excel with multiple sheets
    with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
        concat_summary_df.to_excel(writer, sheet_name='Summary', index=False)
        concat_orders_full.to_excel(writer, sheet_name='Stock Activity', index=False)
        concat_orders.to_excel(writer, sheet_name='Active Orders', index=False)
        concat_position.to_excel(writer, sheet_name='Positions', index=False)

    display_message(system_message, f"File {default_filename} Successfully saved!", color="green")

########################################################################
######### Create buttons and entries in the connectivity frame #########
########################################################################
dropdown_var = customtkinter.StringVar(value="Select account")
accounts_menu = create_dropdown_relative_position(master=button_frame, variable=dropdown_var, values=accounts)

port = create_entry_relative_position(master=button_frame, placeholder_text="Conn Port", side="right", width=60)
client_id = create_entry_relative_position(master=button_frame, placeholder_text="Client ID", side="right", width=60)
connect_reconnect_button = create_button_relative_position(master=button_frame, text="Disconnected", command=connect_ib, side="left")

load_excel_button = create_button_relative_position(master=button_frame_2, text="Load Excel Files", command=load_excel_files, side="right", width=120, fg_color="gray")

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
        checkbox_s = create_checkbox_grid_position(frame, text = "Not include STP loss", tracking_variable = checkbox_s_var, row = 2, column = col, width = 1, height =1)
        checkboxs_s[col] = checkbox_s

        checkbox_sh_var = customtkinter.BooleanVar(value=False) 
        checkbox_sh_vars[col] = checkbox_sh_var
        checkbox_sh = create_checkbox_grid_position(frame, text = "Sell position", tracking_variable = checkbox_sh_var, row = 3, column = col, width = 1, height =1)
        checkboxs_sh[col] = checkbox_sh

        spacer_1 = create_label_grid_position(frame, text="", row=4, column=col)
        stp_name = create_entry_grid_position(frame, "Name", row=5, column=col)
        stp_name_entries[col] = stp_name

        stp_risk_USD = create_entry_grid_position(frame, "Risk in USD", row=6, column=col)
        stp_risk_USD_entries[col] = stp_risk_USD

        positions = create_entry_grid_position(frame, "Position", row=7, column=col)
        position_entries[col] = positions

        #orderId_entry_label = create_label_grid_position(frame, "Order ID Entry:", row=8, column=col)
        #orderId_entry_labels[col] = orderId_entry_label

        stp_entry = create_entry_grid_position(frame, "Entry", row=8, column=col)
        stp_entry_entries[col] = stp_entry

        #orderId_stop_label = create_label_grid_position(frame, "Order ID Stop:", row=10, column=col)
        #orderId_stop_labels[col] = orderId_stop_label

        stp_loss = create_entry_grid_position(frame, "Stop Loss", row=9, column=col)
        stp_loss_entries[col] = stp_loss

        stp_button = create_button_grid_position(frame, "Summit STP Order",lambda c=col: stp_order(c), row=10, column=col)
        stp_buttons[col] = stp_button

        #orderId_lmt_label = create_label_grid_position(frame, "Order ID Limit:", row=13, column=col)
        #orderId_lmt_labels[col] = orderId_lmt_label

        spacer_2 = create_label_grid_position(frame, text="", row=11, column=col)
        lmt_entry = create_entry_grid_position(frame, "Limit Price", row=12, column=col)
        lmt_entry_entries[col] = lmt_entry

        lmt_button = create_button_grid_position(frame, "Summit Limit Order", frame, row=13, column=col)
        lmt_buttons[col] = lmt_button

        spacer_3 = create_label_grid_position(frame, text="", row=14, column=col)
        orderid_entry = create_entry_grid_position(frame, "order ID", row=15, column=col)
        orderid_entries[col] = orderid_entry

        modify_button = create_button_grid_position(frame, "Modify Order", lambda c=col: modify_order(c), row=16, column=col)
        modify_buttons[col] = modify_button

        cancel_button = create_button_grid_position(frame, "Cancel Order", lambda c=col: cancel_order(c), row=17, column=col)
        cancel_buttons[col] = cancel_button

        spacer_4 = create_label_grid_position(frame, text="", row=18, column=col)
        mkt_button = create_button_grid_position(frame, "Submit Sell MKT Order", frame, row=19, column=col)
        mkt_buttons[col] = mkt_button

# Add a button to your main UI to open this widget
open_orders_btn = create_button_relative_position(
    master=button_frame_2,
    text="Show Open Orders",
    command=show_open_orders_widget,
    side="left",
    width=120,
    fg_color="gray"
)

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
        "account": dropdown_var.get(),
        "order_id": orderid_entries[col].get()
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

def stp_order(col: int):
    
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
    if (order == "Risk-based Buy/Sell order") | (order == "Risk-based Sell/Buy order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nRisk USD: {values['risk_USD']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    elif(order == "Position-based Buy/Sell order") | (order == "Position-based Sell/Buy order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    elif(order == "Position-based Buy order") | (order == "Position-based Sell order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    
    confirm_operation(mes + order_summary, on_yes = proceed, on_no = cancel)

def lmt_order(col: int):
    
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
    if (order == "Risk-based Buy/Sell order") | (order == "Risk-based Sell/Buy order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nRisk USD: {values['risk_USD']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    elif(order == "Position-based Buy/Sell order") | (order == "Position-based Sell/Buy order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    elif(order == "Position-based Buy order") | (order == "Position-based Sell order"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
    
    confirm_operation(mes + order_summary, on_yes = proceed, on_no = cancel)

def modify_order(col: int):
    """
    Modify orders based on order ID
    """
    ######################
    #   1. Get values    #
    ######################
    values = get_values(col)

    valid, order, flag_fields_ok, missing_fileds = validate_info_mod_button(values)

    if not valid:
        display_message(system_message, f"⚠️ {order}", color="red")
        return
    
    if not flag_fields_ok:
        display_message(system_message, f"⚠️ Missing: {', '.join(missing_fileds)}. Please fill in all fields.", color="red")
        return
    
    order_id = int(values['order_id'])
    account_id = values['account']
    try:
        ent = int(values['entry'])
    except ValueError:
        ent = None
    try:
        pos = int(values['position'])
    except ValueError:
        pos = None
    
    def cancel():
        display_message(system_message, "Operation cancelled by user", color="yellow")

    def proceed():

        # Get all open orders
        open_orders = ib.reqAllOpenOrders()
        
        print(f"Order Input: {type(order_id)}, Account Input: {type(account_id)}")
        for o in open_orders:
            print(f"o.order.orderId={o.order.orderId} ({type(o.order.orderId)}), input order_id={order_id} ({type(order_id)})")
            print(f"o.order.account={o.order.account} ({type(o.order.account)}), input account_id={account_id} ({type(account_id)})")
        
        # Find your order by ID and account
        matching_order = next(
            (o for o in open_orders 
            if o.order.orderId == order_id and o.order.account == account_id),
            None
        )

        if matching_order is None:
            return display_message(system_message, f"⚠️ No open order found with orderId {values['order_id']} for account {values['account']}.")
        
        # Current values
        current_order: Order = matching_order.order
        order_type = current_order.orderType.upper()
        current_quantity = current_order.totalQuantity

        # Decide new quantity
        new_quantity = pos if pos is not None else current_quantity

        # Decide new quantity (LMT/STP)
        new_lmt_price = current_order.lmtPrice
        new_aux_price = current_order.auxPrice

        if ent is not None:
            if order_type == 'LMT':
                new_lmt_price = float(ent)
            elif order_type == 'STP':
                new_aux_price = float(ent)
            else:
                return display_message(system_message, f"⚠️ Order type {order_type} not supported for modification.", color = "red")

        # Prepare the modified order
        modified_order = Order(
            orderId = order_id,
            account = account_id,
            action = current_order.action,
            totalQuantity = new_quantity,
            orderType = order_type,
            lmtPrice = new_lmt_price,
            auxPrice = new_aux_price,
            tif = current_order.tif,
            transmit = True
        )

        # Send modification
        ib.placeOrder(matching_order.contract, modified_order)

        display_message(system_message, f"MODIFIED -> Order={order_id}, Position={new_quantity}, stpPrice={new_aux_price}, lmtPrice={new_lmt_price}", color="green")
  
    mes = "Are you sure you want to modify this order?\n"
    if (order == "Modify order with new price and position size"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: --> ({order})\nOrder ID: {values['order_id']}\nNew Price: {values['entry']}\nPosition: {values['position']}\nAccount: {values['account']}"
    elif(order == "Modify order with new price"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: --> ({order})\nOrder ID: {values['order_id']}\nNew Price: {values['entry']}\nAccount: {values['account']}"
    elif(order == "Modify order with new position size"):
        order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: --> ({order})\nOrder ID: {values['order_id']}\nPosition: {values['position']}\nAccount: {values['account']}"
    
    confirm_operation(mes + order_summary, on_yes = proceed, on_no = cancel)

def cancel_order(col: int):
    
    """
    Cancel orders based on order ID and account
    """
    ######################
    #   1. Get values    #
    ######################
    values = get_values(col)

    valid, order, flag_fields_ok, missing_fileds = validate_info_cancel_button(values)

    if not valid:
        display_message(system_message, f"⚠️ {order}", color="red")
        return
    
    if not flag_fields_ok:
        display_message(system_message, f"⚠️ Missing: {', '.join(missing_fileds)}. Please fill in all fields.", color="red")
        return
    
    order_id = int(values['order_id'])
    account_id = values['account']
    
    def cancel():
        display_message(system_message, "Operation cancelled by user", color="yellow")

    def proceed():

        # Get all open orders
        open_orders = ib.reqAllOpenOrders()
        
        # Find your order by ID and account
        matching_order = next(
            (o for o in open_orders 
            if o.order.orderId == order_id and o.order.account == account_id),
            None
        )

        if matching_order is None:
            return display_message(system_message, f"⚠️ No open order found with orderId {values['order_id']} for account {values['account']}.")
        
        # Cancel the order
        ib.cancelOrder(matching_order.order)

        display_message(system_message, f"CANCELATION -> Order={order_id}, Account={account_id} has been requested", color="green")

    mes = "Are you sure you want to cancel this order?\n"
    order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nMessage: --> ({order})\nOrder ID: {values['order_id']}\nAccount: {values['account']}"
  
    confirm_operation(order_summary, on_yes = proceed, on_no = cancel)