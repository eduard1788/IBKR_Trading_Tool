from ib_insync import IB, util
from datetime import datetime
import pandas as pd

class IBKRClientAPI:
    def __init__(self):
        self.ib = IB()

    def connect(self, host='127.0.0.1', port=4002, client_id=1):
        if not self.ib.isConnected():
            util.startLoop()
            self.ib.connect(host, port, clientId=client_id)
        return self.ib.isConnected()

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()

    def is_connected(self):
        return self.ib.isConnected()

    def get_account_summary(self):
        # Example: fetch account summary
        account_values = self.ib.accountValues()
        return util.df(account_values)

    # Add more methods for positions, orders, etc.
