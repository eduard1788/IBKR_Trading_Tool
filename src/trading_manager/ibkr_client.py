import customtkinter
from time import sleep
import math
from ib_insync import IB, util, Order, Stock
from datetime import datetime
import pandas as pd
from .utils import TradingManagerUtils
from .widgets import *
from typing import Union, List, Dict, Any
from .constants import *

class IBKRClientAPI:

    def __init__(self):
        self.ib = IB()
        self.trading_manager_utils = TradingManagerUtils()
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")
        self.root = customtkinter.CTk()
        self.root.geometry("500x800")
        self.frame = create_frame_grid_position(self.root)
        self.button_frame = create_frame_relative_position(master = self.root, relx = 1, rely = 0)
        self.connect_reconnect_button = create_button_relative_position(master=self.button_frame, text="Disconnected", command=self.connect, side="left")
        self.port = create_entry_relative_position(master=self.button_frame, placeholder_text="Conn Port", side="right", width=60)
        self.client_id = create_entry_relative_position(master=self.button_frame, placeholder_text="Client ID", side="right", width=60)
        self.dropdown_var = customtkinter.StringVar(value="Select account")
        self.accounts_menu = create_dropdown_relative_position(master=self.button_frame, variable=self.dropdown_var, values=accounts)
        self.system_message = customtkinter.CTkLabel(master=self.root, text="", text_color="white", wraplength=450)
        self.system_message.pack(pady=10)
        self.button_frame_2 = create_frame_relative_position(master = self.root, relx = 0, rely = 0, anchor='nw')
        self.load_excel_button = create_button_relative_position(master=self.button_frame_2, text="Load Excel Files", command=IBKRClientAPI.connect, side="right", width=120, fg_color="gray")
        self.open_orders_btn = create_button_relative_position(master=self.button_frame_2, text="Show Open Orders", command=self.show_open_orders, side="left", width=120, fg_color="gray")

    def connect(self):
        # Clear previous messages
        # call display_message() with ""

        # Get connection parameters
        value_port = self.port.get().strip()
        value_client_id = self.client_id.get().strip()

        missing_fields = []
        if not value_port:
            missing_fields.append("Port Number")
        if not value_client_id:
            missing_fields.append("Client ID")
        if missing_fields:
            Missing_message = f"⚠️ Missing: {', '.join(missing_fields)}. Please fill in all fields."
            self.trading_manager_utils.display_message(self.system_message, Missing_message, color="red")
            return
        try:
            value_port = int(value_port)
            value_client_id = int(value_client_id)
        
            if not self.ib.isConnected():
                util.startLoop()
                self.ib.connect("127.0.0.1", value_port, clientId=value_client_id)
            else:
                self.ib.disconnect()
            self.update_button_status()
        except Exception as e:
            self.trading_manager_utils.display_message(self.system_message, f"⚠️ Connection attempt failed: {str(e)}", color="yellow")

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

    def update_button_status(self):
        ### Updates the button text and color based on connection status.
        if self.ib.isConnected():
            self.connect_reconnect_button.configure(text="Connected", fg_color="green")
        else:
            self.connect_reconnect_button.configure(text="Disconnected", fg_color="red")
        # Re-check status every 1 second
        self.root.after(1000, self.update_button_status)

    def is_connected(self):
        return self.ib.isConnected()

    def prompt_num_columns(self):
        input_dialog = customtkinter.CTkInputDialog(
            text="Enter the number of columns for the grid layout:",
            title="Grid Columns"
        )
        num_columns = input_dialog.get_input()
        if num_columns is None or not num_columns.isdigit() or int(num_columns) < 1:
            raise ValueError("Invalid number of columns entered.")
        return int(num_columns)

    def get_account_summary(self): # Missing to include
        # Example: fetch account summary
        account_values = self.ib.accountValues()
        return util.df(account_values)

    def show_open_orders(self, master=None):
        # Create a new window or frame for the table
        orders = customtkinter.CTkToplevel(master or self.root)
        orders.title("Open Orders")
        orders.geometry("1100x400")
        orders.lift()
        orders.attributes('-topmost', True)
        orders.after(100, lambda: orders.attributes('-topmost', False))
        orders.grab_set()

        scroll_frame = customtkinter.CTkScrollableFrame(orders, width=1050, height=320)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh_table():
            for widget in scroll_frame.winfo_children():
                widget.destroy()
            df = self.fetch_open_orders_df(self.ib)
            if df.empty:
                customtkinter.CTkLabel(scroll_frame, text="No open orders found.", text_color="yellow").grid(row=0, column=0)
                return
            if "symbol" in df.columns:
                df = df.sort_values("symbol")
            for j, col in enumerate(df.columns):
                customtkinter.CTkLabel(scroll_frame, text=col, font=("Arial", 12, "bold")).grid(row=0, column=j, padx=2, pady=2)
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    customtkinter.CTkLabel(scroll_frame, text=str(value), font=("Arial", 11)).grid(row=i+1, column=j, padx=2, pady=2)

        refresh_btn = customtkinter.CTkButton(orders, text="Refresh", command=refresh_table, fg_color="blue")
        refresh_btn.pack(pady=5)

        refresh_table()

    def fetch_open_orders_df(self, ib):
        accounts = ib.managedAccounts()
        today = datetime.now().strftime('%Y-%m-%d')
        open_orders = ib.reqAllOpenOrders()
        order_records = []
        for account_id in accounts:
            for order in open_orders:
                order_obj = order.order
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
        return pd.DataFrame(order_records)

    def load_excel_files(self):
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

                self.get_ib_information(sheets_file_update, file_xml, gp_df, save_path, default_filename)

            except Exception as e:
                display_message(system_message, f"Error reading file or missing required sheets: {e}", color="red")
                return
            
    def get_ib_information(self, sheets_file_update, file_xml, gp_df, save_path, default_filename):
        if not self.ib.isConnected():
            display_message(self.system_message, "⚠️ Not connected to IB. Please connect first.", color="red")
            return
        
        account_ids = self.ib.managedAccounts()

        # -----------------------------------------
        # ✅ 1. Fetch Account Information Summary #
        # -----------------------------------------
        # Use delayed market data
        self.ib.reqMarketDataType(3)

        # Fetch all account values once
        account_values = self.ib.accountValues()
        account_df = util.df(account_values)

        # Prepare list to hold per-account results
        all_account_data = []

        # Loop through each account
        for account_id in account_ids:
            def get_summary_value(tag):
                row = account_df.loc[(account_df['tag'] == tag) & (account_df['account'] == account_id)]
                return row['value'].values[0] if not row.empty else None

            # Manually calculate Unrealized PnL for this account
            positions = self.ib.positions()
            unrealized_total = 0.0

            for pos in positions:
                if pos.account != account_id:
                    continue

                contract = pos.contract
                avg_cost = pos.avgCost
                quantity = pos.position

                self.ib.qualifyContracts(contract)
                ticker = ib.reqMktData(contract, snapshot=True)
                self.ib.sleep(1.5)  # Avoid pacing violations

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
        self.ib.reqMarketDataType(3)

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
                self.ib.qualifyContracts(contract)
                ticker = self.ib.reqMktData(contract, snapshot=True)
                self.ib.sleep(1.0)  # Respect pacing limits

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
        open_orders = self.ib.reqAllOpenOrders()

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

        # --------------------------------------
        # ✅ 5. Saving as excell file
        # --------------------------------------
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            concat_summary_df.to_excel(writer, sheet_name='Summary', index=False)
            concat_orders_full.to_excel(writer, sheet_name='Stock Activity', index=False)
            concat_orders.to_excel(writer, sheet_name='Active Orders', index=False)
            concat_position.to_excel(writer, sheet_name='Positions', index=False)

        display_message(self.system_message, f"File {default_filename} Successfully saved!", color="green")

    def set_order(self, action: str, quantity: int, order_type: str, price: float, tif: str, account: str, transmit:bool, parentId: int = 0):
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

    def get_parent_child_event(self, symbol, parent_order, child_order, stp_flag):
        if stp_flag:
            # Only send the parent order, do not send the child order
            stock = Stock(symbol=symbol, exchange='SMART', currency='USD')
            self.ib.qualifyContracts(stock)

            parent_trade = self.ib.placeOrder(stock, parent_order)
            self.ib.sleep(1)  # Wait for the order to be processed
            position = parent_order.totalQuantity
            return symbol, parent_trade.order.orderId, None, position
        else:
            # Select the contract based on the symbol
            stock = Stock(symbol=symbol, exchange='SMART', currency='USD')
            self.ib.qualifyContracts(stock)

            parent_trade = self.ib.placeOrder(stock, parent_order)
            self.ib.sleep(1)  # Wait for the order to be processed
            parent_id = parent_trade.order.orderId
            child_order.parentId = parent_id
            # Set OCA group so one cancels the other
            oca_group = f"OCA_{symbol}_{parent_id}"
            parent_order.ocaGroup = oca_group
            child_order.ocaGroup = oca_group
            parent_order.ocaType = 1  # CANCEL_WITH_BLOCK
            child_order.ocaType = 1
            # Place the SELL order
            child_trade = self.ib.placeOrder(stock, child_order)

            # Get position (quantity) from parent or child order
            position = parent_order.totalQuantity  # or child_order.totalQuantity

            return symbol, parent_trade.order.orderId, child_trade.order.orderId, position

    def stp_order(self, col: int):
        
        ######################
        #   1. Get values    #
        ######################
        values = self.get_values(col)
        
        #######################
        # 2. Input validation #
        #######################

        valid, order, flag_fields_ok, missing_fileds = self.trading_manager_utils.validate_info_stp_button(values)
        
        if not valid:
            self.trading_manager_utils.display_message(self.system_message, f"⚠️ {order}", color="red")
            return
            
        if not flag_fields_ok:
            self.trading_manager_utils.display_message(self.system_message, f"⚠️ Missing: {', '.join(missing_fileds)}. Please fill in all fields.", color="red")
            return
        
        def cancel():
            self.trading_manager_utils.display_message(self.system_message, "Operation cancelled by user", color="yellow")
        
        def proceed():

            #types_dict = {k: type(v) if v is not None else None for k, v in values.items()}
            #print(f"Values in column {types_dict}")

            starting_message = f"Submitting a {order}..."
            self.show_order_wait(starting_message)
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
                    parent_order = self.set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = True)
                    child_order = None
                else:
                    parent_order = self.set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = False)
                    child_order = self.set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = stop, tif = 'GTC', account = values['account'], transmit = True)
            else:
                # buy order is the parent, sell order is the child
                if values['not_stp_loss']:
                    parent_order = self.set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = True)
                    child_order = None
                else:
                    parent_order = self.set_order(action = 'BUY', quantity = quantity, order_type = 'STP', price = entry, tif = 'GTC', account = values['account'], transmit = False)
                    child_order = self.set_order(action = 'SELL', quantity = quantity, order_type = 'STP', price = stop, tif = 'GTC', account = values['account'], transmit = True)

            ######################
            #   3. Send order    #
            ######################

            # Show waiting message
            message = "Waiting for order to be registered..."
            self.show_order_wait(message)
            sleep(3)
            # Send the parent and child orders
            stp_flag = values['not_stp_loss']
            if values['not_stp_loss']:
                name, parent_order_id, child_order_id, position = self.get_parent_child_event(symbol = values['symbol'], parent_order = parent_order, child_order = child_order, stp_flag = stp_flag)
                # Show order transmission result message
                self.trading_manager_utils.display_message(self.system_message, f"Symbol: {name}, BUY order ID: {parent_order_id} / SELL order ID: {child_order_id}, position: {position}", color="green")
            else:
                name, parent_order_id, child_order_id, position = self.get_parent_child_event(symbol = values['symbol'], parent_order = parent_order, child_order = child_order, stp_flag = stp_flag)
                # Show order transmission result message
                self.trading_manager_utils.display_message(self.system_message, f"Symbol: {name}, BUY order ID: {parent_order_id} / SELL order ID: {child_order_id}, position: {position}", color="green")
            
                
        mes = "Are you sure you want to submit this order?\n"
        if (order == "Risk-based Buy/Sell order") | (order == "Risk-based Sell/Buy order"):
            order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nRisk USD: {values['risk_USD']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
        elif(order == "Position-based Buy/Sell order") | (order == "Position-based Sell/Buy order"):
            order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nStop: {values['stop']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
        elif(order == "Position-based Buy order") | (order == "Position-based Sell order"):
            order_summary = f"\nOrder Summary:\n------------------------------------------------------------------------------\nOrder type: STP --> ({order})\nSymbol: {values['symbol']}\nEntry: {values['entry']}\nPosition: {values['position']}\nPosition-based: {values['position_based']}\nNot include stop loss: {values['not_stp_loss']}\nShort position: {values['short_pos']}\nAccount: {values['account']}"
        
        self.confirm_operation(mes + order_summary, on_yes = proceed, on_no = cancel)

    def lmt_order(self, col: int):
        
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

    def modify_order(self, col: int):
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

    def cancel_order(self, col: int):
        
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

    def mkt_order(self, col: int):
        pass

    def confirm_operation(self, message: str, on_yes, on_no = None):
        """
        Displays a confirmation dialog with the given message.
        Calls on_yes if the user confirms, and on_no if the user cancels.
        """
        confirm_win = customtkinter.CTkToplevel(self.root)
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
    
    def show_order_wait(self, message):
        display_message(self.system_message, message, color="yellow")

    def get_values(self, col: int) -> Dict[str, Any]:

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
            "account": self.dropdown_var.get(),
            "order_id": orderid_entries[col].get()
        }
        return results_dict