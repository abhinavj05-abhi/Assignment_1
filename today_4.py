import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

# Parse allowed values from Excel cell strings
def parse_allowed_values(s):
    if pd.isna(s):
        return []
    s = str(s).strip()
    parts = [part.strip() for part in s.split(",") if part.strip()]
    result = []
    for part in parts:
        if part.startswith("[") and part.endswith("]") and ":" in part:
            range_str = part[1:-1]
            a, b = range_str.split(":")
            a = int(a) if a != "$" else float('-inf')
            b = int(b) if b != "$" and b != "∞" else float('inf')
            result.append(("range", (a, b)))
        else:
            try:
                value = int(part)
                result.append(("value", value))
            except ValueError:
                continue
    return result

# Parse user input (range or comma-separated, supporting multiple ranges)
def parse_user_input(s):
    s = s.strip()
    if not s:
        return None
    parts = [part.strip() for part in s.split(",") if part.strip()]
    ranges = []
    values = []
    for part in parts:
        if part.startswith("[") and part.endswith("]") and ":" in part:
            range_str = part[1:-1]
            try:
                a, b = map(int, range_str.split(":"))
                ranges.append((a, b))
            except ValueError:
                return None
        else:
            try:
                values.extend([int(v.strip()) for v in part.split() if v.strip()])
            except ValueError:
                return None
    if ranges and values:
        return {"type": "mixed", "ranges": ranges, "values": values}
    elif ranges:
        return {"type": "range", "ranges": ranges}
    elif values:
        return {"type": "list", "values": values}
    return None

# Parse bins input
def parse_bins_input(s):
    s = s.strip()
    if not s:
        return None
    try:
        bins = int(s)
        if bins <= 0:
            return None
        return bins
    except ValueError:
        return None

# Get maximum allowed range or values for feedback
def get_max_allowed_range(param, allowed_values):
    ranges = []
    values = []
    for gen in allowed_values:
        for item_type, item in allowed_values[gen].get(param, []):
            if item_type == "range":
                ranges.append(item)
            elif item_type == "value":
                values.append(item)
    if ranges:
        min_val = min(a for a, _ in ranges if a != float('-inf'))
        max_val = max(b for _, b in ranges if b != float('inf'))
        return f"[{min_val}:{max_val}] or {','.join(map(str, values)) if values else 'no discrete values'}"
    elif values:
        return ",".join(map(str, sorted(values)))
    return "No valid data"

# Check if input is allowed
def is_input_allowed(input_data, allowed):
    if input_data["type"] == "range":
        for min_val, max_val in input_data["ranges"]:
            for item_type, item in allowed:
                if item_type == "range":
                    a, b = item
                    if a <= min_val and max_val <= b:
                        break
                else:
                    return False
            else:
                return False
        return True
    elif input_data["type"] == "mixed":
        for min_val, max_val in input_data["ranges"]:
            for item_type, item in allowed:
                if item_type == "range":
                    a, b = item
                    if a <= min_val and max_val <= b:
                        break
                else:
                    return False
            else:
                return False
        for v in input_data["values"]:
            allowed_v = False
            for item_type, item in allowed:
                if item_type == "range" and item[0] <= v <= item[1]:
                    allowed_v = True
                    break
                elif item_type == "value" and item == v:
                    allowed_v = True
                    break
            if not allowed_v:
                return False
        return True
    else:  # list
        values = input_data["values"]
        for v in values:
            allowed_v = False
            for item_type, item in allowed:
                if item_type == "range" and item[0] <= v <= item[1]:
                    allowed_v = True
                    break
                elif item_type == "value" and item == v:
                    allowed_v = True
                    break
            if not allowed_v:
                return False
        return True

# Read Excel file
df = pd.read_excel("data_fc.xlsx", sheet_name="Sheet1")
parameters = df["Parameters"].tolist()
generations = df.columns[1:]

# Parse allowed values
allowed_values = {gen: {param: parse_allowed_values(df.loc[df["Parameters"] == param, gen].iloc[0]) 
                       for param in parameters} for gen in generations}

# Default bins value
default_bins = 1

# Create GUI
root = tk.Tk()
root.title("WiFi Functional Coverage Generator")
root.geometry("1000x900")

# Main frame and canvas for scrolling
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(main_frame)
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Add note about functionality
note_label = ttk.Label(scrollable_frame, 
    text="Note: Tick checkbox for IEEE default values (disables input). Use '+' to add bins. Bins field sets bin count (default 1, ignored for single values).",
    wraplength=950, foreground="blue")
note_label.grid(row=0, column=0, columnspan=6, pady=10)

# GUI elements
param_frames = {}
entries = {}  # dict of lists
bins_entries = {}
check_vars = {}

def toggle_entry_state(param):
    """Enable/disable entry fields based on checkbox state"""
    state = "disabled" if check_vars[param].get() else "normal"
    for entry in entries[param]:
        entry.configure(state=state)
    bins_entries[param].configure(state=state)

