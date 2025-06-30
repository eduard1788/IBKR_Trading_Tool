""" Common functions and variables for the Opening Range Breakout strategy.

"""

def validate_values_stp_button(result_dict: dict):
    if (not result_dict['symbol']) | (not result_dict['entry']):
        print("Please select a symbol and entry price.")






