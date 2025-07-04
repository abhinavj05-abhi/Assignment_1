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
            b = int(b) if b not in ["$", "∞"] else float('inf') if b == "∞" else float('-inf')
            result.append(("range", (a, b)))
        else:
            try:
                value = int(part)
                result.append(("value", value))
            except ValueError:
                continue
    return result

# Parse user input (single range or list of values)
def parse_user_input(s):
    s = s.strip()
    if not s:
        return None
    if s.startswith("[") and s.endswith("]") and ":" in s:
        range_str = s[1:-1]
        try:
            a, b = map(int, range_str.split(":"))
            return {"type": "range", "range": (a, b)}
        except ValueError:
            return None
    else:
        try:
            values = [int(v.strip()) for v in s.split(",") if v.strip()]
            if values:
                return {"type": "list", "values": values}
            return None
        except ValueError:
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

# Get default bin name
def get_default_bin_name(parsed):
    if parsed["type"] == "range":
        a, b = parsed["range"]
        return f"v{a}_{b}"
    elif parsed["type"] == "list":
        values = parsed["values"]
        if len(values) == 1:
            return f"v{values[0]}"
        else:
            min_val = min(values)
            max_val = max(values)
            return f"v{min_val}_{max_val}"

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
        return f"[{min_val}:{max_val}]" if min_val != float('-inf') and max_val != float('inf') else "No valid range"
    elif values:
        return ",".join(map(str, sorted(values)))
    return "No valid data"

# Check if input is allowed
def is_input_allowed(parsed, allowed):
    if parsed["type"] == "range":
        min_val, max_val = parsed["range"]
        for item_type, item in allowed:
            if item_type == "range":
                a, b = item
                if a <= min_val and max_val <= b:
                    return True
        return False
    elif parsed["type"] == "list":
        values = parsed["values"]
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