for i, param in enumerate(parameters):
    param_frame = ttk.Frame(scrollable_frame)
    param_frame.grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
    param_frames[param] = param_frame

    # Checkbox
    check_vars[param] = tk.BooleanVar(value=False)
    checkbox = ttk.Checkbutton(param_frame, text="", variable=check_vars[param], 
                               command=lambda p=param: toggle_entry_state(p))
    checkbox.grid(row=0, column=0, padx=5, pady=5)

    # Bins label
    bins_label = ttk.Label(param_frame, text="Bins:")
    bins_label.grid(row=0, column=1, padx=5, pady=5)

    # Bins entry
    bins_entry = ttk.Entry(param_frame, width=10)
    bins_entry.grid(row=0, column=2, padx=5, pady=5)
    bins_entries[param] = bins_entry

    # Parameter label
    label = ttk.Label(param_frame, text=f"{param}:")
    label.grid(row=0, column=3, padx=5, pady=5)

    # Input fields frame
    input_frame = ttk.Frame(param_frame)
    input_frame.grid(row=0, column=4, padx=5, pady=5)
    entries[param] = []

    def add_input_field(frame):
        entry = ttk.Entry(frame, width=20)
        entry.pack(side="left", padx=5)
        plus_btn = ttk.Button(frame, text="+", command=lambda f=frame: add_input_field(f))
        plus_btn.pack(side="left", padx=5)
        entries[param].append(entry)

    # Initial input field with '+'
    entry = ttk.Entry(input_frame, width=20)
    entry.pack(side="left", padx=5)
    plus_btn = ttk.Button(input_frame, text="+", command=lambda f=input_frame: add_input_field(f))
    plus_btn.pack(side="left", padx=5)
    entries[param].append(entry)

def validate_and_generate():
    inputs = {}
    bins_counts = {}
    invalid_entries = []

    # Collect and validate inputs
    for param in parameters:
        if check_vars[param].get():
            inputs[param] = None
            bins_counts[param] = default_bins
        else:
            param_inputs = []
            for entry in entries[param]:
                val = entry.get().strip()
                if val:
                    parsed = parse_user_input(val)
                    if parsed is None:
                        invalid_entries.append((entry, "Invalid format"))
                    else:
                        param_inputs.append(parsed)
            if param_inputs:
                inputs[param] = param_inputs
                bins_val = parse_bins_input(bins_entries[param].get())
                bins_counts[param] = bins_val if bins_val is not None else default_bins
            else:
                inputs[param] = None
                bins_counts[param] = default_bins

    # Validate aggregated inputs
    for param in parameters:
        if inputs[param] is not None:
            for entry, parsed in zip(entries[param], inputs[param] or []):
                allowed_anywhere = False
                for gen in generations:
                    if is_input_allowed(parsed, allowed_values[gen].get(param, [])):
                        allowed_anywhere = True
                        break
                if not allowed_anywhere:
                    invalid_entries.append((entry, f"Out of range. Allowed: {get_max_allowed_range(param, allowed_values)}"))

    # Handle invalid inputs
    if invalid_entries:
        for entry, msg in invalid_entries:
            entry.configure(background="pink")
        error_msg = "Some inputs are out of range:\n" + "\n".join([msg for _, msg in invalid_entries])
        messagebox.showerror("Error", error_msg)
        return

    # Generate SystemVerilog code
    code = ""
    for gen in generations:
        coverpoints = []
        for param in parameters:
            if inputs.get(param) is None and not check_vars[param].get():
                continue
            bins_count = bins_counts.get(param, default_bins)
            bins = []
            bin_counter = 1
            if check_vars[param].get():
                allowed = allowed_values[gen].get(param, [])
                for item_type, item in allowed:
                    if item_type == "range":
                        a, b = item
                        if b == float('inf'):
                            b = a + 1000
                        bins.append(f"    bins bin{bin_counter}[{bins_count}] = {{[{a}:{b}]}};")
                        bin_counter += 1
                    elif item_type == "value":
                        bins.append(f"    bins bin{bin_counter} = {{{item}}};")
                        bin_counter += 1
            else:
                for parsed in inputs.get(param, []):
                    if parsed["type"] == "range":
                        for min_val, max_val in parsed["ranges"]:
                            bins.append(f"    bins bin{bin_counter}[{bins_count}] = {{[{min_val}:{max_val}]}};")
                            bin_counter += 1
                    elif parsed["type"] == "list":
                        values = parsed["values"]
                        if len(values) == 1:
                            bins.append(f"    bins bin{bin_counter} = {{{values[0]}}};")
                        else:
                            bins.append(f"    bins bin{bin_counter}[] = {{{','.join(map(str, values))}}};")
                        bin_counter += 1
                    elif parsed["type"] == "mixed":
                        for min_val, max_val in parsed["ranges"]:
                            bins.append(f"    bins bin{bin_counter}[{bins_count}] = {{[{min_val}:{max_val}]}};")
                            bin_counter += 1
                        if parsed["values"]:
                            bins.append(f"    bins bin{bin_counter}[] = {{{','.join(map(str, parsed['values']))}}};")
                            bin_counter += 1
            if bins:
                coverpoint = f"  cov_{param}: coverpoint {param} {{\n" + "\n".join(bins) + "\n  };"
                coverpoints.append(coverpoint)

        if coverpoints:
            code += f"// {gen} covergroup\ncovergroup cg_{gen.replace(' ', '_')};\n" + "\n".join(coverpoints) + "\nendgroup\n"
            code += f"cg_{gen.replace(' ', '_')} u_cg_{gen.replace(' ', '_')} = new();\n\n"

    with open("coverage_model.sv", "w") as f:
        f.write(code)
    messagebox.showinfo("Success", "Generated coverage_model.sv")

# Generate button
generate_btn = ttk.Button(scrollable_frame, text="Generate Functional Coverage", command=validate_and_generate)
generate_btn.grid(row=len(parameters)+1, column=0, pady=10)

root.mainloop()