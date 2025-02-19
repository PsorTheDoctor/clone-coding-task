import os
import argparse
import threading
import logging
import tkinter as tk

from uart import UARTHandler
from api import create_api
from gui import GUI

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()

    # UART params
    ap.add_argument('--serial_port', type=str, default=os.getenv('SERIAL_PORT', '/dev/ttyUSB0'), help='Serial port')
    ap.add_argument('--baudrate', type=int, default=os.getenv('BAUDRATE', 115000), help='Baudrate')
    ap.add_argument('--simulate', action='store_true', help='Run in a simulation mode')

    # HTTP server params
    ap.add_argument('--host', type=str, default=os.getenv('HOST', 'localhost'), help='Server host')
    ap.add_argument('--server_port', type=int, default=os.getenv('SERVER_PORT', 7100), help='Server port')
    # ap.add_argument('--database_path', type=str, default=os.getenv('DATABASE_PATH', 'database.db'), help='Database path')

    ap.add_argument('--gui', action='store_true', help='Open a graphic interface')
    args = ap.parse_args()

    # Shared variables
    is_running = [False]  # mutable list so threads can modify it
    messages = []

    uart = UARTHandler(args.serial_port, args.baudrate, args.simulate, is_running, messages)
    uart_thread = threading.Thread(target=uart.read_serial)
    uart_thread.start()

    api = create_api(is_running, messages, uart)
    api_thread = threading.Thread(target=lambda: api.run(
        host=args.host, port=args.server_port, debug=False, use_reloader=False
    ))
    api_thread.start()

    if args.gui:
        root = tk.Tk()
        app = GUI(root)
        root.protocol('WM_DELETE_WINDOW', app.on_close)
        root.mainloop()
    else:
        # Keep main thread alive
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logging.info('Shutting down...')
