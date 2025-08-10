# General utility functions for the trading manager module
import customtkinter
from tkinter import filedialog
from typing import Union, List, Dict, Any
from .constants import *
from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as ET

class TradingManagerUtils:

    def __init__(self):
        self.basic_order : list = ['symbol', 'entry']
        self.risk_based : list = ['symbol', 'risk_USD', 'entry', 'stop']
        self.position_based : list = ['symbol', 'position', 'entry', 'stop']
        self.not_stp_loss : list = ['symbol', 'position', 'entry']
        self.mod_price_and_pos : list = ['entry','position','order_id','account']
        self.mod_only_price : list = ['entry','order_id','account']
        self.mod_only_pos : list = ['position','order_id','account']
        self.cancel_order : list = ['order_id', 'account']

        pass

    def display_message(self, frame: customtkinter.CTkLabel, msg: Union[str, List[str]], color: str = "white"):
        frame.configure(text=msg, text_color=color)

    def validate_info_stp_button(self, result_dict: dict):
        if (not result_dict['symbol']) | (not result_dict['entry']):
            valid = True
            order = "Please select a symbol and entry price."
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.basic_order, result_dict)
            return valid, order, flag_fields_ok, missing_fileds

        if (not result_dict['position_based']) & (not result_dict['not_stp_loss']) & (not result_dict['short_pos']):
            valid = True
            order = "Risk-based Buy/Sell order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.risk_based, result_dict)

        if (result_dict['position_based']) & (not result_dict['not_stp_loss']) & (not result_dict['short_pos']):
            valid = True
            order = "Position-based Buy/Sell order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.position_based, result_dict)

        if (not result_dict['position_based']) & (not result_dict['not_stp_loss']) & (result_dict['short_pos']):
            valid = True
            order = "Risk-based Sell/Buy order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.risk_based, result_dict)

        if (result_dict['position_based']) & (not result_dict['not_stp_loss']) & (result_dict['short_pos']):
            valid = True
            order = "Position-based Sell/Buy order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.position_based, result_dict)
            
        if (result_dict['position_based']) & (result_dict['not_stp_loss']) & (not result_dict['short_pos']):
            valid = True
            order = "Position-based Buy order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.not_stp_loss, result_dict)

        if (result_dict['position_based']) & (result_dict['not_stp_loss']) & (result_dict['short_pos']):
            valid = True
            order = "Position-based Sell order"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.not_stp_loss, result_dict)

        if (not result_dict['position_based']) & (result_dict['not_stp_loss']) & (result_dict['short_pos']):
            valid = False
            order = "If you do not include a stop loss, you must select a position size."
            flag_fields_ok = None
            missing_fileds = None

        if (not result_dict['position_based']) & (result_dict['not_stp_loss']) & (not result_dict['short_pos']):
            valid = False
            order = "If you do not include a stop loss, you must select a position size."
            flag_fields_ok = None
            missing_fileds = None

        return valid, order, flag_fields_ok, missing_fileds

    def validate_info_mod_button(self, result_dict: dict):
        if (result_dict['entry']) and (result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
            valid = True
            order = "Modify order with new price and position size"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.mod_price_and_pos, result_dict)
        
        elif (result_dict['entry']) and (not result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
            valid = True
            order = "Modify order with new price"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.mod_only_price, result_dict)
        
        elif (not result_dict['entry']) and (result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
            valid = True
            order = "Modify order with new position size"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.mod_only_pos, result_dict)

        else:
            valid = False
            order = "Please provide an entry price and/or position size, and order ID to modify the order."
            flag_fields_ok = None
            missing_fileds = None

        return valid, order, flag_fields_ok, missing_fileds

    def validate_info_cancel_button(self, result_dict: dict):
        if (result_dict['order_id']) and (result_dict['account']):
            valid = True
            order = f"Cancel order: {result_dict['order_id']} for account: {result_dict['account']}"
            flag_fields_ok, missing_fileds = self.validate_order_fields(self.cancel_order, result_dict)

        else:
            valid = False
            order = "Please provide an order and account ID to cancel an order."
            flag_fields_ok = None
            missing_fileds = None

        return valid, order, flag_fields_ok, missing_fileds

    def validate_order_fields(self, fields_to_check, result_dict: dict):
            missing_fields = []
            for field in fields_to_check:
                value = result_dict.get(field)
                if value is None or value == "" or (isinstance(value, bool) and not value):
                    # You can customize the display name if needed
                    missing_fields.append(field.replace('_', ' ').title())
            if missing_fields:
                return False, missing_fields
            return True, None