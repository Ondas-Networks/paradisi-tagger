import threading
import queue
import time
import sqlite3  # assuming SQLite is used for the database
import usb.core  # for USB device communication
# from sense_hat import SenseHat


class BarcodeScanner(threading.Thread):
    """Thread class to read data from the barcode scanner and put it into the input queue."""

    def __init__(self, input_queue, sense_hat):
        super().__init__()
        self.input_queue = input_queue
        self.scanner = None
        self.sense_hat = sense_hat

    def find_scanner(self):
        """Find the barcode scanner device and set it as the scanner attribute."""
        while self.scanner is None:
            self.scanner = usb.core.find(
                idVendor="0x03f0", idProduct="0x2d39"
            )  # replace with actual IDs
            if self.scanner is None:
                self.sense_hat.set_pixel(
                    7, 7, 255, 0, 0
                )  # Red pixel to indicate scanner not found
                time.sleep(1)  # Wait for 1 second before trying again

    def run(self):
        self.find_scanner()
        self.sense_hat.clear((0, 255, 0))  # Green flash
        while True:
            try:
                data = self.scanner.read(8)
                barcode = "".join([chr(x) for x in data])
                self.input_queue.put(barcode)
            except usb.core.USBError:
                self.scanner = None
                self.find_scanner()


class DatabaseUpdater(threading.Thread):
    """Thread class to update the database based on the barcode data from the input queue."""

    def __init__(self, input_queue, sense_hat):
        super().__init__()
        self.input_queue = input_queue
        self.sense_hat = sense_hat
        # Initialize database connection
        self.conn = sqlite3.connect("your_database.db")
        self.cursor = self.conn.cursor()

    def run(self):
        while True:
            barcode = self.input_queue.get()
            success = self.update_database(barcode)
            if success:
                self.sense_hat.show_tick()
            else:
                self.sense_hat.show_cross()
            time.sleep(1)  # prevent rapid updates, adjust as needed

    def update_database(self, barcode):
        try:
            # Perform database update action
            # Example: self.cursor.execute("UPDATE table SET column = value WHERE barcode = ?", (barcode,))
            # self.conn.commit()
            return True  # Successful update
        except Exception as e:
            print("Error updating database:", e)
            return False  # Failed update


class SenseHatDisplay:
    def __init__(self):
        self.sense_hat = SenseHat()

    def show_tick(self):
        self.sense_hat.clear((0, 255, 0))  # Green
        # Display a tick mark, customize as needed

    def show_cross(self):
        self.sense_hat.clear((255, 0, 0))  # Red
        # Display a cross mark, customize as needed


def main():
    input_queue = queue.Queue()
    sense_hat_display = SenseHatDisplay()

    barcode_scanner = BarcodeScanner(input_queue, sense_hat_display)
    # database_updater = DatabaseUpdater(input_queue, sense_hat_display)

    barcode_scanner.start()
    # database_updater.start()

    # Keep the main thread running
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
