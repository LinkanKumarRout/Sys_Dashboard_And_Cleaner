"""
Ultra Cleaner Pro
Developed By: LinkanKumarRout
"""

import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------ THEMES ------------------ #
themes = {
    "Dark": {
        "bg": "#121212",
        "fg": "#00ff9f",
        "label": "#00e5ff",
        "cpu": "#ff9800",
        "net": "#03a9f4",
        "box_bg": "#1e1e1e",
        "btn_bg": "#1f1f1f",
        "hover": "#ffffff",
        "graph_text": "white",
    },
    "Light": {
        "bg": "#f4f6f8",
        "fg": "#222",
        "label": "#1565c0",
        "cpu": "#c62828",
        "net": "#2e7d32",
        "box_bg": "#ffffff",
        "btn_bg": "#e0e0e0",
        "hover": "#555555",
        "graph_text": "black",
    },
    "Blue": {
        "bg": "#0a192f",
        "fg": "#64ffda",
        "label": "#8892b0",
        "cpu": "#ffcc00",
        "net": "#00bcd4",
        "box_bg": "#112240",
        "btn_bg": "#233554",
        "hover": "#ffffff",
        "graph_text": "white",
    },
}

current_theme = themes["Dark"]


# ------------------ HOVER ------------------ #
def add_hover(widget):
    def on_enter(e):
        widget.config(fg=current_theme["hover"])

    def on_leave(e):
        widget.config(fg=current_theme["fg"])

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


# ------------------ LOG ------------------ #
def log_output(text):
    log_box.config(state="normal")
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)
    log_box.config(state="disabled")


def clear_logs():
    log_box.config(state="normal")
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, "🗑 Logs cleared successfully...\n")
    log_box.config(state="disabled")


# ------------------ APPLY THEME ------------------ #
def apply_theme(theme):
    global current_theme
    current_theme = theme

    root.configure(bg=theme["bg"])
    topbar.config(bg=theme["bg"])
    content.config(bg=theme["bg"])

    title.config(bg=theme["bg"], fg=theme["fg"])

    ram_label.config(bg=theme["bg"], fg=theme["label"])
    cpu_label.config(bg=theme["bg"], fg=theme["cpu"])
    net_label.config(bg=theme["bg"], fg=theme["net"])

    log_box.config(bg=theme["box_bg"], fg=theme["fg"])

    for b in action_buttons + theme_buttons:
        b.config(
            bg=theme["btn_bg"],
            fg=theme["fg"],
            activebackground=theme["bg"],
            activeforeground=theme["hover"],
        )

    # ttk progressbar fix
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor=theme["box_bg"],
        background=theme["fg"],
    )

    ram_bar.config(style="Custom.Horizontal.TProgressbar")
    cpu_bar.config(style="Custom.Horizontal.TProgressbar")

    root.update_idletasks()


# ------------------ SYSTEM ------------------ #
def get_ram():
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    total = int(lines[0].split()[1]) / 1024
    avail = int(lines[2].split()[1]) / 1024
    used = total - avail
    percent = used / total * 100
    return used, total, percent


def get_cpu():
    try:
        return float(os.popen("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'").read())
    except:
        return 0


last_rx, last_tx = 0, 0


def get_net():
    global last_rx, last_tx
    with open("/proc/net/dev") as f:
        data = f.readlines()[2:]

    rx = tx = 0
    for line in data:
        vals = line.split()
        rx += int(vals[1])
        tx += int(vals[9])

    down = (rx - last_rx) / 1024
    up = (tx - last_tx) / 1024
    last_rx, last_tx = rx, tx
    return down, up


# ------------------ GRAPH ------------------ #
ram_data = []


def update_graph():
    while True:
        _, _, p = get_ram()
        ram_data.append(p)
        if len(ram_data) > 50:
            ram_data.pop(0)

        ax.clear()
        ax.plot(ram_data, color=current_theme["fg"])

        ax.set_facecolor(current_theme["box_bg"])
        fig.patch.set_facecolor(current_theme["bg"])

        txt = current_theme["graph_text"]
        ax.tick_params(colors=txt)

        for spine in ax.spines.values():
            spine.set_color(txt)

        ax.set_title("RAM Usage", color=txt)
        ax.grid(True, linestyle="--", linewidth=0.5)

        canvas.draw()
        time.sleep(1)