scrollable_frame.bind("<Configure>", lambda e: 
    canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Add note about functionality
note_label = ttk.Label(scrollable_frame,
    text="Note: Tick checkbox for IEEE default values (disables input). Use '+' to add up to 10 input and bins fields. Bins field sets bin count for each input (default 1, ignored for single values).",
    wraplength=950, foreground="blue")
note_label.grid(row=0, column=0, columnspan=6, pady=10)

# GUI elements
param_frames = {}
entries = {}
bins_entries = {}
bin_name_entries = {}
check_vars = {}
error_labels = {}

def toggle_entry_state(param):
    state = "disabled" if check_vars[param].get() else "normal"
    input_frame = param_frames[param].grid_slaves(row=0, column=2)[0]
    for subframe in input_frame.winfo_children():
        for widget in subframe.winfo_children():
            if isinstance(widget, (ttk.Entry, ttk.Button)):
                widget.configure(state=state)
            elif isinstance(widget, ttk.Label) and "error" in widget.winfo_name():
                widget.configure(text="")

for i, param in enumerate(parameters):
    param_frame = ttk.Frame(scrollable_frame)
    param_frame.grid(row=i+1, column=0, sticky="w", padx=5, pady=5)
    param_frames[param] = param_frame

    check_vars[param] = tk.BooleanVar(value=False)
    checkbox = ttk.Checkbutton(param_frame, text="", variable=check_vars[param],
                               command=lambda p=param: toggle_entry_state(p))
    checkbox.grid(row=0, column=0, padx=5, pady=5)

    label = ttk.Label(param_frame, text=f"{param}:")
    label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    input_frame = ttk.Frame(param_frame)
    input_frame.grid(row=0, column=2, padx=5, pady=5)
    entries[param] = []
    bins_entries[param] = []
    bin_name_entries[param] = []
    error_labels[param] = []

    def add_input_field(frame, row):
        # Do not add new fields if default values checkbox is ticked
        if check_vars[param].get():
            return
        if row >= 10:  # Limit to 10 additions
            return
        subframe = ttk.Frame(frame)
        subframe.grid(row=row, column=0, sticky="w", pady=2)

        entry = ttk.Entry(subframe, width=20)
        entry.grid(row=0, column=0, padx=5, pady=5)
        entries[param].append(entry)

        bins_label = ttk.Label(subframe, text="Bins:")
        bins_label.grid(row=0, column=1, padx=5, pady=5)

        bins_entry = ttk.Entry(subframe, width=10)
        bins_entry.grid(row=0, column=2, padx=5, pady=5)
        bins_entries[param].append(bins_entry)

        bin_name_label = ttk.Label(subframe, text="Bin name:")
        bin_name_label.grid(row=0, column=3, padx=5, pady=5)

        bin_name_entry = ttk.Entry(subframe, width=15)
        bin_name_entry.grid(row=0, column=4, padx=5, pady=5)
        bin_name_entries[param].append(bin_name_entry)

        error_label = ttk.Label(subframe, text="", name=f"error_{param}_{row}", 
                                 foreground="red")
        error_label.grid(row=0, column=5, padx=5, pady=5)
        error_labels[param].append(error_label)

        plus_btn = ttk.Button(subframe, text="+",
                              command=lambda: add_input_field(frame, row + 1))
        plus_btn.grid(row=0, column=6, padx=5, pady=5)

    add_input_field(input_frame, 0)

def validate_and_generate():
    inputs = {}
    invalid_entries = []

    # Collect all inputs from GUI
    for param in parameters:
        if check_vars[param].get():
            inputs[param] = None  # Use default values if checkbox ticked
        else:
            param_inputs = []
            # Iterate over all input fields for this parameter
            for entry, bins_entry, bin_name_entry, error_label in zip(
                entries[param], bins_entries[param], bin_name_entries[param], error_labels[param]
            ):
                val = entry.get().strip()
                if val:  # Only process non-empty inputs
                    parsed = parse_user_input(val)
                    if parsed is None:
                        invalid_entries.append((entry, error_label, "Invalid format"))
                    else:
                        bins_val = parse_bins_input(bins_entry.get())
                        bin_count = bins_val if bins_val is not None else default_bins
                        bin_name = bin_name_entry.get().strip() or get_default_bin_name(parsed)
                        # Check allowed values across generations
                        allowed_anywhere = False
                        for gen in generations:
                            if is_input_allowed(parsed, allowed_values[gen].get(param, [])):
                                allowed_anywhere = True
                                break
                        if not allowed_anywhere:
                            valid_range = get_max_allowed_range(param, allowed_values)
                            invalid_entries.append((entry, error_label, f"Out of range. Allowed: {valid_range}"))
                        else:
                            param_inputs.append((parsed, bin_count, bin_name))
            # Only assign inputs if there are valid entries
            inputs[param] = param_inputs if param_inputs else None

    # Highlight invalid entries and stop if there are errors
    for entry, error_label, msg in invalid_entries:
        entry.configure(background="pink")
        error_label.configure(text=msg)
    if invalid_entries:
        return

    # Generate SystemVerilog code
    code = ""
    for gen in generations:
        coverpoints = []
        for param in parameters:
            bins = []

            # Case 1: Checkbox ticked, use default values from Excel
            if check_vars[param].get():
                allowed = allowed_values[gen].get(param, [])
                for item_type, item in allowed:
                    if item_type == "range":
                        a, b = item
                        b_str = "$" if b == float('inf') else str(b)
                        bin_name = f"v{a}_{b_str}"
                        bins.append(f"    bins {bin_name} = {{[{a}:{b_str}]}};")
                    elif item_type == "value":
                        bin_name = f"v{item}"
                        bins.append(f"    bins {bin_name} = {{{item}}};")

            # Case 2: User-provided inputs via '+' fields
            elif inputs.get(param):
                # Each item corresponds to one '+' field
                for parsed, bin_count, bin_name in inputs[param]:
                    if parsed["type"] == "range":
                        a, b = parsed["range"]
                        b_str = "$" if b == float('inf') else str(b)
                        if bin_count > 1:
                            bins.append(f"    bins {bin_name}[{bin_count}] = {{[{a}:{b_str}]}};")
                        else:
                            bins.append(f"    bins {bin_name} = {{[{a}:{b_str}]}};")
                    elif parsed["type"] == "list":
                        values = parsed["values"]
                        if len(values) == 1:
                            bins.append(f"    bins {bin_name} = {{{values[0]}}};")
                        else:
                            values_str = ','.join(map(str, values))
                            bins.append(f"    bins {bin_name}[] = {{{values_str}}};")

            # Only add coverpoint if there are bins
            if bins:
                coverpoint = f"  cov_{param}: coverpoint {param} {{\n" + "\n".join(bins) + "\n  };"
                coverpoints.append(coverpoint)

        # Add covergroup for the generation if any coverpoint exists
        if coverpoints:
            cg_name = gen.replace(' ', '_')
            code += f"// {gen} covergroup\ncovergroup cg_{cg_name};\n" + "\n".join(coverpoints) + "\nendgroup\n"
            code += f"cg_{cg_name} u_cg_{cg_name} = new();\n\n"


    with open("coverage_model.sv", "w") as f:
        f.write(code)
    messagebox.showinfo("Success", "Generated coverage_model.sv")

generate_btn = ttk.Button(scrollable_frame, text="Generate Functional Coverage",
                           command=validate_and_generate)
generate_btn.grid(row=len(parameters)+1, column=0, pady=20)

root.mainloop()
