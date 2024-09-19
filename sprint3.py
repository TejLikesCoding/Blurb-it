import cv2  #OpenCV library for webcam access
import tkinter as tk  #tkinter library for the graphical user interface
from tkinter import messagebox  #messagebox module for displaying error messages
from pyzbar.pyzbar import decode  #decode function from pyzbar for reading barcodes
from PIL import Image, ImageTk  #PIL for image processing
import sqlite3


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

        self.db = Database('Y13/Booktest.db')

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
        
                # Button to "love" a book
        self.love_book_button = tk.Button(root, text="Love book", command=self.toggle_love_book)
        self.love_book_button.place(relx=1.0, rely=0.0, anchor = tk.NE, x = -10, y=10)
        #self.love_book_button.pack(side=tk.TOP, anchor=tk.NE, padx=20, pady=20)
        self.love_book_button.place_forget()  # Initially hidden


        

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

    
    def toggle_love_book(self):
        if self.barcode_data:
            self.db.like_book(self.barcode_data)
          
            # Check if the book is now loved or not
            book_data = self.db.get_book_data(self.barcode_data)
            if book_data:
                _, _, _, _, _, _, _, _, _, _, _, loved = book_data
                if loved == "true":
                    self.love_book_button.config(text="Unlove Book", bg="red")
                else:
                    self.love_book_button.config(text="Love Book", bg="green")

    def calculate_reading_time(self, total_pages, average_time_per_page= 1.7):#average reading time is 1.7 minutes
   
        reading_time = round(total_pages * average_time_per_page)


        hours = reading_time // 60
        minutes = reading_time % 60

        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"




    def output_page(self):
        #Close webcam, destroy canvas, hide menu, show "Back" button, and display the barcode data
        self.cap.release()
        cv2.destroyAllWindows()
        self.canvas.destroy()
        self.lovedbooks_button.place_forget()
        self.instruction_label.pack_forget()
        #align the "Back" button to the bottom left corner
        self.back_button.pack(side=tk.BOTTOM, anchor=tk.SW, padx=20, pady=20)


        #fetch book data from DB by using ISBN
        book_data = self.db.get_book_data(self.barcode_data)

        if book_data:

            #show the "Love Book" button
            self.love_book_button.place(relx=1.0, rely=0.0, anchor = tk.NE, x = -10, y=10)

            #unpack book data 
            isbn, name, author, genre, rating, summary, good_review1, good_review2, bad_review1, bad_review2, pages, loved = book_data

             #display book name
            self.name_label = tk.Label(self.root, text=name, font=("Helvetica", 24))
            self.name_label.pack(side=tk.TOP, anchor=tk.NW, padx= 20, pady=(20, 0))

            #display author
            self.author_label = tk.Label(self.root, text=f"Author: {author}", font=("Helvetica", 18))
            self.author_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=(5, 0))



            # Round the rating to the nearest whole number and generate star emojis
            if rating>5:
                rating = 5
            rounded_rating = round(rating)
            star_emoji = "\U00002B50"  # Unicode for star emoji
            stars_display = star_emoji * rounded_rating

            # Display rating with star emojis
            self.rating_label = tk.Label(self.root, text=f"Rating:{stars_display}", font=("Helvetica", 18))
            self.rating_label.pack(side=tk.TOP, anchor=tk.NE, padx=20, pady=(5, 0))
            


            # Calculate and display reading time
            reading_time_text = self.calculate_reading_time(pages)
            self.pages_label = tk.Label(self.root, text=f"Reading Time: {reading_time_text}", font=("Helvetica", 16))
            self.pages_label.pack(side=tk.TOP, anchor=tk.NE, padx=20, pady=(30, 0))

            '''
            #display pages
            self.pages_label = tk.Label(self.root, text=f"Pages: {pages}", font=("Helvetica", 16))
            self.pages_label.pack(side=tk.TOP, anchor=tk.NE, padx=20, pady=(30, 0))
            '''


            # Dropdown for Summary
            self.summary_button = tk.Button(self.root, text="Summary", command=self.show_summary)
            self.summary_button.pack(side=tk.TOP,anchor = tk.W, padx=20, pady=(10, 0))

            # Dropdown for Reviews
            self.reviews_var = tk.StringVar(value = "Reviews", name = "Reviews")
            self.reviews_menu = tk.OptionMenu(self.root, self.reviews_var, "Review 1", "Review 2", "Review 3", "Review 4", command=self.show_review)
            self.reviews_menu.pack(side=tk.LEFT,anchor = tk.W, padx=20, pady=(10, 0))

            # Initialize labels for summary and reviews, but do not pack them yet
            self.summary_label = tk.Label(self.root, text="", font=("Helvetica", 16))
            self.review_label = tk.Label(self.root, text="", font=("Helvetica", 16))

            # Store book data in instance variables for later use
            self.book_summary = summary
            self.book_reviews = {'Review 1': good_review1, 'Review 2': good_review2, 'Review 3': bad_review1, 'Review 4': bad_review2}
           
            #display genre at the bottom
            self.genre_label = tk.Label(self.root, text=f"Genre: {genre}", font=("Helvetica", 16))
            self.genre_label.pack(side=tk.BOTTOM, padx=20, pady=20)

        else:
            # ISBN not found in the database
            self.book_info_label = tk.Label(self.root, text="Book not found in the database.", font=("Helvetica", 16))
            self.book_info_label.pack(side=tk.TOP, padx=20, pady=20)
        #self.result_label.config(text=f"ISBN Data:\n{self.barcode_data}", font=("Helvetica", 20))
        #self.result_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=20)



    
    
    def show_summary(self):
        # Assuming self.summary_button.y is the y-coordinate of the Summary button
        summary_button_y = self.summary_button.winfo_y()
        summary_button_height = self.summary_button.winfo_height()
        self.summary_label.config(text=self.book_summary)
        # Place the summary output below the summary button
        self.summary_label.place(x=20, y=summary_button_y + summary_button_height + 10, width=200, anchor='nw')

    def show_review(self, select):
        # Assuming self.reviews_menu.y is the y-coordinate of the Reviews dropdown
        reviews_menu_y = self.reviews_menu.winfo_y()
        reviews_menu_height = self.reviews_menu.winfo_height()
        selected_review = self.book_reviews.get(select, "")
        self.review_label.config(text=selected_review)
        # Place the review output below the reviews dropdown
        self.review_label.place(x=20, y=reviews_menu_y + reviews_menu_height + 10, width=200, anchor='nw')

    '''
    def show_summary(self):
        self.summary_label.config(text=self.book_summary, font=("Helvetica", 14))
        self.summary_label.pack(side=tk.LEFT, anchor=tk.NW, padx=20, pady=(5, 0))

    def show_review(self, select):
        selected_review = self.book_reviews.get(select, "")
        self.review_label.config(text=selected_review, font=("Helvetica", 14))
        self.review_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=20, pady=(5, 0))

    '''


    def reset_app(self):
        # Hide the "Back" and "Love Book" buttons
        self.back_button.pack_forget()
        self.love_book_button.place_forget()

        #Hide the summary and review labels
        self.summary_label.pack_forget()
        self.review_label.pack_forget()

        # Destroy all widgets created in 'output_page'
        for widget in self.root.pack_slaves():
            widget.pack_forget()
        for widget in self.root.place_slaves():
            widget.place_forget()

        # Reset barcode data and recreate the canvas and webcam feed
        self.barcode_data = None
        self.canvas = tk.Canvas(self.root, width=1280, height=720)
        self.canvas.pack()
        self.instruction_label.pack(side=tk.TOP, pady=(5, 20))
        self.lovedbooks_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-100, y=10)
        self.lovedbooks_button.lift() 

        # Restart webcam feed
        self.cap = cv2.VideoCapture(0)
        self.capture_frame()



    '''

    def reset_app(self):
        #Hide the "Back" button, reset barcode data and result label, recreate the canvas, and restart webcam feed
        self.back_button.pack_forget()
        # Hide the "Love Book" button
        self.love_book_button.place_forget()
        self.book_info_label.destroy()  
        self.barcode_data = None
        self.result_label.config(text="")
        self.result_label.pack_forget()
        self.book_info_label.destroy
        self.canvas = tk.Canvas(self.root, width=1280, height=720)
        self.canvas.pack()
        self.instruction_label.pack(side=tk.TOP, pady=(5, 20))
        self.lovedbooks_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-100, y=10)
        self.lovedbooks_button.lift()   
        self.cap = cv2.VideoCapture(0)
        self.capture_frame()
        
        '''


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def get_book_data(self, isbn):
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM books WHERE ISBN = ?"
        cursor.execute(query, (isbn,))
        data = cursor.fetchone()
        conn.close()
        return data

    def like_book(self, isbn):
        conn = self._connect()
        cursor = conn.cursor()

        # Check current "Loved" status
        query = "SELECT Loved FROM books WHERE ISBN = ?"
        cursor.execute(query, (isbn,))
        current_status = cursor.fetchone()[0]

        # Toggle "Loved" status
        new_status = False if current_status else True
        update_query = "UPDATE books SET Loved = ? WHERE ISBN = ?"
        cursor.execute(update_query, (new_status, isbn))
        conn.commit()
        conn.close()

    def get_loved_books(self):
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT Name FROM books WHERE Loved = True"
        cursor.execute(query)
        books = cursor.fetchall()
        conn.close()
        return [book[0] for book in books]  # Extract book names from tuples
    






        
root = tk.Tk()  #Create the main application window
app = GUI(root)  #Initialize the GUI application
root.mainloop()  #Start the main event loop for the GUI