# ------------------ STATS ------------------ #
def update_stats():
    while True:
        used, total, p = get_ram()
        cpu = get_cpu()
        down, up = get_net()

        ram_label.config(text=f"RAM: {used:.0f}/{total:.0f} MB ({p:.1f}%)")
        cpu_label.config(text=f"CPU: {cpu:.1f}%")
        net_label.config(text=f"⬇ {down:.1f} KB/s | ⬆ {up:.1f} KB/s")

        ram_bar["value"] = p
        cpu_bar["value"] = cpu
        time.sleep(1)


# ------------------ SMART ------------------ #
def get_size(path):
    total = 0
    for r, d, f in os.walk(path):
        for file in f:
            try:
                total += os.path.getsize(os.path.join(r, file))
            except:
                pass
    return total / (1024 * 1024)


def smart_popup():
    cache = get_size(os.path.expanduser("~/.cache"))
    tmp = get_size("/tmp")

    if cache > 100 or tmp > 50:
        log_output("⚠ Cleaning recommended!")
    else:
        log_output("✅ System looks clean")

    log_output(f"Cache: {cache:.1f} MB | Temp: {tmp:.1f} MB")


# ------------------ COMMAND ------------------ #
def run_cmd(title, cmd, sudo=False):
    def task():
        log_output(f"\n===== {title} START =====")
        cmd2 = f"pkexec bash -c '{cmd}'" if sudo else cmd

        p = subprocess.Popen(
            cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in p.stdout:
            log_output("[OUT] " + line.strip())

        for line in p.stderr:
            log_output("[ERR] " + line.strip())

        p.wait()
        log_output(f"===== {title} DONE =====\n")

    threading.Thread(target=task, daemon=True).start()


def clear_ram():
    run_cmd("Clear RAM", "sync && echo 3 > /proc/sys/vm/drop_caches", True)


def clear_temp():
    run_cmd("Clear Temp", "rm -rfv /tmp/*", True)


def clear_cache():
    run_cmd("Clear Cache", "rm -rfv ~/.cache/*")


# ------------------ UI ------------------ #
root = tk.Tk()
root.title("Ultra Cleaner Pro")
root.geometry("950x700")

topbar = tk.Frame(root)
topbar.pack(fill="x", pady=5)

theme_buttons = []
for t in themes:
    b = tk.Button(topbar, text=t, command=lambda n=t: apply_theme(themes[n]))
    b.pack(side="left", padx=5)
    add_hover(b)
    theme_buttons.append(b)

content = tk.Frame(root)
content.pack(expand=True, fill="both")

title = tk.Label(content, text="SYSTEM DASHBOARD", font=("Segoe UI", 18))
title.pack(pady=10)

ram_label = tk.Label(content)
ram_label.pack()
cpu_label = tk.Label(content)
cpu_label.pack()
net_label = tk.Label(content)
net_label.pack()

ram_bar = ttk.Progressbar(content, length=700)
ram_bar.pack(pady=5)

cpu_bar = ttk.Progressbar(content, length=700)
cpu_bar.pack(pady=5)

fig, ax = plt.subplots(figsize=(7, 2))
canvas = FigureCanvasTkAgg(fig, master=content)
canvas.get_tk_widget().pack()

actions = tk.Frame(content)
actions.pack(pady=10)

action_buttons = []


def act_btn(t, c, col):
    b = tk.Button(actions, text=t, command=c, width=15)
    b.grid(row=0, column=col, padx=5)
    add_hover(b)
    action_buttons.append(b)


act_btn("Clear RAM", clear_ram, 0)
act_btn("Clear Temp", clear_temp, 1)
act_btn("Clear Cache", clear_cache, 2)
act_btn("Smart Suggest", smart_popup, 3)

log_frame = tk.Frame(content)
log_frame.pack(fill="both", expand=True)

log_box = scrolledtext.ScrolledText(log_frame, height=10, state="disabled")
log_box.pack(side="left", fill="both", expand=True, padx=10, pady=10)

clear_btn = tk.Button(log_frame, text="Clear Logs", command=clear_logs)
clear_btn.pack(side="right", padx=10)
add_hover(clear_btn)
action_buttons.append(clear_btn)

apply_theme(themes["Dark"])

threading.Thread(target=update_stats, daemon=True).start()
threading.Thread(target=update_graph, daemon=True).start()

log_output("Ultra Cleaner Ready...!!!")

root.mainloop()
