import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import math

# Parse allowed values from Excel cell strings
def parse_allowed_values(s):
    try:
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
    except Exception as e:
        print(f"Error parsing allowed values: {e}")
        return []

# Parse user input (single range or list of values)
def parse_user_input(s):
    try:
        s = s.strip()
        if not s:
            return None
        if s.startswith("[") and s.endswith("]") and ":" in s:
            range_str = s[1:-1]
            try:
                a, b = range_str.split(":")
                a = int(a) if a != "$" else float('-inf')
                b = int(b) if b not in ["$", "∞"] else float('inf') if b == "∞" else float('-inf')
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
    except Exception as e:
        print(f"Error parsing user input: {e}")
        return None

# Parse bins input - return None if empty or invalid
def parse_bins_input(s):
    try:
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
    except Exception as e:
        print(f"Error parsing bins input: {e}")
        return None

# Parse range input - return None if empty or invalid
def parse_range_input(s):
    try:
        s = s.strip()
        if not s:
            return None
        try:
            range_val = int(s)
            if range_val <= 0:
                return None
            return range_val
        except ValueError:
            return None
    except Exception as e:
        print(f"Error parsing range input: {e}")
        return None

# Generate automatic bins based on range division
def generate_automatic_bins(parsed_input, range_div, bin_name_prefix):
    try:
        if parsed_input["type"] != "range":
            return []
        
        min_val, max_val = parsed_input["range"]
        if min_val == float('-inf') or max_val == float('inf'):
            return []
        
        bins = []
        current = min_val
        bin_num = 1
        
        while current <= max_val:
            next_val = min(current + range_div - 1, max_val)
            bin_name = f"{bin_name_prefix}_r{bin_num}"
            bins.append({
                "cross_name": bin_name,
                "range": (current, next_val)
            })
            current = next_val + 1
            bin_num += 1
        
        return bins
    except Exception as e:
        print(f"Error generating automatic bins: {e}")
        return []

# Parse illegal bins input
def parse_illegal_bins(s):
    try:
        s = s.strip()
        if not s:
            return []
        # Split by semicolon to separate different illegal conditions
        conditions = [cond.strip() for cond in s.split(";") if cond.strip()]
        return conditions
    except Exception as e:
        print(f"Error parsing illegal bins: {e}")
        return []

# Get default bin cross_name
def get_default_bin_name(parsed):
    try:
        if parsed["type"] == "range":
            a, b = parsed["range"]
            a_str = str(a) if a != float('-inf') else "0"
            b_str = str(b) if b != float('inf') else "max"
            return f"v{a_str}_{b_str}"
        elif parsed["type"] == "list":
            values = parsed["values"]
            if len(values) == 1:
                return f"v{values[0]}"
            else:
                min_val = min(values)
                max_val = max(values)
                return f"v{min_val}_{max_val}"
    except Exception as e:
        print(f"Error getting default bin cross_name: {e}")
        return "default_bin"

# Get combined allowed range for a parameter (union of all ranges/values)
def get_combined_allowed_range(param, allowed_values):
    try:
        all_ranges = []
        all_values = []
        
        # Collect all ranges and values from all generations
        for gen in allowed_values:
            for item_type, item in allowed_values[gen].get(param, []):
                if item_type == "range":
                    all_ranges.append(item)
                elif item_type == "value":
                    all_values.append(item)
        
        # Find the overall min and max
        min_vals = []
        max_vals = []
        
        for a, b in all_ranges:
            if a != float('-inf'):
                min_vals.append(a)
            if b != float('inf'):
                max_vals.append(b)
        
        if all_values:
            min_vals.extend(all_values)
            max_vals.extend(all_values)
        
        if min_vals and max_vals:
            overall_min = min(min_vals)
            overall_max = max(max_vals)
            return overall_min, overall_max
        
        return None, None
    except Exception as e:
        print(f"Error getting combined allowed range: {e}")
        return None, None

# Get maximum allowed range or values for feedback display
def get_max_allowed_range(param, allowed_values):
    try:
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
    except Exception as e:
        print(f"Error getting max allowed range: {e}")
        return "Error getting range"

