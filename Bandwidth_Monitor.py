import tkinter as tk
from threading import Thread
from scapy.all import *
import os
import psutil
from collections import defaultdict
from win32api import GetMonitorInfo, MonitorFromPoint

KB = float(1024)
MB = float(KB ** 2)
GB = float(KB ** 3)
TB = float(KB ** 4)
all_macs = {iface.mac for iface in ifaces.values()}

WINDOW_SIZE = (240, 280)
WINDOW_RESIZEABLE = True  
REFRESH_DELAY = 1500

last_upload, last_download, upload_speed, down_speed = 0, 0, 0, 0
def size(B):
    B = float(B)
    if B < KB:
        return f"{B} Bytes"
    elif KB <= B < MB:
        return f"{B/KB:.2f} KB"
    elif MB <= B < GB:
        return f"{B/MB:.2f} MB"
    elif GB <= B < TB:
        return f"{B/GB:.2f} GB"
    elif TB <= B:
        return f"{B/TB:.2f} TB"
window = tk.Tk()
window.title("Network Bandwidth Monitor")
window.attributes("-topmost", True)
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
work_area = monitor_info.get("Work")[3]

window_x = screen_width - WINDOW_SIZE[0]
window_y = work_area - WINDOW_SIZE[1]

window.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}+{window_x}+{window_y}")
window.resizable(width=WINDOW_RESIZEABLE, height=WINDOW_RESIZEABLE)

label_total_upload_header = tk.Label(text="Total Upload:", font="Quicksand 12 bold")
label_total_upload_header.pack()
label_total_upload = tk.Label(text="Calculating...", font="Quicksand 12")
label_total_upload.pack()

label_total_download_header = tk.Label(text="Total Download:", font="Quicksand 12 bold")
label_total_download_header.pack()
label_total_download = tk.Label(text="Calculating...", font="Quicksand 12")
label_total_download.pack()

label_total_usage_header = tk.Label(text="Total Network Usage:", font="Quicksand 12 bold")
label_total_usage_header.pack()
label_total_usage = tk.Label(text="Calculating...\n", font="Quicksand 12")
label_total_usage.pack()

label_upload_header = tk.Label(text="Upload Speed:", font="Quicksand 12 bold")
label_upload_header.pack()
label_upload = tk.Label(text="Calculating...", font="Quicksand 12")
label_upload.pack()

label_download_header = tk.Label(text="Download Speed:", font="Quicksand 12 bold")
label_download_header.pack()
label_download = tk.Label(text="Calculating...", font="Quicksand 12")
label_download.pack()

def process_packet(packet):
    pass

def start_packet_capture():
    while True:
        sniff(filter="tcp or udp and (portrange 1-65535)", prn=process_packet, count=1, store=0)

packet_capture_thread = Thread(target=start_packet_capture)
packet_capture_thread.daemon = True
packet_capture_thread.start()

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

    label_total_upload["text"] = f"{size(upload)}"
    label_total_download["text"] = f"{size(download)}"
    label_total_usage["text"] = f"{size(total)}\n"

    label_upload["text"] = size(upload_speed)
    label_download["text"] = size(down_speed)

    label_total_upload.pack()
    label_total_download.pack()
    label_total_usage.pack()
    label_upload.pack()
    label_download.pack()

    window.after(REFRESH_DELAY, update)

window.after(REFRESH_DELAY, update)
window.mainloop()
