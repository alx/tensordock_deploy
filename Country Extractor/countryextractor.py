import json
import tkinter as tk
import os
import time

def check_file_modification():
    global last_modified
    try:
        current_modified = os.path.getmtime(hosts_file_path)
        if current_modified != last_modified:
            last_modified = current_modified
            filter_countries()
            update_last_checked_label()
    except FileNotFoundError:
        print("File not found. Please check the file path.")

def filter_countries():
    # Get countries from the entry field
    countries_to_filter_out = entry.get().split(',')  # Assumes countries are comma-separated

    try:
        if os.path.exists(hosts_file_path):
            with open(hosts_file_path, 'r') as file:
                data = json.load(file)

            hostnodes = data.get("hostnodes", {})
            countries = [node["location"]["country"] for node in hostnodes.values()]

            # Filter out specified countries, make unique, and sort
            filtered_countries = sorted(set(country for country in countries if country not in countries_to_filter_out))

            # Join the countries with a line break
            formatted_countries = "[\n" + ",\n".join([f'    "{country}"' for country in filtered_countries]) + "\n]"

            # Display filtered countries in the text area
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, formatted_countries)
        else:
            print("hosts.txt file not found!")
    except FileNotFoundError:
        print("File not found. Please check the file path.")

def update_last_checked_label():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    last_checked_label.config(text=f"Last checked: {current_time}")

def update_countdown_timer(seconds):
    if seconds >= 0:
        countdown_timer.config(text=f"Next check in: {seconds} seconds")
        root.after(1000, update_countdown_timer, seconds - 1)
    else:
        check_file_modification()
        root.after(5000, poll_file_modification)

# Get the directory of the script file
script_dir = os.path.dirname(os.path.abspath(__file__))
hosts_file_path = os.path.join(os.path.dirname(script_dir), 'hosts.txt')

last_modified = None

root = tk.Tk()
root.title("Country Filter")
root.geometry("500x600")

label = tk.Label(root, text="Enter countries to filter (comma-separated):")
label.pack(padx=10, pady=5)

entry = tk.Entry(root)
entry.pack(padx=10, pady=5)

filter_button = tk.Button(root, text="Filter Countries", command=filter_countries)
filter_button.pack(padx=20, pady=10)

text_area = tk.Text(root, height=20, width=50)
text_area.pack(padx=10, pady=10)

last_checked_label = tk.Label(root, text="")
last_checked_label.pack(pady=5)

countdown_timer = tk.Label(root, text="")
countdown_timer.pack(pady=5)

def poll_file_modification():
    check_file_modification()
    update_countdown_timer(30)

poll_file_modification()

root.mainloop()