# Check if input is within the combined allowed range
def is_input_within_combined_range(parsed, param, allowed_values):
    try:
        overall_min, overall_max = get_combined_allowed_range(param, allowed_values)
        if overall_min is None or overall_max is None:
            return False
        
        if parsed["type"] == "range":
            min_val, max_val = parsed["range"]
            return overall_min <= min_val and max_val <= overall_max
        elif parsed["type"] == "list":
            values = parsed["values"]
            return all(overall_min <= v <= overall_max for v in values)
        
        return False
    except Exception as e:
        print(f"Error checking if input is within combined range: {e}")
        return False

# Check if input is allowed for a specific generation
def is_input_allowed_for_generation(parsed, allowed):
    try:
        if parsed["type"] == "range":
            min_val, max_val = parsed["range"]
            for item_type, item in allowed:
                if item_type == "range":
                    a, b = item
                    if a <= min_val and max_val <= b:
                        return True
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
        
        return False
    except Exception as e:
        print(f"Error checking if input is allowed for generation: {e}")
        return False

def generate_systemverilog_bins(parsed, bins_count, range_div, bin_name, param):
    try:
        if parsed["type"] == "range":
            min_val, max_val = parsed["range"]
            if range_div is not None:
                bins = generate_automatic_bins(parsed, range_div, bin_name)
                bin_code = "\n".join(f"        bins {bin['cross_name']} = {{[{bin['range'][0]}:{bin['range'][1]}]}};" for bin in bins)
                return bin_code
            elif bins_count is not None:
                bin_size = (max_val - min_val + 1) // bins_count
                bins = []
                current = min_val
                for i in range(bins_count):
                    next_val = min(current + bin_size - 1, max_val)
                    bin_name_i = f"{bin_name}_b{i+1}"
                    bins.append(f"        bins {bin_name_i} = {{[{current}:{next_val}]}};")
                    current = next_val + 1
                bin_code = "\n".join(bins)
                return bin_code
            else:
                return f"        bins {bin_name} = {{[{min_val}:{max_val}]}};"
        elif parsed["type"] == "list":
            values = parsed["values"]
            return "\n".join(f"        bins {bin_name}_v{v} = {{{v}}};" for v in values)
    except Exception as e:
        print(f"Error generating SystemVerilog bins: {e}")
        return ""

# Generate cross coverage code
def generate_cross_coverage_code(cross_name, coverpoints, illegal_bins):
    try:
        coverpoint_code = f"    {cross_name}: cross {','.join(coverpoints)};\n"
        if illegal_bins:
            illegal_code = "\n".join(f"        illegal_bins ({illegal_bin});" for illegal_bin in illegal_bins)
            return coverpoint_code + illegal_code
        else:
            return coverpoint_code
    except Exception as e:
        print(f"Error generating cross coverage code: {e}")
        return ""

# Generate module definition
def generate_module_definition(parameters, generations, allowed_values):
    try:
        module_definition = "module rxpktgen_fcov;\n"
        module_definition += "// Variables\n"

        for param in parameters:
            module_definition += f"integer {param.lower()};\n"
        module_definition += "\n// Events\n"

        for gen in generations:
            module_definition += f"event trigger_{gen.lower()}_cov;\n"
        module_definition += "\n// Coverage Groups\n"

        for gen in generations:
            covergroup_name = f"cg_{gen.lower()}"
            module_definition += f"covergroup {covergroup_name} @(posedge clk);\n"

            for param in parameters:
                if param in allowed_values[gen]:
                    coverpoint_name = f"cov_{param.lower()}"
                    module_definition += f"    {coverpoint_name}: coverpoint {param.lower()} {{\n"
                    
                    # Generate bins from allowed values
                    for item_type, item in allowed_values[gen][param]:
                        if item_type == "range":
                            min_val, max_val = item
                            min_str = str(min_val) if min_val != float('-inf') else "0"
                            max_str = str(max_val) if max_val != float('inf') else "999999"

                            # Use default bins if available 
                            if default_bins[param] is not None and default_bins[param] > 1:
                                module_definition += f"        bins {param.lower()}_default[{default_bins[param]}] = {{[{min_str}:{max_str}]}};\n"
                            else:
                                module_definition += f"        bins {param.lower()}_default = {{[{min_str}:{max_str}]}};\n"
                        elif item_type == "value":
                            module_definition += f"        bins {param.lower()}_v{item} = {{{item}}};\n"
                    
                    module_definition += "    }\n"

            module_definition += "endgroup\n\n"
        module_definition += "endmodule\n"
        return module_definition
    except Exception as e:
        print(f"Error generating module definition: {e}")
        return ""

