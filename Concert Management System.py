import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt

class ConcertManagement:
    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        """Create a database connection."""
        try:
            connection = mysql.connector.connect(
                host='localhost',  # Change if your DB is on a different host
                user='root',
                password='1234',
                database='concert_management'
            )
            if connection.is_connected():
                print("Connected to MySQL database")
                return connection
        except Error as e:
            print(f"Error: '{e}'")
            return None

    def add_concert(self, name, date, venue, tickets_available, price):
        """Add a new concert to the database with a price per ticket."""
        cursor = self.connection.cursor()
        query = "INSERT INTO concerts (name, date, venue, tickets_available, price) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, date, venue, tickets_available, price))
        self.connection.commit()
        cursor.close()
        print("Concert added successfully!")

    def book_ticket(self, concert_id, user_name, tickets, payment_mode):
        """Book tickets for a concert with a specified payment mode."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT tickets_available, booked_tickets, price FROM concerts WHERE id = %s", (concert_id,))
        concert = cursor.fetchone()

        if concert:
            tickets_available, booked_tickets, price = concert
            remaining_tickets = tickets_available - booked_tickets

            if tickets <= remaining_tickets:
                total_price = tickets * price
                print(f"The total price for {tickets} tickets is {total_price}. Payment mode: {payment_mode}")

                cursor.execute(
                    "INSERT INTO bookings (concert_id, user_name, tickets, payment_mode) VALUES (%s, %s, %s, %s)",
                    (concert_id, user_name, tickets, payment_mode)
                )
                cursor.execute("UPDATE concerts SET booked_tickets = booked_tickets + %s WHERE id = %s",
                               (tickets, concert_id))
                self.connection.commit()
                print(f"{tickets} tickets booked successfully for concert ID {concert_id} with {payment_mode}!")
            else:
                print("Not enough tickets available.")
        else:
            print("Concert not found.")
        cursor.close()

    def cancel_booking(self, booking_id):
        """Cancel a booking by booking ID."""
        cursor = self.connection.cursor()

        # Check if booking exists
        cursor.execute("SELECT concert_id, tickets FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()

        if booking:
            concert_id, tickets = booking

            # Delete booking and update the concert's booked tickets
            cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
            cursor.execute("UPDATE concerts SET booked_tickets = booked_tickets - %s WHERE id = %s", (tickets, concert_id))
            self.connection.commit()
            print(f"Booking ID {booking_id} has been canceled successfully.")
        else:
            print("Booking not found.")
        cursor.close()

    def view_concerts(self):
        """View all concerts."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM concerts")
        concerts = cursor.fetchall()
        for concert in concerts:
            print(f"ID: {concert[0]}, Name: {concert[1]}, Date: {concert[2]}, Venue: {concert[3]}, "
                  f"Tickets Available: {concert[4]}, Booked Tickets: {concert[5]}, Price: {concert[6]}")
        cursor.close()

    def plot_sales(self):
        """Plot the total tickets sold for each concert with both bar and line graphs."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, booked_tickets FROM concerts")
        data = cursor.fetchall()
        cursor.close()

        if not data:
            print("No sales data available to plot.")
            return

        # Prepare data for plotting
        concert_names = [row[0] for row in data]
        tickets_sold = [row[1] for row in data]

        # Create subplots: 1 row, 2 columns
        fig, axs = plt.subplots(1, 2, figsize=(20, 6))

        # Bar Graph
        axs[0].bar(concert_names, tickets_sold, color='skyblue')
        axs[0].set_xlabel("Concert Name")
        axs[0].set_ylabel("Tickets Sold")
        axs[0].set_title("Total Tickets Sold for Each Concert (Bar Graph)")
        axs[0].set_ylim(0, 100000)  # Set y-axis from 0 to 100000
        axs[0].tick_params(axis='x', rotation=45)

        # Line Graph
        axs[1].plot(concert_names, tickets_sold, marker='o', linestyle='-', color='green')
        axs[1].set_xlabel("Concert Name")
        axs[1].set_ylabel("Tickets Sold")
        axs[1].set_title("Total Tickets Sold for Each Concert (Line Graph)")
        axs[1].set_ylim(0, 100000)  # Set y-axis from 0 to 100000
        axs[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()

    def close_connection(self):
        """Close the database connection."""
        if self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    cm = ConcertManagement()
    while True:
        print("\nConcert Management System")
        print("1. Add Concert")
        print("2. Book Ticket")
        print("3. View Concerts")
        print("4. Cancel Booking")
        print("5. Plot Sales")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter concert name: ")
            date = input("Enter concert date (YYYY-MM-DD HH:MM:SS): ")
            venue = input("Enter concert venue: ")
            tickets_available = int(input("Enter tickets available: "))
            price = float(input("Enter ticket price: "))
            cm.add_concert(name, date, venue, tickets_available, price)

        elif choice == '2':
            concert_id = int(input("Enter concert ID: "))
            user_name = input("Enter your name: ")
            tickets = int(input("Enter number of tickets: "))
            payment_mode = input("Enter payment mode (e.g., Credit Card, PayPal): ")
            cm.book_ticket(concert_id, user_name, tickets, payment_mode)

        elif choice == '3':
            cm.view_concerts()

        elif choice == '4':
            booking_id = int(input("Enter booking ID to cancel: "))
            cm.cancel_booking(booking_id)

        elif choice == '5':
            cm.plot_sales()

        elif choice == '6':
            cm.close_connection()
            break

        else:
            print("Invalid choice, please try again.")
