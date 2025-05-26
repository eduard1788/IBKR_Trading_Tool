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


frame = customtkinter.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

################################################################

label1 = create_label(frame,"My Test")
label2 = create_label(frame,"My Test2", column=1)
label3 = create_label(frame,"My Test3", column=2)

entry1 = create_entry(frame,"Eduardo",row=1)
entry2 = create_entry(frame,"Avril",row=1, column=1)
entry3 = create_entry(frame,"Daniela",row=1, column=2)

button1 = create_button(frame,"B1", "dummy",row=2)
button2 = create_button(frame,"B2", "dummy2",row=2, column=1)
button3 = create_button(frame,"B3", "dummy3",row=2, column=2)

label1 = create_label(frame,"",row=3, column=0)
label2 = create_label(frame,"",row=3, column=1)
label3 = create_label(frame,"", row=3, column=2)

entry1 = create_entry(frame,"Limit Price",row=4)
entry2 = create_entry(frame,"Limit Price",row=4, column=1)
entry3 = create_entry(frame,"Limit Price",row=4, column=2)

###############################################################

# Start main program
root.mainloop()