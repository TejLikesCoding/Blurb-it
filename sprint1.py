
import cv2  #OpenCV library for webcam access
import tkinter as tk  #tkinter library for the graphical user interface
from tkinter import messagebox  #messagebox module for displaying error messages
from pyzbar.pyzbar import decode  #decode function from pyzbar for reading barcodes
from PIL import Image, ImageTk  #PIL for image processing

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blurb-it")  #title of the GUI window
        self.root.geometry("1800x1000")  #initial window size
        self.barcode_data = None  #variable to store barcode data

        #canvas for displaying webcam feed
        self.canvas = tk.Canvas(root, width=1280, height=720)
        self.canvas.pack()

        # Open the webcam and check if it's available
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Unable to access the webcam. Make sure it's connected.")
            self.root.destroy()
        else:
            self.capture_frame()

        #label for displaying barcode data
        self.result_label = tk.Label(root, text="", font=("Helvetica", 20))
        self.result_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=20)

        #button for handling loved books
        self.lovedbooks_button = tk.Button(root, text="Loved books", command=self.handle_menu)
        self.lovedbooks_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-100, y=10)

        #label for displaying the instruction prompt
        self.instruction_label = tk.Label(root, text="Please display ISBN barcode of book", font=("Helvetica", 16))
        self.instruction_label.pack(side=tk.TOP, pady=(5, 20))


        #"Back" button initially hidden
        self.back_button = tk.Button(root, text="Back", command=self.reset_app)
        self.back_button.pack(side=tk.BOTTOM, anchor=tk.SW, padx=20, pady=20)
        self.back_button.pack_forget()

        #menu for loved book button
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="No loved books", command=self.set_option)

    def capture_frame(self):
        ret, frame = self.cap.read()  #Capture a frame from the webcam

        if self.barcode_data is None:
            if ret:
                barcodes = decode(frame)  #Decode barcodes in the frame
                if barcodes:
                    self.barcode_data = barcodes[0].data.decode("utf-8")  #Store barcode data

        if self.barcode_data:
            self.output_page()  #Display the output page if barcode data is available
        else:
            if ret:
                #Display the webcam feed on the canvas
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (1280, 720))
                img = Image.fromarray(img)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.imgtk = imgtk
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.update()
                self.root.after(10, self.capture_frame)
            else:
                self.root.quit()  #Quit the application if the webcam not available

    def handle_menu(self): #allows for the clickable menu to be right below the button
        self.menu.post(self.lovedbooks_button.winfo_rootx(), 
                       self.lovedbooks_button.winfo_rooty() + 
                       self.lovedbooks_button.winfo_height())

    def set_option(self):
        self.menu.unpost()  #temporary placeholder future callback function for click

    def output_page(self):
        #Close webcam, destroy canvas, hide menu, show "Back" button, and display the barcode data
        self.cap.release()
        cv2.destroyAllWindows()
        self.canvas.destroy()
        self.lovedbooks_button.place_forget()
        self.instruction_label.pack_forget()
        #align the "Back" button to the bottom left corner
        self.back_button.pack(side=tk.BOTTOM, anchor=tk.SW, padx=20, pady=20)

        self.result_label.config(text=f"ISBN Data:\n{self.barcode_data}", font=("Helvetica", 20))
        self.result_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=20)


    def reset_app(self):
        #Hide the "Back" button, reset barcode data and result label, recreate the canvas, and restart webcam feed
        self.back_button.pack_forget()
        self.barcode_data = None
        self.result_label.config(text="")
        self.result_label.pack_forget()
        self.canvas = tk.Canvas(self.root, width=1280, height=720)
        self.canvas.pack()
        self.instruction_label.pack(side=tk.TOP, pady=(5, 20))
        self.lovedbooks_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-100, y=10)
        self.lovedbooks_button.lift()   
        self.cap = cv2.VideoCapture(0)
        self.capture_frame()
        
        


root = tk.Tk()  #Create the main application window
app = GUI(root)  #Initialize the GUI application
root.mainloop()  #Start the main event loop for the GUI


#commenting is decent in this sprint but if i were to do it again
# i would reference features of my imports and documentation and be more specific line by line rather than block by block