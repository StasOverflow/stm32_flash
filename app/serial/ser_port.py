import serial


# ser = serial.Serial()

with serial.Serial() as ser:
    print("shit in closed state")

    # ser.baudrate = 230400
    # ser.port = 'COM5'
    # ser.open()
    # ser.write(b'hello')
