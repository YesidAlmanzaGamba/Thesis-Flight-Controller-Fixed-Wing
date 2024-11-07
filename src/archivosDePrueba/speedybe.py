import serial
import time

# Replace 'COM7' with the correct port for your system
port = 'COM7'
baudrate = 115200

def read_telemetry_data():
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Allow time for the connection to establish
        print(f"Connected to {port} at {baudrate} baud.")
    except serial.SerialException as e:
        print(f"Failed to connect to {port} at {baudrate} baud: {e}")
        return

    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                print(f"Received: {data}")
                if data.startswith('YPR:'):
                    ypr_data = data.split(',')
                    if len(ypr_data) == 4:
                        _, yaw, pitch, roll = ypr_data
                        print(f"Yaw: {yaw}, Pitch: {pitch}, Roll: {roll}")
            else:
                print("No data waiting...")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        ser.close()
        print("Serial connection closed.")

print("Starting telemetry data read...")
read_telemetry_data()
