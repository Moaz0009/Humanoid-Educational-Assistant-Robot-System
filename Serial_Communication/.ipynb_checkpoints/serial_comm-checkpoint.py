import serial

def send(message, port='/dev/ttyUSB0', baudrate=9600):
    try:
        with serial.Serial(port, baudrate, timeout=2) as ser:
            ser.write(message.encode())
            print(f"Sent: {message}")
    except Exception as e:
        print(f"Serial send error: {e}")

def recieve(port='/dev/ttyUSB0', baudrate=9600, timeout=2):
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            print(f"Listening on {port}...")
            line = ser.readline().decode().strip()
            print(f"Received: {line}")
            return line
    except Exception as e:
        print(f"Serial read error: {e}")
        return None
