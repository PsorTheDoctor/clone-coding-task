import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_BASE_URL = 'http://localhost:7100'


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title('UART Device Control')
        self.root.geometry('800x600')

        toolbox = tk.Frame(root)
        toolbox.pack(fill='x', pady=5)

        self.start_btn = tk.Button(toolbox, text='Start Device', command=self.start_device)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = tk.Button(toolbox, text='Stop Device', command=self.stop_device)
        self.stop_btn.pack(side='left', pady=5)

        tk.Label(toolbox, text='Frequency (Hz):').pack(side='left', padx=5)
        self.freq_entry = tk.Entry(toolbox)
        self.freq_entry.pack(side='left', padx=5)

        self.debug_var = tk.IntVar()
        self.debug_checkbox = tk.Checkbutton(toolbox, text='Enable Debug Mode', variable=self.debug_var)
        self.debug_checkbox.pack(side='left', padx=5)

        self.config_btn = tk.Button(toolbox, text='Configure', command=self.config_device)
        self.config_btn.pack(side='left', padx=5)

        display = tk.Frame(root)
        display.pack(fill='x', pady=5)

        self.label = tk.Label(display, text='Pressure: -- Temp: -- Velocity: --')
        self.label.pack(side='left', padx=5)

        self.fig, self.axes = plt.subplots(3, 1, figsize=(10, 8))
        self.fig.tight_layout(pad=2)
        self.fig.patch.set_facecolor('#f0f0f0')

        self.x = []
        self.pressure = []
        self.temp = []
        self.velocity = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(pady=10, expand=True, fill='both')

        self.is_running = True
        self.refresh_thread = threading.Thread(target=self.update_data)
        self.refresh_thread.start()

        self.anim = animation.FuncAnimation(self.fig, self.animate, interval=100, save_count=100)

    def start_device(self):
        try:
            response = requests.get(f'{API_BASE_URL}/start')
            if response.status_code == 200:
                messagebox.showinfo('Success', 'Device started successfully')
            else:
                messagebox.showerror('Error', f'Failed to start device: {response.json()}')
        except:
            messagebox.showerror('Connection error', '')

    def stop_device(self):
        try:
            response = requests.get(f'{API_BASE_URL}/stop')
            if response.status_code == 200:
                messagebox.showinfo('Success', 'Device stopped successfully')
            else:
                messagebox.showerror('Error', f'Failed to stop device: {response.json()}')
        except:
            messagebox.showerror('Connection error', '')

    def config_device(self):
        try:
            frequency = int(self.freq_entry.get())
            debug_mode = bool(self.debug_var.get())

            payload = {'frequency': frequency, 'debug': debug_mode}
            response = requests.put(f'{API_BASE_URL}/configure', json=payload)

            if response.status_code == 200:
                messagebox.showinfo('Success', 'Device configured successfully')
            else:
                messagebox.showerror('Error', f'Failed to configure device: {response.json()}')
        except ValueError:
            messagebox.showerror('Error', '')

    def update_data(self):
        while self.is_running:
            try:
                response = requests.get(f'{API_BASE_URL}/device')
                if response.status_code == 200:
                    data = response.json()
                    latest = data.get('latest', {})
                    self.label.config(
                        text=f"Pressure: {latest.get('pressure', '--')} "
                             f"Temp: {latest.get('temperature', '--')} "
                             f"Velocity: {latest.get('velocity', '--')} "
                    )
                    self.x.append(time.time())
                    self.pressure.append(latest.get('pressure', 0))
                    self.temp.append(latest.get('temperature', 0))
                    self.velocity.append(latest.get('velocity', 0))

                    n = 50
                    self.x = self.x[-n:]
                    self.pressure = self.pressure[-n:]
                    self.temp = self.temp[-n:]
                    self.velocity = self.velocity[-n:]

                time.sleep(0.1)
            except:
                time.sleep(0.1)

    def animate(self, frame):
        data = [self.pressure, self.temp, self.velocity]
        labels = ['Pressure', 'Temperature', 'Velocity']

        for i in range(3):
            self.axes[i].cla()
            self.axes[i].plot(range(len(data[i])), data[i], label=labels[i])
            self.axes[i].set_ylabel(labels[i])
            self.axes[i].legend()

        self.canvas.draw()

    def on_close(self):
        self.is_running = False
        self.root.destroy()


root = tk.Tk()
app = GUI(root)
root.protocol('WM_DELETE_WINDOW', app.on_close)
root.mainloop()
