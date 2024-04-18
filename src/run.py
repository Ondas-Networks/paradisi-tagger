import threading
import queue
import time
import re
import usb.core  # for USB device communication
from sense_hat import SenseHat
from loguru import logger

from keyboard_alike import reader

# Import loguru

# Configure loguru to log to a file
logger.add("logs.log")

VENDOR_ID = 0x03f0
PRODUCT_ID = 0x2d39
BARCODE_PATTERN = r'^\d{10}$' # Regex representing a 10-digit barcode

class BarcodeScanner(threading.Thread):
    """Thread class to read data from the barcode scanner and put it into the input queue."""

    def __init__(self, input_queue, sense_hat):
        super().__init__()
        self.input_queue = input_queue
        self.scanner = None
        self.sense_hat = sense_hat

    def run(self):
        """Find the barcode scanner device and set it as the scanner attribute."""
        bit = False
        while True:
            try:
                self.scanner = reader.Reader(0x03f0, 0x2d39, 10, 8, True, debug=True)
                self.scanner.initialize()
                print(self.scanner)
                if bit is False:
                    self.sense_hat.set_pixel(
                        7, 7, 0, 255, 0
                    )
                    time.sleep(1)
                    self.sense_hat.clear()
                    bit = True
                text = self.scanner.read().strip()
                if re.match(BARCODE_PATTERN, text):
                    self.input_queue.put(text)
                    logger.info(f"Queue: {self.input_queue.queue}")
                self.scanner.disconnect()
            except Exception as e:
                logger.error(e)
                bit = False
                self.sense_hat.set_pixel(
                    7, 7, 255, 0, 0
                )
                time.sleep(1)
            finally:
                try:
                    self.scanner.disconnect()
                except Exception as e:
                    print("oops")


            
        # while not reader.Reader(0x03f0, 0x2d39, 10, 8, True, debug=True):
        #     self.sense_hat.set_pixel(
        #         7, 7, 255, 0, 0
        #     )
        #     time.sleep(1)
        # self.sense_hat.clear((0, 255, 0))  # Green flash
        # time.sleep(1)
        # self.sense_hat.clear()

        # while True:
        #     self.scanner = reader.Reader(0x03f0, 0x2d39, 10, 8, True, debug=True)
        #     while self.scanner is None:
        #         self.sense_hat.set_pixel(
        #             7, 7, 255, 0, 0
        #         )
        #         time.sleep(1)
        #         self.scanner = reader.Reader(0x03f0, 0x2d39, 10, 8, True, debug=True)
        #     self.scanner.initialize()
        #     text = self.scanner.read().strip()
        #     if re.match(BARCODE_PATTERN, text):
        #         self.input_queue.put(text)
        #         logger.info(f"Queue: {self.input_queue.queue}")
        #     self.scanner.disconnect()

    # def find_scanner(self):
    #     """Find the barcode scanner device and set it as the scanner attribute."""
    #     while self.scanner is None:
    #         self.scanner = usb.core.find(
    #             idVendor=VENDOR_ID, idProduct=PRODUCT_ID
    #         )  # replace with actual IDs
    #         if self.scanner is None:
    #             self.sense_hat.set_pixel(
    #                 7, 7, 255, 0, 0
    #             )  # Red pixel to indicate scanner not found
    #             time.sleep(1)  # Wait for 1 second before trying again
    #         else:
    #             self.scanner.set_configuration()
    #             self.sense_hat.clear((0, 255, 0))  # Green flash
    #             time.sleep(1)
    #             self.sense_hat.clear()

    # def run(self):
    #     self.find_scanner()
    #     while True:
    #         try:
    #             data = self.scanner.read(8)
    #             barcode = "".join([chr(x) for x in data])
    #             self.input_queue.put(barcode)
    #         except usb.core.USBError:
    #             self.scanner = None
    #             self.find_scanner()


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




def main():
    sense_hat_display = SenseHat()
    try:
        input_queue = queue.Queue()

        barcode_scanner = BarcodeScanner(input_queue, sense_hat_display)
        # database_updater = DatabaseUpdater(input_queue, sense_hat_display)

        barcode_scanner.start()
        # database_updater.start()

        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        barcode_scanner.join()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        sense_hat_display.clear()


if __name__ == "__main__":
    main()
