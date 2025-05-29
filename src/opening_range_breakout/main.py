import customtkinter
from ib_insync import *
ib = IB() # Define ib globally
from utilities import *

#### Live Account client_id = 1, port_number = 4001
#### Paper Account client_id = 1, port_number = 4002

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


#############################################################
######### Frame for buttons in the top-right corner #########
#############################################################

button_frame = create_frame_relative_position(master = root, relx = 1, rely = 0)


########################################################################
######### Create buttons and entries in the connectivity frame #########
########################################################################

dropdown_var = customtkinter.StringVar(value="Select account")
accounts_menu = create_dropdown_relative_position(master=button_frame, variable=dropdown_var, values=accounts)
port = create_entry_relative_position(master=button_frame, placeholder_text="Conn Port", side="right")
client_id = create_entry_relative_position(master=button_frame, placeholder_text="Client ID", side="right")
connect_reconnect_button = create_button_relative_position(master=button_frame, text="Disconnected", command=connect_ib, side="left")


# Start main program

if __name__ == "__main__":
    # Prompt user for number of columns before launching main window
    input_dialog = customtkinter.CTkInputDialog(text="Enter the number of columns for the grid layout:", title="Grid Columns")
    num_columns = input_dialog.get_input()
    if num_columns is None or not num_columns.isdigit() or int(num_columns) < 1:
        raise ValueError("Invalid number of columns entered.")
    num_columns = int(num_columns)
    draw_widgets(num_columns, frame)
    root.mainloop()