""" Common functions and variables for the Opening Range Breakout strategy.

"""
basic_order = ['symbol', 'entry']
risk_based = ['symbol', 'risk_USD', 'entry', 'stop']
position_based = ['symbol', 'position', 'entry', 'stop']
not_stp_loss = ['symbol', 'position', 'entry']
mod_price_and_pos = ['entry','position','order_id','account']
mod_only_price = ['entry','order_id','account']
mod_only_pos = ['position','order_id','account']
cancel_order = ['order_id', 'account']

def validate_info_stp_button(result_dict: dict):
    if (not result_dict['symbol']) | (not result_dict['entry']):
        valid = True
        order = "Please select a symbol and entry price."
        flag_fields_ok, missing_fileds = validate_order_fields(basic_order, result_dict)
        return valid, order, flag_fields_ok, missing_fileds

    if (not result_dict['position_based']) & (not result_dict['not_stp_loss']) & (not result_dict['short_pos']):
        valid = True
        order = "Risk-based Buy/Sell order"
        flag_fields_ok, missing_fileds = validate_order_fields(risk_based, result_dict)

    if (result_dict['position_based']) & (not result_dict['not_stp_loss']) & (not result_dict['short_pos']):
        valid = True
        order = "Position-based Buy/Sell order"
        flag_fields_ok, missing_fileds = validate_order_fields(position_based, result_dict)

    if (not result_dict['position_based']) & (not result_dict['not_stp_loss']) & (result_dict['short_pos']):
        valid = True
        order = "Risk-based Sell/Buy order"
        flag_fields_ok, missing_fileds = validate_order_fields(risk_based, result_dict)

    if (result_dict['position_based']) & (not result_dict['not_stp_loss']) & (result_dict['short_pos']):
        valid = True
        order = "Position-based Sell/Buy order"
        flag_fields_ok, missing_fileds = validate_order_fields(position_based, result_dict)
        
    if (result_dict['position_based']) & (result_dict['not_stp_loss']) & (not result_dict['short_pos']):
        valid = True
        order = "Position-based Buy order"
        flag_fields_ok, missing_fileds = validate_order_fields(not_stp_loss, result_dict)

    if (result_dict['position_based']) & (result_dict['not_stp_loss']) & (result_dict['short_pos']):
        valid = True
        order = "Position-based Sell order"
        flag_fields_ok, missing_fileds = validate_order_fields(not_stp_loss, result_dict)

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

def validate_info_mod_button(result_dict: dict):
    if (result_dict['entry']) and (result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
        valid = True
        order = "Modify order with new price and position size"
        flag_fields_ok, missing_fileds = validate_order_fields(mod_price_and_pos, result_dict)
    
    elif (result_dict['entry']) and (not result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
        valid = True
        order = "Modify order with new price"
        flag_fields_ok, missing_fileds = validate_order_fields(mod_only_price, result_dict)
    
    elif (not result_dict['entry']) and (result_dict['position']) and (result_dict['order_id']) and (result_dict['account']):
        valid = True
        order = "Modify order with new position size"
        flag_fields_ok, missing_fileds = validate_order_fields(mod_only_pos, result_dict)

    else:
        valid = False
        order = "Please provide an entry price and/or position size, and order ID to modify the order."
        flag_fields_ok = None
        missing_fileds = None

    return valid, order, flag_fields_ok, missing_fileds

def validate_info_cancel_button(result_dict: dict):
    if (result_dict['order_id']) and (result_dict['account']):
        valid = True
        order = f"Cancel order: {result_dict['order_id']} for account: {result_dict['account']}"
        flag_fields_ok, missing_fileds = validate_order_fields(cancel_order, result_dict)

    else:
        valid = False
        order = "Please provide an order and account ID to cancel an order."
        flag_fields_ok = None
        missing_fileds = None

    return valid, order, flag_fields_ok, missing_fileds

def validate_order_fields(fields_to_check, result_dict: dict):
        missing_fields = []
        for field in fields_to_check:
            value = result_dict.get(field)
            if value is None or value == "" or (isinstance(value, bool) and not value):
                # You can customize the display name if needed
                missing_fields.append(field.replace('_', ' ').title())
        if missing_fields:
            return False, missing_fields
        return True, None
