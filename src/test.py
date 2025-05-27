import customtkinter
from ib_insync import *
ib = IB() # Define ib globally
from table_Initializer import *

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
root =  customtkinter.CTk()
root.geometry("500x800")

# System message label
system_message = customtkinter.CTkLabel(master=root, text="", text_color="white", wraplength=450)
system_message.pack(pady=10)

frame = create_frame_with_pack(root)

################################################################

label1 = create_label_with_pack(frame,"My Test")
label2 = create_label_with_pack(frame,"My Test2", column=1)
label3 = create_label_with_pack(frame,"My Test3", column=2)

entry1 = create_entry_with_pack(frame,"Eduardo",row=1)
entry2 = create_entry_with_pack(frame,"Avril",row=1, column=1)
entry3 = create_entry_with_pack(frame,"Daniela",row=1, column=2)

button1 = create_button_with_pack(frame,"B1", "dummy",row=2)
button2 = create_button_with_pack(frame,"B2", "dummy2",row=2, column=1)
button3 = create_button_with_pack(frame,"B3", "dummy3",row=2, column=2)

label1 = create_label_with_pack(frame,"",row=3, column=0)
label2 = create_label_with_pack(frame,"",row=3, column=1)
label3 = create_label_with_pack(frame,"", row=3, column=2)

entry1 = create_entry_with_pack(frame,"Limit Price",row=4)
entry2 = create_entry_with_pack(frame,"Limit Price",row=4, column=1)
entry3 = create_entry_with_pack(frame,"Limit Price",row=4, column=2)

###############################################################
#### Create corner buttons ####

button_frame = customtkinter.CTkFrame(master=root, fg_color="transparent")
button_frame.place(relx=1, rely=0, anchor="ne")  # Places in the top-right corner

#########################
# Connection Parameters #
#########################
port = customtkinter.CTkEntry(master = button_frame, placeholder_text = "Conn Port")
port.pack(side="right")
client_id = customtkinter.CTkEntry(master = button_frame, placeholder_text = "Client ID")
client_id.pack(side="right")

#################
# Small Buttons #
#################
#connect_reconnect_button = customtkinter.CTkButton(master=button_frame, text="Disconnected", width=80, height=30, 
#                                                   fg_color="red", command=connect_ib)
#connect_reconnect_button.pack(side="left")

# Start main program
root.mainloop()