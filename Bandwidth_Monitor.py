from tkinter import PhotoImage
import tkinter as tk
from threading import Thread
import os
import psutil
from win32api import GetMonitorInfo, MonitorFromPoint
import time

# Constants for data size conversions
KB = float(1024)
MB = float(KB ** 2)
GB = float(KB ** 3)
TB = float(KB ** 4)

# Window configuration
WINDOW_SIZE = (525, 30)
WINDOW_RESIZEABLE = True 
REFRESH_DELAY = 1500
MOUSE_AWAY_DELAY = 2

# Variables to store network data and mouse movement
last_upload, last_download, upload_speed, down_speed = 0, 0, 0, 0
last_mouse_move_time = time.time()

# Function to convert data size to appropriate unit
def size(B):
    B = float(B)
    if B < KB:
        return f"{B:.2f} Bytes"
    elif KB <= B < MB:
        return f"{B/KB:.2f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.2f} MB"
    elif GB <= B < TB:
        return f"{B/GB:.2f} GB"
    elif TB <= B:
        return f"{B/TB:.2f} TB"

# Variables to store previous mouse coordinates for dragging window
prev_x = 0
prev_y = 0

# Function to start dragging the window
def start_drag(event):
    global prev_x, prev_y
    prev_x, prev_y = event.x_root, event.y_root

# Function to handle dragging of the window
def on_drag(event):
    global prev_x, prev_y
    x, y = event.x_root - prev_x, event.y_root - prev_y
    window.geometry(f"+{window.winfo_x() + x}+{window.winfo_y() + y}")
    prev_x, prev_y = event.x_root, event.y_root

# Create Tkinter window
window = tk.Tk()
window.title("Network Bandwidth Monitor")
window.attributes("-topmost", True)
window.overrideredirect(True)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
image = PhotoImage(file='drag.png')
monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
work_area = monitor_info.get("Work")[3]

window_x = screen_width - WINDOW_SIZE[0]
window_y = work_area - WINDOW_SIZE[1]

window.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}+{window_x}+{window_y}")
window.resizable(width=WINDOW_RESIZEABLE, height=WINDOW_RESIZEABLE)

# Labels to display network usage and speeds
label_usage = tk.Label(text="Usage:", font="Quicksand 12 bold", width=6)
label_usage.grid(row=1, column=1)
usagedata = tk.Label(text="Calculating...", font="Quicksand 12", fg="gray", width=9)
usagedata.grid(row=1, column=2)
uplabel = tk.Label(text="| ⬆ Speed:", font="Quicksand 12 bold", width=6)
uplabel.grid(row=1, column=3)
updata = tk.Label(text="Calculating...", font="Quicksand 12", fg="#32CD30", width=11)
updata.grid(row=1, column=4)
downlabel = tk.Label(text="| ⬇ Speed:", font="Quicksand 12 bold", width=6)
downlabel.grid(row=1, column=5)
downdata = tk.Label(text="Calculating...", font="Quicksand 12", fg="#FF2511", width=11)
downdata.grid(row=1, column=6)
dragwin = tk.Label(window, image=image, width=20)
dragwin.grid(row=1, column=0)
dragwin.bind("<ButtonPress-1>", start_drag)
dragwin.bind("<B1-Motion>", on_drag)

# Function to check mouse position and reset mouse move time
def check_mouse_position(event):
    global last_mouse_move_time
    last_mouse_move_time = time.time()

window.bind("<Motion>", check_mouse_position)

# Function to check if the mouse is away and adjust window transparency accordingly
def check_mouse_away():
    global last_mouse_move_time
    while True:
        if time.time() - last_mouse_move_time > MOUSE_AWAY_DELAY:
            window.attributes('-alpha', 0.5) 
        else:
            window.attributes('-alpha', 1.0) 
        time.sleep(1)

# Start thread to monitor mouse position
mouse_away_thread = Thread(target=check_mouse_away)
mouse_away_thread.daemon = True
mouse_away_thread.start()

# Function to update network data and speeds periodically
def update():
    global last_upload, last_download, upload_speed, down_speed
    counter = psutil.net_io_counters()

    upload = counter.bytes_sent
    download = counter.bytes_recv
    total = upload + download

    if last_upload > 0:
        if upload < last_upload:
            upload_speed = 0
        else:
            upload_speed = upload - last_upload

    if last_download > 0:
        if download < last_download:
            down_speed = 0
        else:
            down_speed = download - last_download

    last_upload = upload
    last_download = download

    usagedata["text"] = f"{size(total)}"
    updata["text"] = f"{size(upload_speed)}"
    downdata["text"] = f"{size(down_speed)}"

    window.after(REFRESH_DELAY, update)

# Start updating network data
window.after(REFRESH_DELAY, update)
window.mainloop()
