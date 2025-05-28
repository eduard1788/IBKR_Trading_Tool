""" 
1. Create a Table Widget
customtkinter does not have a built-in table widget, but you can use a CTkFrame with a grid of CTkLabel widgets to 
simulate a table, or use tkinter.ttk.Treeview for a more standard table.

2. Fetch Active Orders and Trades
With ib_insync, you can get:

Active orders: ib.openOrders()
Active trades: ib.trades()
3. Populate the Table
You can periodically update the table by fetching the latest orders/trades and updating the table rows.
"""

import tkinter.ttk as ttk

# Create the Table in Your Main Frame:
# Add this after your main frame is created
order_table = ttk.Treeview(frame, columns=("OrderId", "Symbol", "Action", "Quantity", "Status"), show="headings")
for col in ("OrderId", "Symbol", "Action", "Quantity", "Status"):
    order_table.heading(col, text=col)
order_table.grid(row=12, column=0, columnspan=2, sticky="nsew")

# Create the Table in Your Main Frame:
def update_order_table():
    # Clear existing rows
    for row in order_table.get_children():
        order_table.delete(row)
    # Fetch active orders
    for order in ib.openOrders():
        contract = order.contract
        order_table.insert("", "end", values=(
            order.orderId,
            getattr(contract, "symbol", ""),
            order.action,
            order.totalQuantity,
            order.status
        ))
    # Schedule next update
    root.after(2000, update_order_table)  # Update every 2 seconds

# Start the Table Update Loop:
    update_order_table()

# Repeat for Trades: create a similar table for trades using ib.trades().

"""
Better create a function that calls information about orders and trades, and then loads them into a DataFrame

"""
