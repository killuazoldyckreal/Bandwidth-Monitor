from tkinter import PhotoImage
import tkinter as tk
from threading import Thread
import os
import psutil
from win32api import GetMonitorInfo, MonitorFromPoint

KB = float(1024)
MB = float(KB ** 2)
GB = float(KB ** 3)
TB = float(KB ** 4)

WINDOW_SIZE = (525, 30)
WINDOW_RESIZEABLE = True 
REFRESH_DELAY = 1500

last_upload, last_download, upload_speed, down_speed = 0, 0, 0, 0

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
prev_x = 0
prev_y = 0

def start_drag(event):
    global prev_x, prev_y
    prev_x, prev_y = event.x_root, event.y_root

def on_drag(event):
    global prev_x, prev_y
    x, y = event.x_root - prev_x, event.y_root - prev_y
    window.geometry(f"+{window.winfo_x() + x}+{window.winfo_y() + y}")
    prev_x, prev_y = event.x_root, event.y_root
    
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

label_usage = tk.Label(text="Usage:",font="Quicksand 12 bold")
label_usage.grid(row=1,column=1)
usagedata = tk.Label(text="Calculating...", font="Quicksand 12",fg="gray")
usagedata.grid(row=1,column=2)
uplabel = tk.Label(text="| ⬆ Speed:", font="Quicksand 12 bold")
uplabel.grid(row=1,column=3)
updata = tk.Label(text="Calculating...", font="Quicksand 12", fg="#32CD30")
updata.grid(row=1,column=4)
downlabel = tk.Label(text="| ⬇ Speed:", font="Quicksand 12 bold")
downlabel.grid(row=1,column=5)
downdata = tk.Label(text="Calculating...", font="Quicksand 12", fg="#FF2511")
downdata.grid(row=1,column=6)
dragwin = tk.Label(window, image=image)
dragwin.grid(row=1, column=0)
dragwin.bind("<ButtonPress-1>", start_drag)
dragwin.bind("<B1-Motion>", on_drag)

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

window.after(REFRESH_DELAY, update)
window.mainloop()
