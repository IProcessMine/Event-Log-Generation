import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
import os
import yaml

class ToolTip:
    """
    Create a tooltip for a given widget.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        "Create a tooltip window and display the text."
        x, y, _cx, _cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        "Destroy the tooltip window."
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
def prompt_list(prompt_text):
    """
    Display a dialog box to prompt the user for a comma-separated list.

    :param prompt_text: The prompt text to display in the dialog.
    :return: A list of strings entered by the user.
    """
    response = simpledialog.askstring("Input", prompt_text)
    if response:
        return response.split(',')
    return []

def create_activity_defaults_frame(parent):
    """
    Create a frame for configuring activity defaults.

    :param parent: The parent widget in which this frame is contained.
    :return: A tuple containing the frame and a dictionary of entries.
    """
    frame = ttk.LabelFrame(parent, text="Activity Defaults")
    entries = {}
    defaults = {
        'min_weight': 1,
        'max_weight': 4,
        'duration_range': [1, 5],
        'duration_uom': 'days',
        'transaction_types': [],
        'transaction_duration_range': [1, 4],
        'transaction_duration_uom': 'minutes'
    }
    uoms = ['seconds', 'minutes', 'hours', 'days']
    transaction_types = ["start", "complete", "suspend", "resume"]

    for i, (key, default) in enumerate(defaults.items()):
        ttk.Label(frame, text=key.replace('_', ' ').title()).grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
        if 'uom' in key:
            entry = ttk.Combobox(frame, values=uoms)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.set(default)
            entries[key] = entry
        elif 'transaction_types' in key:
            entry = tk.StringVar(value=default)
            checkbuttons = []
            for j, ttype in enumerate(transaction_types):
                chk = ttk.Checkbutton(frame, text=ttype, variable=entry, onvalue=ttype, offvalue="")
                chk.grid(column=1+j, row=i, sticky=tk.W, padx=5, pady=5)
                checkbuttons.append(chk)
            entries[key] = entry
        else:
            entry = ttk.Entry(frame)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.insert(0, str(default))
            entries[key] = entry

    return frame, entries

def create_attribute_defaults_frame(parent):
    """
    Create a frame for configuring attribute defaults.

    :param parent: The parent widget in which this frame is contained.
    :return: A tuple containing the frame and a dictionary of entries.
    """
    frame = ttk.LabelFrame(parent, text="Attribute Defaults")
    entries = {}
    defaults = {
        'range': [0, 100],
        'distribution': 'uniform',
        'adjustment_type': 'slight_change',
        'generation_level': 'case'
    }
    distributions = ['normal', 'uniform', 'pareto', 'exponential']
    adjustment_types = ['slight_change', 'no_change', 'full_change']
    generation_levels = ['case', 'event', 'process']

    for i, (key, default) in enumerate(defaults.items()):
        ttk.Label(frame, text=key.replace('_', ' ').title()).grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
        if key == 'distribution':
            entry = ttk.Combobox(frame, values=distributions)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.set(default)
            entries[key] = entry
        elif key == 'adjustment_type':
            entry = ttk.Combobox(frame, values=adjustment_types)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.set(default)
            entries[key] = entry
        elif key == 'generation_level':
            entry = ttk.Combobox(frame, values=generation_levels)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.set(default)
            entries[key] = entry
        else:
            entry = ttk.Entry(frame)
            entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
            entry.insert(0, str(default))
            entries[key] = entry

    return frame, entries


def create_object_type_defaults_frame(parent):
    """
    Create a frame for configuring object type defaults.

    :param parent: The parent widget in which this frame is contained.
    :return: A tuple containing the frame and a dictionary of entries.
    """
    frame = ttk.LabelFrame(parent, text="Object Type Defaults")
    entries = {}
    defaults = {
        'range': [1, 4]
    }

    for i, (key, default) in enumerate(defaults.items()):
        ttk.Label(frame, text=key.replace('_', ' ').title()).grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
        entry = ttk.Button(frame, text="Edit", command=lambda k=key: entries[k].config(
            text=str(prompt_list(f"Enter {k.replace('_', ' ')} (comma separated)"))))
        entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        entry.config(text=str(default))
        entries[key] = entry

    return frame, entries


def create_trace_generation_defaults_frame(parent):
    """
    Create a frame for configuring trace generation defaults.

    :param parent: The parent widget in which this frame is contained.
    :return: A tuple containing the frame and a dictionary of entries.
    """
    frame = ttk.LabelFrame(parent, text="Trace Generation Defaults")
    entries = {}
    defaults = {
        'trace_count': 100,
        'event_count_range': [10, 200]
    }

    for i, (key, default) in enumerate(defaults.items()):
        ttk.Label(frame, text=key.replace('_', ' ').title()).grid(column=0, row=i, sticky=tk.W, padx=5, pady=5)
        entry = ttk.Entry(frame)
        entry.grid(column=1, row=i, columnspan=2, sticky=tk.EW, padx=5, pady=5)
        entry.insert(0, str(default))
        entries[key] = entry

    return frame, entries

def set_tooltips(entries, tooltips):
    """
    Set tooltips for the given entries.

    :param entries: A dictionary of entries to set tooltips for.
    :param tooltips: A dictionary of tooltips for the entries.
    :return: None
    """
    for key, tooltip_text in tooltips.items():
        if key in entries:
            ToolTip(entries[key], tooltip_text)

def initialize_gui():
    """
    Initialize the main GUI window and pack the frames for configuring defaults.

    :return: None
    """
    root = tk.Tk()
    root.title("Configuration Defaults")

    # Create a single main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)

    with open("Config/tooltips.yaml", 'r') as tooltips_file:
        tooltips = yaml.safe_load(tooltips_file)

    activity_frame, activity_entries = create_activity_defaults_frame(main_frame)
    activity_frame.pack(fill="both", expand=True, padx=10, pady=5)
    set_tooltips(activity_entries, tooltips['activity_tooltips'])

    attribute_frame, attribute_entries = create_attribute_defaults_frame(main_frame)
    attribute_frame.pack(fill="both", expand=True, padx=10, pady=5)
    set_tooltips(attribute_entries, tooltips['attribute_tooltips'])

    object_type_frame, object_type_entries = create_object_type_defaults_frame(main_frame)
    object_type_frame.pack(fill="both", expand=True, padx=10, pady=5)

    trace_generation_frame, trace_generation_entries = create_trace_generation_defaults_frame(main_frame)
    trace_generation_frame.pack(fill="both", expand=True, padx=10, pady=5)
    set_tooltips(trace_generation_entries, tooltips['trace_generation_tooltips'])

    def save_defaults():
        """
        Save the configured default values to a YAML file.

        :return: None
        """
        defaults = dict(
            activity_defaults={k: v.get() if isinstance(v, ttk.Entry) else (v[0].get(), v[1].get()) for k, v in
                               activity_entries.items()},
            attribute_defaults={k: v.get() if isinstance(v, ttk.Entry) else (v[0].get(), v[1].get()) for k, v in
                                attribute_entries.items()},
            object_type_defaults={k: v.get() if isinstance(v, ttk.Entry) else (v[0].get(), v[1].get()) for k, v
                                  in object_type_entries.items()},
            trace_generation_defaults={k: v.get() if isinstance(v, ttk.Entry) else (v[0].get(), v[1].get()) for
                                       k, v in trace_generation_entries.items()})

        # Save to YAML file in Config directory
        config_dir = os.path.join(os.getcwd(), 'Config')
        os.makedirs(config_dir, exist_ok=True)
        config_file_path = os.path.join(config_dir, 'defaults1.yaml')

        with open(config_file_path, 'w') as config_file:
            yaml.dump(defaults, config_file)

        messagebox.showinfo("Defaults Saved",
                            f"Configuration defaults have been saved successfully to {config_file_path}!")

    save_button = ttk.Button(main_frame, text="Save Defaults", command=save_defaults)
    save_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        initialize_gui()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")