# Check if Excel file exists
excel_file = "data_fc_2.xlsx"
if not os.path.exists(excel_file):
    print(f"Error: Excel file '{excel_file}' not found in current directory.")
    print(f"Current directory: {os.getcwd()}")
    print("Please make sure the Excel file is in the same directory as this script.")
    sys.exit(1)

# Read Excel file with better error handling
try:
    df = pd.read_excel(excel_file, sheet_name="Sheet1", engine='openpyxl')
    print(f"Successfully loaded Excel file: {excel_file}")
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
except FileNotFoundError:
    print(f"Error: Excel file '{excel_file}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("Please check if the file is corrupted or in use by another application.")
    sys.exit(1)

# Validate DataFrame structure
if df.empty:
    print("Error: Excel file is empty.")
    sys.exit(1)

if "Parameters" not in df.columns:
    print("Error: 'Parameters' column not found in Excel file.")
    print(f"Available columns: {df.columns.tolist()}")
    sys.exit(1)

if len(df.columns) < 3:
    print("Error: Excel file must have at least 3 columns (Parameters, Bins, and at least one covergroup).")
    sys.exit(1)

try:
    parameters = df["Parameters"].dropna().tolist()  # Remove NaN values
    if not parameters:
        print("Error: No valid parameters found in 'Parameters' column.")
        sys.exit(1)
    
    # Second column is bins
    bins_column = df.columns[1]
    print(f"Bins column: {bins_column}")
    
    # Functional coverage covergroups start from column 3
    generations = [col for col in df.columns[2:]]  # Skip Parameters and Bins columns
    if not generations:
        print("Error: No generation columns found (should start from column 3).")
        sys.exit(1)
    
    print(f"Found {len(parameters)} parameters and {len(generations)} generations")
    print(f"Parameters: {parameters}")
    print(f"Generations: {generations}")
    
except Exception as e:
    print(f"Error processing DataFrame: {e}")
    sys.exit(1)

# Parse allowed values and default bins with better error handling
try:
    allowed_values = {}
    default_bins = {}
    
    # Parse default bins from column 2
    for param in parameters:
        try:
            param_rows = df[df["Parameters"] == param]
            if param_rows.empty:
                print(f"Warning: Parameter '{param}' not found in DataFrame")
                default_bins[param] = None
                continue
            
            bins_value = param_rows[bins_column].iloc[0]
            if pd.isna(bins_value):
                default_bins[param] = None
            else:
                try:
                    default_bins[param] = int(bins_value)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid bins value for parameter '{param}': {bins_value}. Using default value None.")
                    default_bins[param] = None
        except Exception as e:
            print(f"Error parsing default bins for parameter '{param}': {e}")
            default_bins[param] = None
    
    # Parse allowed values from generation columns
    for gen in generations:
        allowed_values[gen] = {}
        for param in parameters:
            try:
                param_rows = df[df["Parameters"] == param]
                if param_rows.empty:
                    print(f"Warning: Parameter '{param}' not found in DataFrame")
                    allowed_values[gen][param] = []
                    continue
                
                cell_value = param_rows[gen].iloc[0]
                parsed_values = parse_allowed_values(cell_value)
                allowed_values[gen][param] = parsed_values
                
            except Exception as e:
                print(f"Error parsing values for parameter '{param}', generation '{gen}': {e}")
                allowed_values[gen][param] = []
    
    print("Successfully parsed allowed values and default bins")
    print(f"Default bins: {default_bins}")
    
except Exception as e:
    print(f"Error creating allowed_values dictionary: {e}")
    sys.exit(1)

# Replace the GUI creation section in your code with this improved version:

# Create GUI with error handling
try:
    root = tk.Tk()
    root.title("WiFi Functional Coverage Generator - Enhanced with Range Parameter")
    root.geometry("1800x1200")
    
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
        text="Enhanced Note: Tick checkbox for default values from Excel. Use '+' to add up to 10 input fields. NEW: Range field automatically divides a range into equal bins. Example: Input=[1:50000], Range=1000 creates bins [1:1000], [1001:2000], etc. Leave Range empty for manual binning. For specific values (like 10,50), use separate input fields with empty Range.",
        wraplength=1750, foreground="blue", font=("Arial", 10))
    note_label.grid(row=0, column=0, columnspan=12, pady=10, sticky="w")

    # GUI elements
    param_frames = {}
    entries = {}
    bins_entries = {}
    range_entries = {}
    bin_name_entries = {}
    check_vars = {}
    error_labels = {}
    
    # Cross coverage variables
    cross_coverage_frames = {}
    cross_coverage_entries = {}
    cross_coverage_illegal_entries = {}

    def toggle_entry_state(param):
        try:
            state = "disabled" if check_vars[param].get() else "normal"
            input_frame = param_frames[param].grid_slaves(row=0, column=2)[0]
            for widget in input_frame.winfo_children():
                if isinstance(widget, (ttk.Entry, ttk.Button)):
                    widget.configure(state=state)
                elif isinstance(widget, ttk.Label) and "error" in widget.winfo_name():
                    widget.configure(text="")
        except Exception as e:
            print(f"Error toggling entry state for {param}: {e}")

    current_row = 1
    
    # Configure grid weights for proper alignment
    scrollable_frame.grid_columnconfigure(0, weight=1)
    
    for i, param in enumerate(parameters):
        try:
            # Create main parameter frame
            param_frame = ttk.Frame(scrollable_frame)
            param_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=2)
            param_frame.grid_columnconfigure(2, weight=1)  # Make input column expandable
            param_frames[param] = param_frame

            # Checkbox - fixed width
            check_vars[param] = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(param_frame, text="", variable=check_vars[param],
                                       command=lambda p=param: toggle_entry_state(p))
            checkbox.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")

            # Parameter label with FIXED WIDTH for alignment
            default_bins_display = default_bins[param] if default_bins[param] is not None else "auto"
            label_text = f"{param} (default bins: {default_bins_display}):"
            label = ttk.Label(param_frame, text=label_text, font=("Arial", 10,), width=35, anchor="w")
            label.grid(row=0, column=1, padx=(0, 20), pady=2, sticky="w")

            # Input fields frame - this will contain all the aligned input elements
            input_frame = ttk.Frame(param_frame)
            input_frame.grid(row=0, column=2, sticky="ew", padx=0, pady=2)
            
            # Configure input_frame columns for consistent alignment
            input_frame.grid_columnconfigure(0, minsize=160)  # Input column
            input_frame.grid_columnconfigure(1, minsize=80)   # Bins column
            input_frame.grid_columnconfigure(2, minsize=80)   # Range column
            input_frame.grid_columnconfigure(3, minsize=120)  # Bin Name column
            input_frame.grid_columnconfigure(4, minsize=150)  # Error column
            input_frame.grid_columnconfigure(5, minsize=40)   # Plus button column
            
            entries[param] = []
            bins_entries[param] = []
            range_entries[param] = []
            bin_name_entries[param] = []
            error_labels[param] = []

            def add_input_field(frame, row, param=param):
                try:
                    if row >= 10:  # Limit to 10 additions
                        return
                    
                    if row == 0:
                        # Add header labels at row=0 with consistent spacing
                        header_frame = ttk.Frame(frame)
                        header_frame.grid(row=0, column=0, columnspan=6, sticky="ew", pady=(0, 5))
                        
                        # Configure header frame columns to match input columns
                        header_frame.grid_columnconfigure(0, minsize=160)
                        header_frame.grid_columnconfigure(1, minsize=80)
                        header_frame.grid_columnconfigure(2, minsize=80)
                        header_frame.grid_columnconfigure(3, minsize=120)
                        header_frame.grid_columnconfigure(4, minsize=150)
                        header_frame.grid_columnconfigure(5, minsize=40)
                        


