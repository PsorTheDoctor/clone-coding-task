import serial
import logging
import time
import random

logging.basicConfig(level=logging.INFO)


class UARTHandler:
    def __init__(self, port, baudrate, simulate, is_running, messages):
        self.port = port
        self.baudrate = baudrate
        self.simulate = simulate
        self.is_running = is_running
        self.messages = messages
        self.ser = None

        if not self.simulate:
            try:
                self.ser = serial.Serial(port, baudrate, timeout=1)
                logging.info(f'Connected to UART device at {port} with baudrate {baudrate}')
            except:
                logging.error('Failed to connect to UART')
                self.simulate = True

    @staticmethod
    def parse_message(msg):
        try:
            if msg.startswith('$') and msg.endswith('\n'):
                msg = msg[1:-1]  # remove $ and \n
                values = list(map(float, msg.split(',')))
                if len(values) == 3:
                    return {'pressure': values[0], 'temperature': values[1], 'velocity': values[2]}
        except ValueError:
            logging.warning('Invalid message received')

    def read_serial(self):
        while True:
            if self.is_running[0] and (self.simulate or (self.ser and self.ser.in_waiting > 0)):
                data = self.simulate_data() if self.simulate else self.ser.readline().decode('utf-8').strip()
                parsed = self.parse_message(data)
                if parsed:
                    self.messages.append(parsed)
                    if len(self.messages) > 100:
                        self.messages.pop(0)
            time.sleep(0.1)

    def send_command(self, command):
        if self.simulate:
            logging.info(f'Simulating command: {command.strip()}')
        elif self.ser:
            logging.info(f'Sending command: {command.strip()}')
            self.ser.write(command.encode('utf-8'))

    @staticmethod
    def simulate_data():
        return f'${random.uniform(0, 1000):.2f},{random.uniform(0, 1000):.2f},{random.uniform(0, 1000):.2f}\n'
