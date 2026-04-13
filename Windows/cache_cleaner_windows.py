"""
Ultra Cleaner Pro (Windows Version)
Developed By: LinkanKumarRout
"""

import os
import subprocess
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk

import matplotlib.pyplot as plt
import psutil
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

    # Buttons styling
    for b in action_buttons + theme_buttons:
        b.config(
            bg=theme["btn_bg"],
            fg=theme["fg"],
            activebackground=theme["bg"],
            activeforeground=theme["hover"],
        )

    # ttk Progressbar styling (IMPORTANT)
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
    mem = psutil.virtual_memory()
    return mem.used / 1024 / 1024, mem.total / 1024 / 1024, mem.percent


def get_cpu():
    return psutil.cpu_percent()


def get_net():
    net = psutil.net_io_counters()
    return net.bytes_recv / 1024, net.bytes_sent / 1024


# ------------------ GRAPH ------------------ #
ram_data = []


def update_graph():
    while True:
        _, _, p = get_ram()
        ram_data.append(p)
        if len(ram_data) > 50:
            ram_data.pop(0)

        ax.clear()
        ax.plot(ram_data, color=current_theme["fg"])  # FIXED COLOR

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
        net_label.config(text=f"⬇ {down:.1f} KB | ⬆ {up:.1f} KB")

        ram_bar["value"] = p
        cpu_bar["value"] = cpu
        time.sleep(1)


# ------------------ COMMAND ------------------ #
def run_cmd(title, cmd):
    def task():
        log_output(f"\n===== {title} START =====")

        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        for line in p.stdout:
            log_output("[OUT] " + line.strip())

        for line in p.stderr:
            log_output("[ERR] " + line.strip())

        p.wait()
        log_output(f"===== {title} DONE =====\n")

    threading.Thread(target=task, daemon=True).start()


# ------------------ CLEANERS ------------------ #
def clear_temp():
    run_cmd("Clear Temp", f'del /q/f/s "%TEMP%\\*"')


def clear_dns():
    run_cmd("Flush DNS", "ipconfig /flushdns")


def clear_prefetch():
    run_cmd("Clear Prefetch", "del /q/f/s C:\\Windows\\Prefetch\\*")


def smart_scan():
    temp = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, dn, filenames in os.walk(os.environ["TEMP"])
        for f in filenames
    ) / (1024 * 1024)

    log_output(f"Temp Size: {temp:.1f} MB")
    log_output("⚠ Cleaning recommended!" if temp > 500 else "✅ System looks clean")


# ------------------ UI ------------------ #
root = tk.Tk()
root.title("Ultra Cleaner Pro (Windows)")
root.geometry("950x700")

# TOPBAR
topbar = tk.Frame(root)
topbar.pack(fill="x", pady=5)

theme_buttons = []
for t in themes:
    b = tk.Button(topbar, text=t, command=lambda n=t: apply_theme(themes[n]))
    b.pack(side="left", padx=5)
    add_hover(b)
    theme_buttons.append(b)

# CONTENT
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

# ACTIONS
actions = tk.Frame(content)
actions.pack(pady=10)

action_buttons = []


def act_btn(t, c, col):
    b = tk.Button(actions, text=t, command=c, width=15)
    b.grid(row=0, column=col, padx=5)
    add_hover(b)
    action_buttons.append(b)


act_btn("Clear Temp", clear_temp, 0)
act_btn("Flush DNS", clear_dns, 1)
act_btn("Clear Prefetch", clear_prefetch, 2)
act_btn("Smart Scan", smart_scan, 3)

# LOG
log_frame = tk.Frame(content)
log_frame.pack(fill="both", expand=True)

log_box = scrolledtext.ScrolledText(log_frame, height=10, state="disabled")
log_box.pack(side="left", fill="both", expand=True, padx=10, pady=10)

clear_btn = tk.Button(log_frame, text="Clear Logs", command=clear_logs)
clear_btn.pack(side="right", padx=10)
add_hover(clear_btn)
action_buttons.append(clear_btn)

# INIT
apply_theme(themes["Dark"])

threading.Thread(target=update_stats, daemon=True).start()
threading.Thread(target=update_graph, daemon=True).start()

log_output("Ultra Cleaner Ready (Windows)...!!!")

root.mainloop()
