from datetime import datetime
import pandas as pd

def fetch_open_orders_df(ib):
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