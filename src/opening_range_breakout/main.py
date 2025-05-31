import customtkinter
from ib_insync import *
ib = IB() # Define ib globally
from utilities import *

#### Live Account client_id = 1, port_number = 4001
#### Paper Account client_id = 1, port_number = 4002

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