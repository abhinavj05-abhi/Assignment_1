import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import math

# Add error handling for missing dependencies
try:
    import pandas as pd
except ImportError:
    print("Error: pandas is not installed. Please install it using: pip install pandas")
    sys.exit(1)

try:
    import openpyxl
except ImportError:
    print("Error: openpyxl is not installed. Please install it using: pip install openpyxl")
    sys.exit(1)

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
                "name": bin_name,
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

# Get default bin name
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
        print(f"Error getting default bin name: {e}")
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

# Create GUI with error handling
try:
    root = tk.Tk()
    root.title("WiFi Functional Coverage Generator - Enhanced with Range Parameter")
    root.geometry("1600x1200")
    
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
        wraplength=1550, foreground="blue", font=("Arial", 10))
    note_label.grid(row=0, column=0, columnspan=8, pady=10)

    # GUI elements
    param_frames = {}
    entries = {}
    bins_entries = {}
    range_entries = {}  # New: Range entries
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
            for subframe in input_frame.winfo_children():
                for widget in subframe.winfo_children():
                    if isinstance(widget, (ttk.Entry, ttk.Button)):
                        widget.configure(state=state)
                    elif isinstance(widget, ttk.Label) and "error" in widget.winfo_name():
                        widget.configure(text="")
        except Exception as e:
            print(f"Error toggling entry state for {param}: {e}")

    current_row = 1
    
    for i, param in enumerate(parameters):
        try:
            param_frame = ttk.Frame(scrollable_frame)
            param_frame.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
            param_frames[param] = param_frame

            check_vars[param] = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(param_frame, text="", variable=check_vars[param],
                                       command=lambda p=param: toggle_entry_state(p))
            checkbox.grid(row=0, column=0, padx=5, pady=5)

            # Modified label to show default bins or "auto" if None
            default_bins_display = default_bins[param] if default_bins[param] is not None else "auto"
            label = ttk.Label(param_frame, text=f"{param} (default bins: {default_bins_display}):")
            label.grid(row=0, column=1, padx=5, pady=5, sticky="e")

            input_frame = ttk.Frame(param_frame)
            input_frame.grid(row=0, column=2, padx=5, pady=5)
            entries[param] = []
            bins_entries[param] = []
            range_entries[param] = []  # New: Range entries list
            bin_name_entries[param] = []
            error_labels[param] = []

            def add_input_field(frame, row, param=param):
                try:
                    if row >= 10:  # Limit to 10 additions
                        return
                    subframe = ttk.Frame(frame)
                    subframe.grid(row=row, column=0, sticky="w", pady=2)

                    # Input field
                    input_label = ttk.Label(subframe, text="Input:")
                    input_label.grid(row=0, column=0, padx=5, pady=5)
                    
                    entry = ttk.Entry(subframe, width=20)
                    entry.grid(row=0, column=1, padx=5, pady=5)
                    entries[param].append(entry)

                    # Bins field
                    bins_label = ttk.Label(subframe, text="Bins:")
                    bins_label.grid(row=0, column=2, padx=5, pady=5)

                    bins_entry = ttk.Entry(subframe, width=10)
                    # Set default bins from Excel only if it's not None
                    if default_bins[param] is not None:
                        bins_entry.insert(0, str(default_bins[param]))
                    bins_entry.grid(row=0, column=3, padx=5, pady=5)
                    bins_entries[param].append(bins_entry)

                    # NEW: Range field
                    range_label = ttk.Label(subframe, text="Range:")
                    range_label.grid(row=0, column=4, padx=5, pady=5)

                    range_entry = ttk.Entry(subframe, width=10)
                    range_entry.grid(row=0, column=5, padx=5, pady=5)
                    range_entries[param].append(range_entry)

                    # Bin name field
                    bin_name_label = ttk.Label(subframe, text="Bin name:")
                    bin_name_label.grid(row=0, column=6, padx=5, pady=5)

                    bin_name_entry = ttk.Entry(subframe, width=15)
                    bin_name_entry.grid(row=0, column=7, padx=5, pady=5)
                    bin_name_entries[param].append(bin_name_entry)

                    # Error label
                    error_label = ttk.Label(subframe, text="", name=f"error_{param}_{row}", foreground="red")
                    error_label.grid(row=0, column=8, padx=5, pady=5)
                    error_labels[param].append(error_label)

                    # Plus button
                    if row < 9:  # Only show + button if not at max
                        plus_btn = ttk.Button(subframe, text="+",
                                              command=lambda: add_input_field(frame, row + 1, param))
                        plus_btn.grid(row=0, column=9, padx=5, pady=5)
                        
                    # Add help text for the first row
                    if row == 0:
                        help_text = ttk.Label(subframe, 
                            text="Input: Range [1:50000] or values 10,50 | Bins: Number of bins (optional) | Range: Auto-divide range (e.g., 1000) | Bin name: Custom name",
                            font=("Arial", 8), foreground="gray")
                        help_text.grid(row=1, column=0, columnspan=10, sticky="w", padx=5)
                        
                except Exception as e:
                    print(f"Error adding input field for {param}: {e}")

            add_input_field(input_frame, 0, param)
            current_row += 1
            
        except Exception as e:
            print(f"Error creating GUI elements for parameter {param}: {e}")

    # Add separator
    separator = ttk.Separator(scrollable_frame, orient='horizontal')
    separator.grid(row=current_row, column=0, columnspan=8, sticky="ew", pady=10)
    current_row += 1

    # Cross Coverage Section
    cross_coverage_title = ttk.Label(scrollable_frame, text="Cross Coverage Configuration", font=("Arial", 12, "bold"))
    cross_coverage_title.grid(row=current_row, column=0, columnspan=8, pady=10)
    current_row += 1

    # Cross coverage help text
    cross_help_text = ttk.Label(scrollable_frame, 
        text="Cross Coverage Help: Enter coverpoints as 'cov_param1,cov_param2'. For illegal bins, use format: 'cov_param1.bin_name,cov_param2.bin_name; cov_param1.bin2,cov_param2.bin2'. Auto-generated range bins use format: 'cov_param.param_r1,cov_param.param_r2' etc.",
        wraplength=1550, foreground="gray", font=("Arial", 9))
    cross_help_text.grid(row=current_row, column=0, columnspan=8, pady=5)
    current_row += 1

    # Create cross coverage frames for each generation
    for gen in generations:
        try:
            gen_frame = ttk.LabelFrame(scrollable_frame, text=f"Cross Coverage for {gen}", padding="10")
            gen_frame.grid(row=current_row, column=0, columnspan=8, sticky="ew", padx=5, pady=5)
            
            cross_coverage_frames[gen] = gen_frame
            cross_coverage_entries[gen] = []
            cross_coverage_illegal_entries[gen] = []

            def add_cross_coverage_field(frame, row, gen=gen):
                try:
                    if row >= 10:  # Limit to 10 cross coverages
                        return
                    
                    subframe = ttk.Frame(frame)
                    subframe.grid(row=row, column=0, sticky="w", pady=2)

                    # Cross coverage name
                    name_label = ttk.Label(subframe, text="Cross name:")
                    name_label.grid(row=0, column=0, padx=5, pady=5)

                    name_entry = ttk.Entry(subframe, width=25)
                    name_entry.grid(row=0, column=1, padx=5, pady=5)

                    # Coverpoints selection
                    coverpoints_label = ttk.Label(subframe, text="Coverpoints:")
                    coverpoints_label.grid(row=0, column=2, padx=5, pady=5)

                    coverpoints_entry = ttk.Entry(subframe, width=40)
                    coverpoints_entry.grid(row=0, column=3, padx=5, pady=5)

                    # Illegal bins
                    illegal_label = ttk.Label(subframe, text="Illegal bins:")
                    illegal_label.grid(row=0, column=4, padx=5, pady=5)

                    illegal_entry = ttk.Entry(subframe, width=50)
                    illegal_entry.grid(row=0, column=5, padx=5, pady=5)

                    # Store entries
                    cross_coverage_entries[gen].append((name_entry, coverpoints_entry))
                    cross_coverage_illegal_entries[gen].append(illegal_entry)

                    # Add help text
                    help_text = ttk.Label(subframe, 
                        text="Example: Name='rtt_cbw_cross' | Coverpoints='cov_rtt,cov_cbw' | Illegal='cov_rtt.v1_10,cov_cbw.v20_40; cov_rtt.rtt_r1,cov_cbw.cbw_r3' (for auto-range bins)",
                        font=("Arial", 8), foreground="gray")
                    help_text.grid(row=1, column=0, columnspan=6, sticky="w", padx=5)

                    if row < 9:  # Only show + button if not at max
                        plus_btn = ttk.Button(subframe, text="+",
                                              command=lambda: add_cross_coverage_field(frame, row + 1, gen))
                        plus_btn.grid(row=0, column=6, padx=5, pady=5)
                except Exception as e:
                    print(f"Error adding cross coverage field for {gen}: {e}")

            add_cross_coverage_field(gen_frame, 0, gen)
            current_row += 1
            
        except Exception as e:
            print(f"Error creating cross coverage section for {gen}: {e}")

    # Add separator before generate button
    separator2 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator2.grid(row=current_row, column=0, columnspan=8, sticky="ew", pady=10)
    current_row += 1

    def validate_and_generate():
        try:
            inputs = {}
            invalid_entries = []

            # Clear previous error highlighting
            for param in parameters:
                for entry, error_label in zip(entries[param], error_labels[param]):
                    entry.configure(background="white")
                    error_label.configure(text="")

            # Collect all inputs from GUI
            for param in parameters:
                if check_vars[param].get():
                    inputs[param] = None  # Use default values if checkbox ticked
                else:
                    param_inputs = []
                    # Iterate over all input fields for this parameter
                    for entry, bins_entry, range_entry, bin_name_entry, error_label in zip(
                        entries[param], bins_entries[param], range_entries[param], bin_name_entries[param], error_labels[param]
                    ):
                        val = entry.get().strip()
                        if val:  # Only process non-empty inputs
                            parsed = parse_user_input(val)
                            if parsed is None:
                                invalid_entries.append((entry, error_label, "Invalid format"))
                            else:
                                bins_val = parse_bins_input(bins_entry.get())
                                range_val = parse_range_input(range_entry.get())  # New: Parse range input
                                # Use bins_val if provided, otherwise use default_bins[param], otherwise None
                                bin_count = bins_val if bins_val is not None else default_bins[param]
                                bin_name = bin_name_entry.get().strip() or get_default_bin_name(parsed)
                                
                                # Check if input is within combined allowed range
                                if not is_input_within_combined_range(parsed, param, allowed_values):
                                    valid_range = get_max_allowed_range(param, allowed_values)
                                    invalid_entries.append((entry, error_label, f"Out of combined range. Allowed: {valid_range}"))
                                else:
                                    param_inputs.append((parsed, bin_count, range_val, bin_name))
                    
                    # Only assign inputs if there are valid entries
                    inputs[param] = param_inputs if param_inputs else None

            # Highlight invalid entries and stop if there are errors
            for entry, error_label, msg in invalid_entries:
                entry.configure(background="pink")
                error_label.configure(text=msg)
            if invalid_entries:
                return

            # Collect cross coverage inputs
            cross_coverage_inputs = {}
            for gen in generations:
                cross_coverage_inputs[gen] = []
                for (name_entry, coverpoints_entry), illegal_entry in zip(
                    cross_coverage_entries[gen], cross_coverage_illegal_entries[gen]
                ):
                    name = name_entry.get().strip()
                    coverpoints = coverpoints_entry.get().strip()
                    illegal_bins = illegal_entry.get().strip()
                    
                    if name and coverpoints:
                        # Parse coverpoints
                        coverpoint_list = [cp.strip() for cp in coverpoints.split(",") if cp.strip()]
                        illegal_list = parse_illegal_bins(illegal_bins)
                        cross_coverage_inputs[gen].append((name, coverpoint_list, illegal_list))

            # Generate SystemVerilog code
            code = ""
            for gen in generations:
                coverpoints = []
                for param in parameters:
                    bins_list = []
                    
                    # Case 1: Checkbox ticked, use default values from Excel
                    if check_vars[param].get():
                        allowed = allowed_values[gen].get(param, [])
                        param_default_bins = default_bins[param]
                        
                        for item_type, item in allowed:
                            if item_type == "range":
                                a, b = item
                                a_str = str(a) if a != float('-inf') else "0