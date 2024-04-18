import usb.core
import usb.util



# Define the Vendor ID and Product ID of your barcode scanner
# VENDOR_ID = 
# PRODUCT_ID = 

from keyboard_alike import reader

reader = reader.Reader(0x03f0, 0x2d39, 10, 8, True, debug=True)
reader.initialize()
print(reader.read().strip())
reader.disconnect()