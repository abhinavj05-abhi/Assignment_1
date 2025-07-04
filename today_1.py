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

# Create GUI
root = tk.Tk()
root.title("WiFi Functional Coverage Generator")
root.geometry("900x800")

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

# Add note about checkbox functionality
note_label = ttk.Label(scrollable_frame, 
    text="Note: If a parameter's checkbox is ticked, its IEEE default values will be used in the coverage model, and the input field will be disabled. Bins field specifies the number of bins for the coverpoint.",
    wraplength=850, foreground="blue")
note_label.grid(row=0, column=0, columnspan=5, pady=10)

# GUI elements
entries = {}
bins_entries = {}
labels = {}
tooltips = {}
checkboxes = {}
check_vars = {}

def toggle_entry_state(param):
    """Enable/disable entry fields based on checkbox state"""
    state = "disabled" if check_vars[param].get() else "normal"
    entries[param].configure(state=state)
    bins_entries[param].configure(state=state)

for i, param in enumerate(parameters):
    # Checkbox
    check_vars[param] = tk.BooleanVar(value=False)
    checkbox = ttk.Checkbutton(scrollable_frame, text="", variable=check_vars[param], 
                            command=lambda p=param: toggle_entry_state(p))
    checkbox.grid(row=i+1, column=0, padx=5, pady=5)
    checkboxes[param] = checkbox
    
    # Label
    label = ttk.Label(scrollable_frame, text=f"{param}:")
    label.grid(row=i+1, column=1, padx=5, pady=5, sticky="e")
    labels[param] = label
    
    # Entry for parameter value
    entry = ttk.Entry(scrollable_frame, width=20)
    entry.grid(row=i+1, column=2, padx=5, pady=5, sticky="w")
    entries[param] = entry
    
    # Entry for bins
    bins_entry = ttk.Entry(scrollable_frame, width=10)
    bins_entry.grid(row=i+1, column=3, padx=5, pady=5, sticky="w")
    bins_entries[param] = bins_entry
    
    # Tooltip
    tooltip = ttk.Label(scrollable_frame, text="", foreground="red")
    tooltip.grid(row=i+1, column=4, padx=5, pady=5, sticky="w")
    tooltips[param] = tooltip

def validate_and_generate():
    inputs = {}
    bins_counts = {}
    invalid_params = {}
    
    # Collect inputs and reset GUI styles
    for param, entry in entries.items():
        bins_entry = bins_entries[param]
        bins_val = parse_bins_input(bins_entry.get())
        if bins_val is not None:
            bins_counts[param] = bins_val
        
        if check_vars[param].get():
            # Use default values from Excel if checkbox is ticked
            inputs[param] = None
        else:
            val = entry.get().strip()
            if val:
                parsed = parse_user_input(val)
                if parsed is None:
                    invalid_params[param] = "Invalid format"
                else:
                    inputs[param] = parsed
        entry.configure(background="white")
        bins_entry.configure(background="white")
        labels[param].configure(foreground="black")
        tooltips[param].configure(text="")

    # Validate inputs for non-checked parameters
    for param, input_data in inputs.items():
        if input_data is None:  # Checkbox ticked, using default values
            continue
        allowed_anywhere = False
        for gen in generations:
            if is_input_allowed(input_data, allowed_values[gen].get(param, [])):
                allowed_anywhere = True
                break
        if not allowed_anywhere:
            invalid_params[param] = get_max_allowed_range(param, allowed_values)
    
    # Validate bins inputs
    for param, bins_val in bins_counts.items():
        if bins_val is None:
            invalid_params[param] = "Bins must be a positive integer"
    
    # Highlight invalid inputs
    if invalid_params:
        for param, msg in invalid_params.items():
            entries[param].configure(background="pink")
            bins_entries[param].configure(background="pink")
            labels[param].configure(foreground="red")
            tooltips[param].configure(text=msg)
        messagebox.showerror("Error", "Correct the highlighted fields.")
        return

    # Generate SystemVerilog code
    code = ""
    for gen in generations:
        coverpoints = []
        for param in parameters:
            if param not in inputs and not check_vars[param].get():
                continue  # Skip parameters with no input and not checked
            bins_count = bins_counts.get(param, None)
            bins_suffix = f"[{bins_count}]" if bins_count is not None else ""
            
            if check_vars[param].get():
                # Use default values from Excel
                allowed = allowed_values[gen].get(param, [])
                bins = []
                bin_counter = 1
                for item_type, item in allowed:
                    if item_type == "range":
                        a, b = item
                        if b == float('inf'):
                            b = a + 1000  # Reasonable upper bound for infinite ranges
                        bins.append(f"    bins bin{bin_counter}{bins_suffix} = {{[{a}:{b}]}};")
                        bin_counter += 1
                    elif item_type == "value":
                        bins.append(f"    bins bin{bin_counter}{bins_suffix} = {{{item}}};")
                        bin_counter += 1
                if bins:
                    coverpoint = f"  cov_{param}: coverpoint {param} {{\n" + "\n".join(bins) + "\n  };"
                    coverpoints.append(coverpoint)
            else:
                input_data = inputs.get(param)
                if not input_data or not is_input_allowed(input_data, allowed_values[gen].get(param, [])):
                    continue
                bins = []
                bin_counter = 1
                if input_data["type"] in ["range", "mixed"]:
                    allowed = allowed_values[gen].get(param, [])
                    for item_type, item in allowed:
                        if item_type == "range":
                            a, b = item
                            if b == float('inf'):
                                b = max([max_val for _, max_val in input_data.get("ranges", [(0, 0)])] + [a + 1000])
                            for min_val, max_val in input_data.get("ranges", []):
                                if a <= max_val and min_val <= b:
                                    intersect_min = max(a, min_val)
                                    intersect_max = min(b, max_val)
                                    bins.append(f"    bins bin{bin_counter}{bins_suffix} = {{[{intersect_min}:{intersect_max}]}};")
                                    bin_counter += 1
                    if input_data["type"] == "mixed" and input_data.get("values"):
                        bins.append(f"    bins bin{bin_counter}{bins_suffix} = {{{','.join(map(str, input_data['values']))}}};")
                        bin_counter += 1
                elif input_data["type"] == "list":
                    bins.append(f"    bins bin{bin_counter}{bins_suffix} = {{{','.join(map(str, input_data['values']))}}};")
                    bin_counter += 1
                if bins:
                    coverpoint = f"  cov_{param}: coverpoint {param} {{\n" + "\n".join(bins) + "\n  };"
                    coverpoints.append(coverpoint)

        if coverpoints:
            code += f"// {gen} covergroup\ncovergroup cg_{gen.replace(' ', '_')};\n" + "\n".join(coverpoints) + "\nendgroup\n"
            code += f"cg_{gen.replace(' ', '_')} u_cg_{gen.replace(' ', '_')} = new();\n\n"

    # Write to file
    with open("coverage_model.sv", "w") as f:
        f.write(code)
    messagebox.showinfo("Success", "Generated coverage_model.sv")

# Generate button
generate_btn = ttk.Button(scrollable_frame, text="Generate Functional Coverage", command=validate_and_generate)
generate_btn.grid(row=len(parameters)+1, column=0, columnspan=5, pady=10)

root.mainloop()