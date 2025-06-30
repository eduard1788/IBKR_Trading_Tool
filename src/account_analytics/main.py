import pandas as pd
from ib_insync import *
from datetime import datetime
import requests
from io import StringIO
import xml.etree.ElementTree as ET
import os
util.startLoop()


# ------------------------------------- #
# 0. Connect to Interactive Brokers API #
# ------------------------------------- #

ib = IB()
ib.connect('127.0.0.1', 4001, clientId=1)

# Store all account IDs
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
account_df_export = pd.DataFrame(all_account_data)


# ----------------------------------------
# ✅ 2. Fetch Trades (Stock Activities) #
# ----------------------------------------

# 1. Load and parse the XML
tree = ET.parse('eduardo_my_trade_report_historical.xml')
root = tree.getroot()

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

# assume df is your parsed DataFrame
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

# 5. Aggregate fills per orderID + symbol
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

# 6. Merge with orders
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

# 7. (Optional) Combine with summary for a top-level view
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

# 8. Print or export
print("=== Orders with Fill Summary ===")
print(orders_full.to_string(index=False))

print("\n=== Top-Level Symbol Summary ===")
print(symbol_totals.to_string(index=False))


# -----------------------------
# ✅ 3. Fetch Open Positions #
# -----------------------------
# Get the list of managed accounts
account_ids = ib.managedAccounts()

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


# ----------------------------
# ✅ 4. Fetch Active Orders #
# ----------------------------
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