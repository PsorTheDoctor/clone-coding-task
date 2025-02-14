import argparse
import serial
import threading
import time

ap = argparse.ArgumentParser()
ap.add_argument('--port', type=str, default='/dev/ttyUSB0', help='Port')
ap.add_argument('--baudrate', type=int, default=115000, help='Baudrate')
args = ap.parse_args()

is_running = False
messages = []

try:
    ser = serial.Serial(args.port, args.baudrate)
except serial.SerialException as e:
    print(e)


def parse_message(msg):
    try:
        if msg.startswith('$') and msg.endswith('\n'):
            msg = msg[1:-1]  # remove $ and \n
            values = list(map(float, msg.split(',')))
            if len(values) == 3:
                return {'pressure': values[0], 'temperature': values[1], 'velocity': values[2]}
    except ValueError:
        pass


def read_serial():
    global is_running
    while True:
        if is_running and ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            parsed = parse_message(data)
            if parsed:
                messages.append(parsed)
                if len(messages) > 100:
                    messages.pop(0)
        time.sleep(0.1)


if __name__ == '__main__':
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()
