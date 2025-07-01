""" Common functions and variables for the Opening Range Breakout strategy.

"""
basic_order = ['symbol', 'entry']
risk_based = ['symbol', 'risk_USD', 'entry', 'stop']
position_based = ['symbol', 'position', 'entry', 'stop']
not_stp_loss = ['symbol', 'position', 'entry']

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
