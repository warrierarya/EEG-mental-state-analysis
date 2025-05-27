import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
from PIL import Image, ImageTk
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
matlab_file = 'process_eeg.m'
textfile = 'eeg_results.txt'
power_spectrum = 'eeg_power.png'
power_bands = 'eeg_bands.png'
path = "C:\\Users\\santh.UNNIMAYA\\OneDrive" ######please add the path of your devoce foe this code to work
class output(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.expected_files = {
            os.path.join(path, textfile),
            os.path.join(path, power_spectrum),
            os.path.join(path, power_bands),
        }
        self.files_created = set()
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path in self.expected_files:
            self.files_created.add(event.src_path)
            if self.files_created == self.expected_files:
                self.callback()

def delete_previous_files():
    results_file_path = os.path.join(path, textfile)
    power_plot_path = os.path.join(path, power_spectrum)
    bands_plot_path = os.path.join(path, power_bands)

    files_to_delete = [results_file_path, power_plot_path, bands_plot_path]

    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted previous file: {file_path}")
        except Exception as e:
            print(f"Error deleting previous file {file_path}: {e}")

def clear_results_display():
    
    results_text.config(state=tk.NORMAL)
    results_text.delete("1.0", tk.END)
    results_text.config(state=tk.DISABLED)
    power_label.config(image=None)
    bands_label.config(image=None)
    power_label.image = None
    bands_label.image = None  

def run_matlab_script(mat_file_path):
    if not mat_file_path:
        messagebox.showerror("Error", "Please select a .mat file.")
        return

    clear_results_display()
    delete_previous_files()
    results_frame.config(text="Processing and Saving to path...")
    run_button.config(state=tk.DISABLED)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    matlab_function_path = os.path.join(script_dir, matlab_file)
    matlab_command = f"matlab -nosplash -nodesktop -r \"cd('{script_dir}'); try, process_eeg('{mat_file_path}'); catch e, disp(getReport(e)); exit(1); end; exit(0);\""
    subprocess.Popen(matlab_command, shell=True)

    
    global observer
    event_handler = output(update_gui_after_matlab)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

   

def update_gui_after_matlab():
   
    window.after(0, _update_gui) 


def browse_file():
   
    file_path = filedialog.askopenfilename(
        defaultextension=".mat",
        filetypes=[("MATLAB files", "*.mat"), ("All files", "*.*")]
    )
    if file_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(0, file_path)
def _update_gui():
 
    results_frame.config(text="Processing Results")
    run_button.config(state=tk.NORMAL)
    update_results()
    update_plots()
    messagebox.showinfo("Success", "EEG processing complete!\nResults and plots updated.")



def update_plots():
    
    power_plot_path = os.path.join(path, power_spectrum)
    bands_plot_path = os.path.join(path, power_bands)

    try:
        power_img = Image.open(power_plot_path)
        power_img = power_img.resize((300, 200))
        power_tk_img = ImageTk.PhotoImage(power_img)
        power_label.config(image=power_tk_img)
        power_label.image = power_tk_img
    except FileNotFoundError:
        power_label.config(image=None)
        print(f"Warning: Power plot not found at {power_plot_path}")

    try:
        bands_img = Image.open(bands_plot_path)
        bands_img = bands_img.resize((300, 200))
        bands_tk_img = ImageTk.PhotoImage(bands_img)
        bands_label.config(image=bands_tk_img)
        bands_label.image = bands_tk_img
    except FileNotFoundError:
        bands_label.config(image=None)
        print(f"Warning: Bands plot not found at {bands_plot_path}")
def update_results():
    
    results_file_path = os.path.join(path, textfile)
    try:
        with open(results_file_path, "r") as f:
            results_text.config(state=tk.NORMAL)
            results_text.delete("1.0", tk.END)
            results_text.insert(tk.END, f.read())
            results_text.config(state=tk.DISABLED)
    except FileNotFoundError:
        results_text.config(state=tk.NORMAL)
        results_text.delete("1.0", tk.END)
        results_text.insert(tk.END, f"No results file found at {results_file_path} yet.")
        results_text.config(state=tk.DISABLED)
def on_closing():
    global observer
    if 'observer' in globals() and observer.is_alive():
        observer.stop()
        observer.join()
    window.destroy()
window = tk.Tk()
window.title("EEG Data Processor")
window.protocol("WM_DELETE_WINDOW", on_closing)
file_frame = tk.Frame(window)
file_frame.pack(pady=10)
file_path_label = tk.Label(file_frame, text="Select .mat file:")
file_path_label.pack(side=tk.LEFT)
file_path_entry = tk.Entry(file_frame, width=40)
file_path_entry.pack(side=tk.LEFT)
browse_button = tk.Button(file_frame, text="Browse", command=browse_file)
browse_button.pack(side=tk.LEFT, padx=5)
run_button = tk.Button(window, text="Process EEG Data", command=lambda: run_matlab_script(file_path_entry.get()))
run_button.pack(pady=10)
results_frame = tk.LabelFrame(window, text="Processing Results")
results_frame.pack(pady=10, padx=10, fill="both", expand=True)
results_text = tk.Text(results_frame, height=10, state=tk.DISABLED)
results_text.pack(fill="both", expand=True)
plots_frame = tk.Frame(window)
plots_frame.pack(pady=10, padx=10)
power_label = tk.Label(plots_frame)
power_label.pack(side=tk.LEFT, padx=10)
bands_label = tk.Label(plots_frame)
bands_label.pack(side=tk.LEFT, padx=10)
observer = None
update_results()
update_plots()
window.mainloop()