# To:
                        ttk.Label(header_frame, text="Input", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Bins", font=("Arial", 9)).grid(row=0, column=1, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Range", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Bin Name", font=("Arial", 9)).grid(row=0, column=3, sticky="w", padx=2)
                        ttk.Label(header_frame, text="", font=("Arial", 9)).grid(row=0, column=4, sticky="w", padx=2)  # Remove "Error" text
                    
                    # Add input fields at row=row+1
                    input_row = row + 1
                    
                    # Input field
                    entry = ttk.Entry(frame, width=20)
                    entry.grid(row=input_row, column=0, sticky="ew", padx=2, pady=1)
                    entries[param].append(entry)
                    
                    # Bins field
                    bins_entry = ttk.Entry(frame, width=8)
                    if default_bins[param] is not None:
                        bins_entry.insert(0, str(default_bins[param]))
                    bins_entry.grid(row=input_row, column=1, sticky="ew", padx=2, pady=1)
                    bins_entries[param].append(bins_entry)
                    
                    # Range field
                    range_entry = ttk.Entry(frame, width=8)
                    range_entry.grid(row=input_row, column=2, sticky="ew", padx=2, pady=1)
                    range_entries[param].append(range_entry)
                    
                    # Bin Name field
                    bin_name_entry = ttk.Entry(frame, width=12)
                    bin_name_entry.grid(row=input_row, column=3, sticky="ew", padx=2, pady=1)
                    bin_name_entries[param].append(bin_name_entry)
                    
                    # Error label
                    error_label = ttk.Label(frame, text="", name=f"error_{param}_{row}", 
                                            foreground="red", font=("Arial", 8), width=18)
                    error_label.grid(row=input_row, column=4, sticky="w", padx=2, pady=1)
                    error_labels[param].append(error_label)
                    
                    # Plus button
                    if row < 9:  # Only show + button if not at max
                        plus_btn = ttk.Button(frame, text="+", width=3,
                                              command=lambda: add_input_field(frame, row + 1, param))
                        plus_btn.grid(row=input_row, column=5, sticky="w", padx=2, pady=1)
                        
                except Exception as e:
                    print(f"Error adding input field for {param}: {e}")

            add_input_field(input_frame, 0, param)
            current_row += 1
        
        except Exception as e:
            print(f"Error creating GUI elements for parameter {param}: {e}")

    # Add separator 
    separator = ttk.Separator(scrollable_frame, orient='horizontal')
    separator.grid(row=current_row, column=0, columnspan=12, sticky="ew", pady=10)
    current_row += 1

    # WiFi specification frame
    wifi_specs_frame = ttk.LabelFrame(scrollable_frame, text="WiFi Specification", padding="10")
    wifi_specs_frame.grid(row=current_row, column=0, columnspan=12, sticky="ew", padx=5, pady=10)
    current_row += 1

    wifi_specs_vars = {}
    wifi_specs = ["11ax SU", "11ax SU_MU", "11ac", "11n"]

    for i, spec in enumerate(wifi_specs):
        var = tk.BooleanVar(value=False)
        checkbox = ttk.Checkbutton(wifi_specs_frame, text=spec, variable=var)
        checkbox.grid(row=0, column=i, padx=5, pady=5)
        wifi_specs_vars[spec] = var

    # Cross Coverage Section
    cross_coverage_title = ttk.Label(scrollable_frame, text="Cross Coverage Configuration", font=("Arial", 12, "bold"))
    cross_coverage_title.grid(row=current_row, column=0, columnspan=12, pady=10, sticky="w")
    current_row += 1

    # Cross coverage help text
    cross_help_text = ttk.Label(scrollable_frame, 
        text="Cross Coverage Help: Enter coverpoints as 'cov_param1,cov_param2'. For illegal bins, use format: 'cov_param1.bin_name,cov_param2.bin_name; cov_param1.bin2,cov_param2.bin2'. Auto-generated range bins use format: 'cov_param.param_r1,cov_param.param_r2' etc.",
        wraplength=1750, foreground="gray", font=("Arial", 9))
    cross_help_text.grid(row=current_row, column=0, columnspan=12, pady=5, sticky="w")
    current_row += 1

    # Create cross coverage frames for each generation
    for gen in generations:
        try:
            gen_frame = ttk.LabelFrame(scrollable_frame, text=f"Cross Coverage for {gen}", padding="10")
            gen_frame.grid(row=current_row, column=0, columnspan=12, sticky="ew", padx=5, pady=5)
            
            cross_coverage_frames[gen] = gen_frame
            cross_coverage_entries[gen] = []
            cross_coverage_illegal_entries[gen] = []

            def add_cross_coverage_field(frame, row, gen=gen):
                try:
                    if row >= 10:  # Limit to 10 cross coverages
                        return
                    
                    subframe = ttk.Frame(frame)
                    subframe.grid(row=row, column=0, sticky="ew", pady=2)
                    
                    # Configure subframe columns for consistent alignment
                    subframe.grid_columnconfigure(1, minsize=200)  # Cross name
                    subframe.grid_columnconfigure(3, minsize=300)  # Coverpoints
                    subframe.grid_columnconfigure(5, minsize=400)  # Illegal bins

                    # Cross coverage name
                    name_label = ttk.Label(subframe, text="Cross Name:", font=("Arial", 9))
                    name_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

                    name_entry = ttk.Entry(subframe, width=25)
                    name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

                    # Coverpoints selection
                    coverpoints_label = ttk.Label(subframe, text="Coverpoints:", font=("Arial", 9))
                    coverpoints_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")

                    coverpoints_entry = ttk.Entry(subframe, width=40)
                    coverpoints_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

                    # Illegal bins
                    illegal_label = ttk.Label(subframe, text="Illegal bins:", font=("Arial", 9 ))
                    illegal_label.grid(row=0, column=4, padx=5, pady=2, sticky="w")

                    illegal_entry = ttk.Entry(subframe, width=50)
                    illegal_entry.grid(row=0, column=5, padx=5, pady=2, sticky="ew")

                    # Plus button
                    if row < 9:
                        plus_btn = ttk.Button(subframe, text="+", width=3,
                                              command=lambda: add_cross_coverage_field(frame, row + 1, gen))
                        plus_btn.grid(row=0, column=6, padx=5, pady=2, sticky="w")

                    # Store entries
                    cross_coverage_entries[gen].append((name_entry, coverpoints_entry))
                    cross_coverage_illegal_entries[gen].append(illegal_entry)

                except Exception as e:
                    print(f"Error adding cross coverage field for {gen}: {e}")

            add_cross_coverage_field(gen_frame, 0, gen)
            current_row += 1

        except Exception as e:
            print(f"Error creating cross coverage frame for generation {gen}: {e}")

    # Generate button
    def generate_code():
        try:
            all_results = {}
            
            for gen in generations:
                result = f"// Generation: {gen}\n"
                result += f"covergroup cg_{gen.lower()} @(posedge clk);\n"
                
                # Process parameters
                for param in parameters:
                    if check_vars[param].get():
                        # Use default values from Excel
                        if param in allowed_values[gen] and allowed_values[gen][param]:
                            result += f"    cov_{param.lower()}: coverpoint {param.lower()} {{\n"
                            
                            # Generate bins from allowed values
                            for item_type, item in allowed_values[gen][param]:
                                if item_type == "range":
                                    min_val, max_val = item
                                    min_str = str(min_val) if min_val != float('-inf') else "0"
                                    max_str = str(max_val) if max_val != float('inf') else "999999"
                                    
                                    if default_bins[param] is not None and default_bins[param] > 1:
                                        result += f"        bins {param.lower()}_default[{default_bins[param]}] = {{[{min_str}:{max_str}]}};\n"
                                    else:
                                        result += f"        bins {param.lower()}_default = {{[{min_str}:{max_str}]}};\n"
                                elif item_type == "value":
                                    result += f"        bins {param.lower()}_v{item} = {{{item}}};\n"
                            
                            result += "    }\n"
                    else:
                        # Use user-defined values
                        has_valid_input = False
                        result += f"    cov_{param.lower()}: coverpoint {param.lower()} {{\n"
                        
                        # Clear previous error messages
                        for error_label in error_labels[param]:
                            error_label.config(text="")
                        
                        for i, entry in enumerate(entries[param]):
                            user_input = entry.get().strip()
                            if user_input:
                                parsed = parse_user_input(user_input)
                                if parsed is None:
                                    error_labels[param][i].config(text="Invalid input format")
                                    continue
                                
                                # Check if input is within allowed range
                                if not is_input_within_combined_range(parsed, param, allowed_values):
                                    max_range = get_max_allowed_range(param, allowed_values)
                                    error_labels[param][i].config(text=f"Out of range: {max_range}")
                                    continue
                                
                                # Get bin name
                                bin_name = bin_name_entries[param][i].get().strip()
                                if not bin_name:
                                    bin_name = get_default_bin_name(parsed)
                                
                                # Get bins and range
                                bins_input = bins_entries[param][i].get().strip()
                                range_input = range_entries[param][i].get().strip()
                                
                                bins_count = parse_bins_input(bins_input)
                                range_div = parse_range_input(range_input)
                                
                                # Generate SystemVerilog code
                                bin_code = generate_systemverilog_bins(parsed, bins_count, range_div, bin_name, param)
                                if bin_code:
                                    result += bin_code + "\n"
                                    has_valid_input = True
                                    error_labels[param][i].config(text="OK", foreground="green")
                                else:
                                    error_labels[param][i].config(text="Code generation failed")
                        
                        if not has_valid_input:
                            result += f"        // No valid input for {param}\n"
                        
                        result += "    }\n"
                
                # Add cross coverage
                for name_entry, coverpoints_entry in cross_coverage_entries[gen]:
                    cross_name = name_entry.get().strip()
                    coverpoints = coverpoints_entry.get().strip()
                    
                    if cross_name and coverpoints:
                        coverpoints_list = [cp.strip() for cp in coverpoints.split(",")]
                        
                        # Find corresponding illegal bins entry
                        idx = cross_coverage_entries[gen].index((name_entry, coverpoints_entry))
                        illegal_bins_str = cross_coverage_illegal_entries[gen][idx].get().strip()
                        illegal_bins = parse_illegal_bins(illegal_bins_str)
                        
                        cross_code = generate_cross_coverage_code(cross_name, coverpoints_list, illegal_bins)
                        result += cross_code
                
                result += "endgroup\n\n"
                all_results[gen] = result
            
            # Create output window
            output_window = tk.Toplevel(root)
            output_window.title("Generated SystemVerilog Code")
            output_window.geometry("1200x800")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(output_window)
            notebook.pack(fill="both", expand=True)
            
            # Add tabs for each generation
            for gen in generations:
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=gen)
                
                text_widget = tk.Text(frame, wrap="none", font=("Courier", 10))
                text_widget.pack(fill="both", expand=True)
                text_widget.insert("1.0", all_results[gen])
                
                # Add scrollbars
                h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=text_widget.xview)
                h_scrollbar.pack(side="bottom", fill="x")
                text_widget.config(xscrollcommand=h_scrollbar.set)
                
                v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
                v_scrollbar.pack(side="right", fill="y")
                text_widget.config(yscrollcommand=v_scrollbar.set)
            
            # Add WiFi specs tab if any selected
            selected_specs = [spec for spec, var in wifi_specs_vars.items() if var.get()]
            if selected_specs:
                frame = ttk.Frame(notebook)
                notebook.add(frame, text="WiFi Specs")
                
                text_widget = tk.Text(frame, wrap="none", font=("Courier", 10))
                text_widget.pack(fill="both", expand=True)
                
                wifi_code = f"// Selected WiFi Specifications: {', '.join(selected_specs)}\n"
                wifi_code += "// Add your WiFi-specific coverage code here\n"
                text_widget.insert("1.0", wifi_code)
                
                # Add scrollbars
                h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=text_widget.xview)
                h_scrollbar.pack(side="bottom", fill="x")
                text_widget.config(xscrollcommand=h_scrollbar.set)
                
                v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
                v_scrollbar.pack(side="right", fill="y")
                text_widget.config(yscrollcommand=v_scrollbar.set)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating code: {e}")
            print(f"Detailed error: {e}")

    # Add generate button
    generate_btn = ttk.Button(scrollable_frame, text="Generate SystemVerilog Code", 
                              command=generate_code, style="Accent.TButton")
    generate_btn.grid(row=current_row, column=0, columnspan=12, pady=20)
    current_row += 1

    # Add help section
    help_frame = ttk.LabelFrame(scrollable_frame, text="Help", padding="10")
    help_frame.grid(row=current_row, column=0, columnspan=12, sticky="ew", padx=5, pady=10)
    
    help_text = """
Input Format Examples:
• Single range: [1:100]
• Multiple values: 10,20,30,40
• Mixed: Not supported in single field

Bins: Number of bins to create from range (leave empty for single bin)
Range: Divide range into equal parts (e.g., 1000 divides [1:50000] into 50 bins of 1000 each)
Bin Name: Custom name for the bin (auto-generated if empty)

Cross Coverage:
• Coverpoints: cov_param1,cov_param2
• Illegal bins: cov_param1.bin_name,cov_param2.bin_name
"""
    
    help_label = ttk.Label(help_frame, text=help_text, font=("Arial", 9), justify="left")
    help_label.pack(anchor="w")

    # Configure scrollable area
    scrollable_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    print("GUI created successfully")
    
except Exception as e:
    print(f"Error creating GUI: {e}")
    messagebox.showerror("GUI Error", f"Error creating GUI: {e}")
    sys.exit(1)

# Start GUI
if __name__ == "__main__":
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running GUI: {e}")
        messagebox.showerror("Runtime Error", f"Error running GUI: {e}")
        sys.exit(1)