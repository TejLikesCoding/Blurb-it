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
        self.lovedbooks_button = tk.Button(root, text="Loved books", command=self.handle_loved_menu)
        self.lovedbooks_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-100, y=10)

        #label for displaying the instruction prompt
        self.instruction_label = tk.Label(root, text="Please display ISBN barcode of book", font=("Helvetica", 16))
        self.instruction_label.pack(side=tk.TOP, pady=(5, 20))


        #"Back" button initially hidden
        self.back_button = tk.Button(root, text="Back", command=self.reset_app)
        self.back_button.pack(side=tk.BOTTOM, anchor=tk.SW, padx=20, pady=20)
        self.back_button.pack_forget()


        
        #menu for loved book button menu
        self.menu = tk.Menu(root, tearoff=0)
        #self.menu.add_command(label="No loved books", command=self.set_option)
        
        
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


    def handle_loved_menu(self): #determines the result of clicking the button
        self.menu.delete(0, tk.END)
        loved_books = self.db.get_loved_books()
        #print("Loved Books:", loved_books)  # Debug print statement
        if not loved_books:
            self.menu.add_command(label="No loved books", state=tk.DISABLED)
        else: #displays book names that have Loved set to true
            for book_name in loved_books:
                self.menu.add_command(
                    label=book_name,
                    command=lambda b=book_name: self.display_loved_book(b)
    )

        self.menu.post(self.lovedbooks_button.winfo_rootx(), self.lovedbooks_button.winfo_rooty() + self.lovedbooks_button.winfo_height())






    def toggle_love_book(self):
        if self.barcode_data:
            #toggle the loved status in the database
            self.db.toggle_loved_status(self.barcode_data)
          

        # Fetch the updated book data
        book_data = self.db.get_book_data(self.barcode_data)
        if book_data:
            _, _, _, _, _, _, _, _, _, _, _, loved = book_data
            loved_status = loved == "True"  #database stores "True" or "False" as strings
            self.love_book_button.config(text="Unlove Book" if loved_status else "Love Book",
                                         bg="red" if loved_status else "green")
            
      

    def display_loved_book(self, book_name):#callback function for when you click the name of a book under Loved books
    
        #fetch the book data by name
        book_data = self.db.get_loved_book_data_by_name(book_name)
        if book_data:
            #unpack the book data
            isbn, name, author, genre, rating, summary, good_review1, good_review2, bad_review1, bad_review2, pages, loved = book_data
            #set the barcode data to the ISBN of the selected book
            self.barcode_data = isbn
            #call output_page to display the book information
            self.output_page()



    def display_rec_books(self, genre, current_book_name):#procedure for managing the result of clicking the recommended books
        self.rec_menu.delete(0, tk.END)
        rec_books = self.db.get_books_by_genre(genre)
        if not rec_books:
            self.rec_menu.add_command(label="No similar books found", state=tk.DISABLED)
        else:
            for book_name in rec_books:
                if book_name != current_book_name:  #skip the current book
                    self.rec_menu.add_command(
                        label=book_name,
                        command=lambda b=book_name: self.prepare_and_show_book(b)
                    )


    def prepare_and_show_book(self, book_name):#callback function for recommended books
        # Fetch book data by name
        book_data = self.db.get_book_data_by_name(book_name)
        if book_data:
            # Clear the current output page
            self.clear_output_page()
            # Unpack the book data
            isbn, _, _, _, _, _, _, _, _, _, _, _ = book_data
            # Set the barcode data to the ISBN of the selected book
            self.barcode_data = isbn
            # Call output_page to display the book information
            self.output_page()
        else:
            messagebox.showerror("Error", "Book not found in the database.")


            

    def calculate_reading_time(self, total_pages, average_time_per_page= 1.7):#average reading time is 1.7 minutes
   
        reading_time = round(total_pages * average_time_per_page)


        hours = reading_time // 60
        minutes = reading_time % 60

        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"


    def clear_output_page(self):
        #clears all the widgets from the output page
        for widget in self.root.pack_slaves():
            widget.pack_forget()
        for widget in self.root.place_slaves():
            widget.place_forget()

    def output_page(self):#main method for outputting information onto my frame

        self.clear_output_page()#clear page

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


             #check the "Loved" status and set button label initially
            loved_status = loved == "True"  #True if loved is "True", otherwise False
            self.love_book_button.config(text="Unlove Book" if loved_status else "Love Book",
                                     bg="red" if loved_status else "green")
            #self.love_book_button.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-10, y=10)  # Make sure to place it again


             #display book name
            self.name_label = tk.Label(self.root, text=name, font=("Helvetica", 24))
            self.name_label.pack(side=tk.TOP, anchor=tk.NW, padx= 20, pady=(20, 0))

            #display author
            self.author_label = tk.Label(self.root, text=f"Author: {author}", font=("Helvetica", 18))
            self.author_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=(5, 0))


             #display genre at the top under author
            self.genre_label = tk.Label(self.root, text=f"Genre: {genre}", font=("Helvetica", 16))
            self.genre_label.pack(side=tk.TOP, anchor= tk.NW,  padx=20, pady=20)

            #create the menu button for recommendations
            self.rec_menu_button = tk.Menubutton(self.root, text="Similar Recommendations", relief=tk.RAISED)
            self.rec_menu_button.pack(side=tk.BOTTOM, padx=20, pady=80)
            self.rec_menu= tk.Menu(self.rec_menu_button, tearoff=0)
            self.rec_menu_button['menu'] = self.rec_menu



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


            currentname = book_data[1]#getting the name of the current book
            #show similar books based on genre
            self.display_rec_books(genre, currentname)


            # Dropdown for Summary
            self.summary_button = tk.Button(self.root, text="Summary", command=self.show_summary)
            self.summary_button.pack(side=tk.TOP,anchor = tk.W, padx=20, pady=(10, 0))

            # Dropdown for Reviews
            self.reviews_var = tk.StringVar(value = "Reviews", name = "Reviews")
            self.reviews_menu = tk.OptionMenu(self.root, self.reviews_var, "Review 1", "Review 2", "Review 3", "Review 4", command=self.show_review)
            self.reviews_menu.pack(side=tk.LEFT,anchor = tk.W, padx=20, pady=(10, 0))

            # Initialize labels for summary and reviews, but do not pack them yet


            #self.summary_label = tk.Label(self.root, text="", font=("Helvetica", 16))
            self.summary_label = tk.Label(self.root, text="", font=("Helvetica", 16), wraplength=500, justify='left', anchor='nw')

            #self.review_label = tk.Label(self.root, text="", font=("Helvetica", 16))
            self.review_label = tk.Label(self.root, text="", font=("Helvetica", 16), wraplength=500, justify='left', anchor='nw')


            # Store book data in instance variables for later use
            self.book_summary = summary
            self.book_reviews = {'Review 1': good_review1, 'Review 2': good_review2, 'Review 3': bad_review1, 'Review 4': bad_review2}



            
           
           

        else:# if there is no ISBN matching to the scanned one in the database
            # ISBN not found in the database
            self.book_info_label = tk.Label(self.root, text="Book not found in the database.", font=("Helvetica", 16))
            self.book_info_label.pack(side=tk.TOP, padx=20, pady=20)
        #self.result_label.config(text=f"ISBN Data:\n{self.barcode_data}", font=("Helvetica", 20))
        #self.result_label.pack(side=tk.TOP, anchor=tk.NW, padx=20, pady=20)



    
    
    def show_summary(self):#outputs summary button onto page
        #fetch book data from DB by using ISBN
        book_data = self.db.get_book_data(self.barcode_data)

        if book_data:
            # Assuming self.summary_button.y is the y-coordinate of the Summary button
            summary_button_y = self.summary_button.winfo_y()
            summary_button_height = self.summary_button.winfo_height()
            self.summary_label.config(text=self.book_summary)
            # Place the summary output below the summary button
            self.summary_label.place(x=20, y=summary_button_y + summary_button_height + 10, width=800, anchor='nw')
        


    def show_review(self, select):#outputs reviews button onto page

        #fetch book data from DB by using ISBN
        book_data = self.db.get_book_data(self.barcode_data)

        if book_data:
            # Assuming self.reviews_menu.y is the y-coordinate of the Reviews dropdown
            reviews_menu_y = self.reviews_menu.winfo_y()
            reviews_menu_height = self.reviews_menu.winfo_height()
            selected_review = self.book_reviews.get(select, "")
            self.review_label.config(text=selected_review)
            # Place the review output below the reviews dropdown
            self.review_label.place(x=20, y=reviews_menu_y + reviews_menu_height + 10, width=800, anchor='nw')
    


    def reset_app(self):#clear the output page and revert back to state of webcam page
        

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



   
class Database:#to manage the tasks to do with editing and pulling info from the database
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):#connecting to DB
        return sqlite3.connect(self.db_path)

    def get_book_data(self, isbn):#retrieving book data 
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM books WHERE ISBN = ?"
        cursor.execute(query, (isbn,))
        data = cursor.fetchone()
        conn.close()
        return data
    


    def toggle_loved_status(self, isbn):#change state of the Loved field between True and False
        conn = self._connect()
        cursor = conn.cursor()
        
        #fetch the current "Loved" field status
        query = "SELECT Loved FROM books WHERE ISBN = ?"
        cursor.execute(query, (isbn,))
        current_status = cursor.fetchone()[0]
        
        #field data from string to boolean
        is_loved = current_status == "True"
        
        #toggle the "Loved" status
        new_status = "False" if is_loved else "True"
        
        #update the "Loved" status in the database
        update_query = "UPDATE books SET Loved = ? WHERE ISBN = ?"
        cursor.execute(update_query, (new_status, isbn))
        conn.commit()
        conn.close()


    def get_loved_books(self):#retrieve all book names that have Loved set to true 
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT Name FROM books WHERE Loved = 'True'"
        cursor.execute(query)
        books = cursor.fetchall()
        conn.close()
        return [book[0] for book in books]  # Extract book names from tuples
   

  
    
    def get_loved_book_data_by_name(self, name):#retrieve info about books based off their names as long as Loved=true
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM books WHERE Name = ? AND Loved = 'True'"
        cursor.execute(query, (name,))
        data = cursor.fetchone()
        conn.close()
        return data
    

    def get_book_data_by_name(self, name):#retrieve info about books based off their names
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT * FROM books WHERE Name = ?"
        cursor.execute(query, (name,))
        data = cursor.fetchone()
        conn.close()
        return data

    
    def get_books_by_genre(self, genre):#retrieve names of books based off their genre
        conn = self._connect()
        cursor = conn.cursor()
        query = "SELECT Name FROM books WHERE Genre = ?"
        cursor.execute(query, (genre,))
        books = cursor.fetchall()
        conn.close()
        return [book[0] for book in books]
    

        
root = tk.Tk()  #Create the main application window
app = GUI(root)  #Initialize the GUI application
root.mainloop()  #Start the main event loop for the GUI


