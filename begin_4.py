
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import math
import uuid
import json

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
                b = int(b) if b != "$" else float('inf')
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
                b = int(b) if b != "$" else float('inf')
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
            bin_name = f"{bin_name_prefix}_v{current}_{next_val}"
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
        conditions = [cond.strip() for cond in s.split(";") if cond.strip()]
        return conditions
    except Exception as e:
        print(f"Error parsing illegal bins: {e}")
        return []

# Get default bin cross_name with updated format
def get_default_bin_name(parsed, param_name):
    try:
        if parsed["type"] == "range":
            a, b = parsed["range"]
            a_str = str(a) if a != float('-inf') else "inf"
            b_str = str(b) if b != float('inf') else "$"
            return f"{param_name}_v{a_str}_{b_str}"
        elif parsed["type"] == "list":
            values = parsed["values"]
            if len(values) == 1:
                return f"{param_name}_v{values[0]}_{values[0]}"
            else:
                min_val = min(values)
                max_val = max(values)
                return f"{param_name}_v{min_val}_{max_val}"
    except Exception as e:
        print(f"Error getting default bin cross_name: {e}")
        return f"{param_name}_default_bin"

# Get combined allowed range for a parameter (union of all ranges/values)
def get_combined_allowed_range(param, allowed_values):
    try:
        all_ranges = []
        all_values = []
        
        for gen in allowed_values:
            for item_type, item in allowed_values[gen].get(param, []):
                if item_type == "range":
                    all_ranges.append(item)
                elif item_type == "value":
                    all_values.append(item)
        
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
            min_str = str(min_val) if min_val != float('-inf') else "inf"
            max_str = str(max_val) if max_val != float('inf') else "$"
            return f"[{min_str}:{max_str}]"
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
            min_str = str(min_val) if min_val != float('-inf') else "inf"
            max_str = str(max_val) if max_val != float('inf') else "$"
            if range_div is not None:
                bins = []
                current = min_val
                while current <= max_val:
                    next_val = min(current + range_div - 1, max_val)
                    next_str = str(next_val) if next_val != float('inf') else "$"
                    bin_name_i = f"{param}_v{current}_{next_str}" if not bin_name else bin_name
                    if bins_count is not None and bins_count > 1:
                        bins.append(f"        bins {bin_name_i}[{bins_count}] = {{[{current}:{next_str}]}};")
                    else:
                        bins.append(f"        bins {bin_name_i}[] = {{[{current}:{next_str}]}};")
                    current = next_val + 1
                return "\n".join(bins)
            else:
                if not bin_name:
                    bin_name = f"{param}_v{min_str}_{max_str}"
                if bins_count is not None and bins_count > 1:
                    return f"        bins {bin_name}[{bins_count}] = {{[{min_str}:{max_str}]}};"
                else:
                    return f"        bins {bin_name}[] = {{[{min_str}:{max_str}]}};"
        elif parsed["type"] == "list":
            values = parsed["values"]
            if len(values) == 1:
                v = values[0]
                bin_name_v = f"{param}_v{v}_{v}" if not bin_name else bin_name
                if bins_count is not None and bins_count > 1:
                    return f"        bins {bin_name_v}[{bins_count}] = {{{v}}};"
                else:
                    return f"        bins {bin_name_v}[] = {{{v}}};"
            else:
                values_str = ",".join(map(str, values))
                bin_name_v = f"{param}_v{min(values)}_{max(values)}" if not bin_name else bin_name
                if bins_count is not None and bins_count > 1:
                    return f"        bins {bin_name_v}[{bins_count}] = {{{values_str}}};"
                else:
                    return f"        bins {bin_name_v}[] = {{{values_str}}};"
    except Exception as e:
        print(f"Error generating SystemVerilog bins: {e}")
        return ""

# Generate cross coverage code
def generate_cross_coverage_code(cross_name, coverpoints, illegal_bins):
    try:
        coverpoint_code = f"    {cross_name}: cross {','.join(coverpoints)}"
        if illegal_bins:
            coverpoint_code += " {\n"
            illegal_code = "\n".join(f"        illegal_bins {illegal_bin.replace('=', '==')} = 1 when {{{illegal_bin}}};" 
                                   for illegal_bin in illegal_bins)
            coverpoint_code += illegal_code + "\n    }"
        else:
            coverpoint_code += ";"
        return coverpoint_code
    except Exception as e:
        print(f"Error generating cross coverage code: {e}")
        return ""

# Save user inputs to JSON file
def save_inputs_to_json(entries, bins_entries, range_entries, bin_name_entries, check_vars, cross_coverage_entries, wifi_specs_vars):
    try:
        inputs_data = {
            "parameters": {},
            "cross_coverage": {},
            "wifi_specifications": {}
        }
        
        # Save parameter inputs
        for param in entries:
            if param == "pkt_type":
                continue
            param_data = {
                "use_default": check_vars[param].get(),
                "inputs": []
            }
            for i in range(len(entries[param])):
                input_data = {
                    "input": entries[param][i].get().strip() if i < len(entries[param]) else "",
                    "bins": bins_entries[param][i].get().strip() if i < len(bins_entries[param]) else "",
                    "range": range_entries[param][i].get().strip() if i < len(range_entries[param]) else "",
                    "bin_name": bin_name_entries[param][i].get().strip() if i < len(bin_name_entries[param]) else ""
                }
                param_data["inputs"].append(input_data)
            inputs_data["parameters"][param] = param_data
        
        # Save cross coverage inputs
        for gen in cross_coverage_entries:
            cross_data = []
            for cross_entry in cross_coverage_entries[gen]:
                cross_data.append({
                    "cross_name": cross_entry['name'].get().strip(),
                    "coverpoints": cross_entry['coverpoints'].get().strip(),
                    "illegal_bins": cross_entry['illegal'].get().strip()
                })
            inputs_data["cross_coverage"][gen] = cross_data
        
        # Save WiFi specifications selections
        for gen, var in wifi_specs_vars.items():
            inputs_data["wifi_specifications"][gen] = var.get()
        
        output_file = "user_inputs.json"
        with open(output_file, 'w') as f:
            json.dump(inputs_data, f, indent=4)
        
        messagebox.showinfo("Success", f"User inputs saved successfully to: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving inputs to JSON: {str(e)}")
        print(f"Detailed error: {e}")

# Save user inputs to TXT file in JSON format
def save_inputs_to_txt(entries, bins_entries, range_entries, bin_name_entries, check_vars, cross_coverage_entries, wifi_specs_vars):
    try:
        inputs_data = {
            "parameters": {},
            "cross_coverage": {},
            "wifi_specifications": {}
        }
        
        # Save parameter inputs
        for param in entries:
            if param == "pkt_type":
                continue
            param_data = {
                "use_default": check_vars[param].get(),
                "inputs": []
            }
            for i in range(len(entries[param])):
                input_data = {
                    "input": entries[param][i].get().strip() if i < len(entries[param]) else "",
                    "bins": bins_entries[param][i].get().strip() if i < len(bins_entries[param]) else "",
                    "range": range_entries[param][i].get().strip() if i < len(range_entries[param]) else "",
                    "bin_name": bin_name_entries[param][i].get().strip() if i < len(bin_name_entries[param]) else ""
                }
                param_data["inputs"].append(input_data)
            inputs_data["parameters"][param] = param_data
        
        # Save cross coverage inputs
        for gen in cross_coverage_entries:
            cross_data = []
            for cross_entry in cross_coverage_entries[gen]:
                cross_data.append({
                    "cross_name": cross_entry['name'].get().strip(),
                    "coverpoints": cross_entry['coverpoints'].get().strip(),
                    "illegal_bins": cross_entry['illegal'].get().strip()
                })
            inputs_data["cross_coverage"][gen] = cross_data
        
        # Save WiFi specifications selections
        for gen, var in wifi_specs_vars.items():
            inputs_data["wifi_specifications"][gen] = var.get()
        
        output_file = "user_inputs.txt"
        with open(output_file, 'w') as f:
            json.dump(inputs_data, f, indent=4)
        
        messagebox.showinfo("Success", f"User inputs saved successfully to: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving inputs to TXT: {str(e)}")
        print(f"Detailed error: {e}")

# Generate combined module definition for all WiFi specifications
def generate_combined_module_definition(parameters, generations, allowed_values, wifi_specs_vars, user_inputs):
    try:
        selected_specs = [spec for spec, var in wifi_specs_vars.items() if var.get()]
        
        module_definition = "module rxpktgen_fcov;\n"
        module_definition += "// Variables\n"

        # Declare only parameters from Excel sheet
        for param in parameters:
            module_definition += f"integer {param.lower()};\n"
        
        module_definition += "\n// Clock signal\n"
        module_definition += "logic clk;\n"
        
        module_definition += "\n// Events\n"
        module_definition += "event trigger_cov;\n"
        for gen in generations:
            module_definition += f"event trigger_{gen.lower().replace(' ', '_')}_cov;\n"
        
        module_definition += "\n// Combined Coverage Groups\n"

        for gen in generations:
            if gen not in selected_specs:
                continue
            covergroup_name = f"pkt_{gen.lower().replace(' ', '_')}_cov"
            module_definition += f"covergroup {covergroup_name} @trigger_{gen.lower().replace(' ', '_')}_cov;\n"

            # Always include pkt_type coverpoint
            if "pkt_type" in allowed_values[gen]:
                coverpoint_name = "cov_pkt_type"
                module_definition += f"    {coverpoint_name}: coverpoint pkt_type {{\n"
                for item_type, item in allowed_values[gen]["pkt_type"]:
                    if item_type == "value":
                        module_definition += f"        bins pkt_type_tb = {{{item}}};\n"
                    elif item_type == "range":
                        min_val, max_val = item
                        min_str = str(min_val) if min_val != float('-inf') else "inf"
                        max_str = str(max_val) if max_val != float('inf') else "$"
                        module_definition += f"        bins pkt_type_tb = {{[{min_str}:{max_str}]}};\n"
                module_definition += "    }\n"

            for param in parameters:
                if param == "pkt_type":
                    continue  # Skip pkt_type as it's already handled
                if param in user_inputs and user_inputs[param]['use_default']:
                    if param in allowed_values[gen] and allowed_values[gen][param]:
                        coverpoint_name = f"cov_{param.lower()}"
                        module_definition += f"    {coverpoint_name}: coverpoint {param.lower()} {{\n"
                        for item_type, item in allowed_values[gen][param]:
                            if item_type == "range":
                                min_val, max_val = item
                                min_str = str(min_val) if min_val != float('-inf') else "inf"
                                max_str = str(max_val) if max_val != float('inf') else "$"
                                default_bins_count = user_inputs[param]['default_bins']
                                if default_bins_count is not None and default_bins_count > 1:
                                    bin_name = f"{param.lower()}_v{min_str}_{max_str}"
                                    module_definition += f"        bins {bin_name}[] = {{[{min_str}:{max_str}]}};\n"
                                else:
                                    bin_name = f"{param.lower()}_v{min_str}_{max_str}"
                                    module_definition += f"        bins {bin_name}[] = {{[{min_str}:{max_str}]}};\n"
                            elif item_type == "value":
                                bin_name = f"{param.lower()}_v{item}_{item}"
                                module_definition += f"        bins {bin_name}[] = {{{item}}};\n"
                        module_definition += "    }\n"
                else:
                    if param in user_inputs and user_inputs[param]['custom_bins']:
                        coverpoint_name = f"cov_{param.lower()}"
                        module_definition += f"    {coverpoint_name}: coverpoint {param.lower()} {{\n"
                        for bin_code in user_inputs[param]['custom_bins']:
                            module_definition += bin_code + "\n"
                        module_definition += "    }\n"

            if gen in user_inputs and 'cross_coverage' in user_inputs[gen]:
                for cross_code in user_inputs[gen]['cross_coverage']:
                    module_definition += cross_code + "\n"

            module_definition += f"endgroup: {covergroup_name}\n"
            module_definition += f"{covergroup_name} = new();\n\n"
        
        module_definition += "// Tasks\n"
        module_definition += "task run(integer dpi);\n"
        module_definition += "    cover_rxpktgen(dpi);\n"
        module_definition += "    -> trigger_cov;\n"
        
        # Generate if statements based on pkt_type values from Excel
        pkt_type_row = df[df["Parameters"] == "pkt_type"]
        for idx, gen in enumerate(generations):
            pkt_type_value = pkt_type_row[gen].iloc[0] if not pkt_type_row.empty else None
            if pd.notna(pkt_type_value):
                try:
                    pkt_type = int(pkt_type_value)
                    gen_name = gen.lower().replace(" ", "_")
                    module_definition += f"    if (pkt_type == {pkt_type}) -> trigger_{gen_name}_cov;\n"
                except (ValueError, TypeError):
                    print(f"Warning: Invalid pkt_type value for {gen}: {pkt_type_value}")
        module_definition += "endtask: run\n\n"
        
        # Generate cover_rxpktgen task with parameters from Excel (excluding pkt_type)
        task_params = [param.lower() for param in parameters if param != "pkt_type"]
        module_definition += "task cover_rxpktgen(integer dpi);\n"
        module_definition += f"    doi_rxpktgen_GetPktFuncCov(dpi, {', '.join(task_params)});\n"
        module_definition += "endtask: cover_rxpktgen\n\n"
        
        module_definition += "endmodule\n"
        return module_definition
    except Exception as e:
        print(f"Error generating combined module definition: {e}")
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
    parameters = df["Parameters"].dropna().tolist()
    if not parameters:
        print("Error: No valid parameters found in 'Parameters' column.")
        sys.exit(1)
    
    bins_column = df.columns[1]
    print(f"Bins column: {bins_column}")
    
    generations = [col for col in df.columns[2:] if col.strip()]
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
    root.title("WiFi Functional Coverage Generator - Combined Output")
    root.geometry("1800x1200")
    
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

    note_label = ttk.Label(scrollable_frame,
        text="Enhanced Note: Generates COMBINED functional coverage for all WiFi specifications in a single output file. Bin names default to {parameter}_v{start}_{end} format. Tick checkbox for default values from Excel. Use '+' to add up to 10 input fields for parameters and cross coverage models. Range field automatically divides a range into equal bins. The code automatically adapts to any number of WiFi specification columns in the Excel file. pkt_type is automatically set from Excel and not user-configurable.",
        wraplength=1750, foreground="blue", font=("Arial", 10))
    note_label.grid(row=0, column=0, columnspan=12, pady=10, sticky="w")

    param_frames = {}
    entries = {}
    bins_entries = {}
    range_entries = {}
    bin_name_entries = {}
    check_vars = {}
    error_labels = {}
    
    cross_coverage_frames = {}
    cross_coverage_entries = {}

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
    
    scrollable_frame.grid_columnconfigure(0, weight=1)
    
    for i, param in enumerate(parameters):
        if param == "pkt_type":
            continue  # Skip pkt_type in GUI
        try:
            # Add separator line before each parameter (except the first one)
            if i > 0:
                separator = ttk.Separator(scrollable_frame, orient="horizontal")
                separator.grid(row=current_row, column=0, sticky="ew", pady=10)
                current_row += 1

            param_frame = ttk.Frame(scrollable_frame)
            param_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=2)
            param_frame.grid_columnconfigure(2, weight=1)
            param_frames[param] = param_frame

            check_vars[param] = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(param_frame, text="", variable=check_vars[param],
                                       command=lambda p=param: toggle_entry_state(p))
            checkbox.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")

            default_bins_display = default_bins[param] if default_bins[param] is not None else "auto"
            label_text = f"{param} (default bins: {default_bins_display}):"
            label = ttk.Label(param_frame, text=label_text, font=("Arial", 10,), width=35, anchor="w")
            label.grid(row=0, column=1, padx=(0, 20), pady=2, sticky="w")

            input_frame = ttk.Frame(param_frame)
            input_frame.grid(row=0, column=2, sticky="ew", padx=0, pady=2)
            
            input_frame.grid_columnconfigure(0, minsize=160)
            input_frame.grid_columnconfigure(1, minsize=80)
            input_frame.grid_columnconfigure(2, minsize=80)
            input_frame.grid_columnconfigure(3, minsize=120)
            input_frame.grid_columnconfigure(4, minsize=150)
            input_frame.grid_columnconfigure(5, minsize=40)
            
            entries[param] = []
            bins_entries[param] = []
            range_entries[param] = []
            bin_name_entries[param] = []
            error_labels[param] = []

            def add_input_field(frame, row, param=param):
                try:
                    if row >= 10:
                        return
                    
                    if row == 0:
                        header_frame = ttk.Frame(frame)
                        header_frame.grid(row=0, column=0, columnspan=6, sticky="ew", pady=(0, 5))
                        
                        header_frame.grid_columnconfigure(0, minsize=160)
                        header_frame.grid_columnconfigure(1, minsize=80)
                        header_frame.grid_columnconfigure(2, minsize=80)
                        header_frame.grid_columnconfigure(3, minsize=120)
                        header_frame.grid_columnconfigure(4, minsize=150)
                        header_frame.grid_columnconfigure(5, minsize=40)
                        
                        ttk.Label(header_frame, text="Input", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Bins", font=("Arial", 9)).grid(row=0, column=1, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Range", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=2)
                        ttk.Label(header_frame, text="Bin Name", font=("Arial", 9)).grid(row=0, column=3, sticky="w", padx=2)
                        ttk.Label(header_frame, text="", font=("Arial", 9)).grid(row=0, column=4, sticky="w", padx=2)
                    
                    input_row = row + 1
                    
                    entry = ttk.Entry(frame, width=20)
                    entry.grid(row=input_row, column=0, sticky="ew", padx=2, pady=1)
                    entries[param].append(entry)
                    
                    bins_entry = ttk.Entry(frame, width=8)
                    if default_bins[param] is not None:
                        bins_entry.insert(0, str(default_bins[param]))
                    bins_entry.grid(row=input_row, column=1, sticky="ew", padx=2, pady=1)
                    bins_entries[param].append(bins_entry)
                    
                    range_entry = ttk.Entry(frame, width=8)
                    range_entry.grid(row=input_row, column=2, sticky="ew", padx=2, pady=1)
                    range_entries[param].append(range_entry)
                    
                    bin_name_entry = ttk.Entry(frame, width=12)
                    bin_name_entry.grid(row=input_row, column=3, sticky="ew", padx=2, pady=1)
                    bin_name_entries[param].append(bin_name_entry)
                    
                    error_label = ttk.Label(frame, text="", name=f"error_{param}_{row}", 
                                            foreground="red", font=("Arial", 8), width=18)
                    error_label.grid(row=input_row, column=4, sticky="w", padx=2, pady=1)
                    error_labels[param].append(error_label)
                    
                    if row < 9:
                        plus_btn = ttk.Button(frame, text="+", width=3,
                                              command=lambda: add_input_field(frame, row + 1, param))
                        plus_btn.grid(row=input_row, column=5, padx=2, pady=1)
                except Exception as e:
                    print(f"Error adding input field for {param}: {e}")
            
            add_input_field(input_frame, 0, param)
            
            current_row += 1
            
            combined_min, combined_max = get_combined_allowed_range(param, allowed_values)
            if combined_min is not None and combined_max is not None:
                min_str = str(combined_min) if combined_min != float('-inf') else "inf"
                max_str = str(combined_max) if combined_max != float('inf') else "$"
                info_text = f"Combined range: [{min_str}:{max_str}]"
            else:
                info_text = "No valid range found"
            
            info_label = ttk.Label(param_frame, text=info_text, font=("Arial", 8), foreground="gray")
            info_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=(0, 10))
            
            current_row += 1
            
        except Exception as e:
            print(f"Error creating GUI elements for parameter {param}: {e}")
            current_row += 1
    
    cross_coverage_label = ttk.Label(scrollable_frame, text="Cross Coverage Configuration:", 
                                     font=("Arial", 12, "bold"))
    cross_coverage_label.grid(row=current_row, column=0, sticky="w", pady=(20, 10))
    current_row += 1
    
    for gen in generations:
        try:
            cross_frame = ttk.LabelFrame(scrollable_frame, text=f"Cross Coverage for {gen}", 
                                         padding="10")
            cross_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
            cross_frame.grid_columnconfigure(0, weight=1)
            cross_frame.grid_columnconfigure(1, weight=2)
            cross_frame.grid_columnconfigure(2, weight=2)
            cross_coverage_frames[gen] = cross_frame
            
            cross_coverage_entries[gen] = []
            
            def add_cross_coverage_field(frame, row, gen=gen):
                try:
                    if row >= 10:
                        return
                    
                    if row == 0:
                        header_frame = ttk.Frame(frame)
                        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 5))
                        
                        header_frame.grid_columnconfigure(0, weight=1, minsize=200)
                        header_frame.grid_columnconfigure(1, weight=2, minsize=400)
                        header_frame.grid_columnconfigure(2, weight=2, minsize=400)
                        header_frame.grid_columnconfigure(3, minsize=40)
                        
                        ttk.Label(header_frame, text="Cross Name", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
                        ttk.Label(header_frame, text="Coverpoints (comma-separated)", font=("Arial", 9)).grid(row=0, column=1, sticky="w", padx=5, pady=2)
                        ttk.Label(header_frame, text="Illegal Bins (semicolon-separated, optional)", font=("Arial", 9)).grid(row=0, column=2, sticky="w", padx=5, pady=2)
                    
                    input_row = row + 1
                    
                    cross_name_entry = ttk.Entry(frame, width=25)
                    cross_name_entry.insert(0, f"cross_{gen.lower().replace(' ', '_')}_{row + 1}")
                    cross_name_entry.grid(row=input_row, column=0, sticky="ew", padx=5, pady=2)
                    
                    coverpoints_entry = ttk.Entry(frame, width=50)
                    coverpoints_entry.grid(row=input_row, column=1, sticky="ew", padx=5, pady=2)
                    
                    illegal_entry = ttk.Entry(frame, width=50)
                    illegal_entry.grid(row=input_row, column=2, sticky="ew", padx=5, pady=2)
                    
                    cross_coverage_entries[gen].append({
                        'name': cross_name_entry,
                        'coverpoints': coverpoints_entry,
                        'illegal': illegal_entry
                    })
                    
                    if row < 9:
                        plus_btn = ttk.Button(frame, text="+", width=3,
                                              command=lambda: add_cross_coverage_field(frame, row + 1, gen))
                        plus_btn.grid(row=input_row, column=3, padx=5, pady=2)
                except Exception as e:
                    print(f"Error adding cross coverage field for {gen}: {e}")
            
            add_cross_coverage_field(cross_frame, 0, gen)
            
            current_row += 1
            
        except Exception as e:
            print(f"Error creating cross coverage GUI for generation {gen}: {e}")
            current_row += 1
    
    wifi_specs_label = ttk.Label(scrollable_frame, text="WiFi Specifications to Include:", 
                                 font=("Arial", 12, "bold"))
    wifi_specs_label.grid(row=current_row, column=0, sticky="w", pady=(20, 10))
    current_row += 1
    
    wifi_specs_frame = ttk.Frame(scrollable_frame)
    wifi_specs_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
    
    wifi_specs_vars = {}
    for i, gen in enumerate(generations):
        wifi_specs_vars[gen] = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(wifi_specs_frame, text=gen, variable=wifi_specs_vars[gen])
        checkbox.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)
    
    current_row += 1
    
    def generate_coverage():
        try:
            user_inputs = {}
            
            for param in parameters:
                if param == "pkt_type":
                    user_inputs[param] = {
                        'use_default': True,  # Always use default for pkt_type
                        'default_bins': default_bins[param],
                        'custom_bins': []
                    }
                    continue
                user_inputs[param] = {
                    'use_default': check_vars[param].get(),
                    'default_bins': default_bins[param],
                    'custom_bins': []
                }
                
                if not check_vars[param].get():
                    for i, entry in enumerate(entries[param]):
                        input_text = entry.get().strip()
                        if not input_text:
                            continue
                        
                        if i < len(error_labels[param]):
                            error_labels[param][i].config(text="")
                        
                        parsed = parse_user_input(input_text)
                        if parsed is None:
                            if i < len(error_labels[param]):
                                error_labels[param][i].config(text="Invalid input format")
                            continue
                        
                        if not is_input_within_combined_range(parsed, param, allowed_values):
                            max_range = get_max_allowed_range(param, allowed_values)
                            if i < len(error_labels[param]):
                                error_labels[param][i].config(text=f"Out of range: {max_range}")
                            continue
                        
                        bins_count = None
                        range_div = None
                        bin_name = ""
                        
                        if i < len(bins_entries[param]):
                            bins_count = parse_bins_input(bins_entries[param][i].get())
                        if i < len(range_entries[param]):
                            range_div = parse_range_input(range_entries[param][i].get())
                        if i < len(bin_name_entries[param]):
                            bin_name = bin_name_entries[param][i].get().strip()
                        
                        if not bin_name:
                            bin_name = get_default_bin_name(parsed, param.lower())
                        
                        bin_code = generate_systemverilog_bins(parsed, bins_count, range_div, bin_name, param.lower())
                        if bin_code:
                            user_inputs[param]['custom_bins'].append(bin_code)
            
            for gen in generations:
                if gen in cross_coverage_entries:
                    user_inputs[gen] = {'cross_coverage': []}
                    for cross_entry in cross_coverage_entries[gen]:
                        cross_name = cross_entry['name'].get().strip()
                        coverpoints_text = cross_entry['coverpoints'].get().strip()
                        illegal_text = cross_entry['illegal'].get().strip()
                        
                        if cross_name and coverpoints_text:
                            coverpoints = [cp.strip() for cp in coverpoints_text.split(',') if cp.strip()]
                            if coverpoints:
                                illegal_bins = parse_illegal_bins(illegal_text)
                                cross_code = generate_cross_coverage_code(cross_name, coverpoints, illegal_bins)
                                user_inputs[gen]['cross_coverage'].append(cross_code)
            
            combined_code = generate_combined_module_definition(
                parameters, generations, allowed_values, wifi_specs_vars, user_inputs
            )
            
            output_file = "combined_wifi_functional_coverage.sv"
            with open(output_file, 'w') as f:
                f.write(combined_code)
            
            messagebox.showinfo("Success", f"Combined functional coverage generated successfully!\nSaved to: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating coverage: {str(e)}")
            print(f"Detailed error: {e}")
    
    # Create a frame to hold buttons for centering
    button_frame = ttk.Frame(scrollable_frame)
    button_frame.grid(row=current_row, column=0, sticky="ew", pady=10)
    button_frame.grid_columnconfigure(0, weight=1)
    
    generate_btn = ttk.Button(button_frame, text="Generate Combined Functional Coverage", 
                             command=generate_coverage)
    generate_btn.pack(side="left", padx=10, pady=10)
    
    save_inputs_btn = ttk.Button(button_frame, text="Save Inputs to JSON", 
                                command=lambda: save_inputs_to_json(entries, bins_entries, range_entries, 
                                                                   bin_name_entries, check_vars, 
                                                                   cross_coverage_entries, wifi_specs_vars))
    save_inputs_btn.pack(side="left", padx=10, pady=10)
    
    download_inputs_btn = ttk.Button(button_frame, text="Download Input Fields", 
                                    command=lambda: save_inputs_to_txt(entries, bins_entries, range_entries, 
                                                                      bin_name_entries, check_vars, 
                                                                      cross_coverage_entries, wifi_specs_vars))
    download_inputs_btn.pack(side="left", padx=10, pady=10)
    
    current_row += 1
    

    
    instructions = """
    Instructions:
    1. Check the checkbox to use default values from Excel for a parameter
    2. When unchecked, enter custom values in the format: [min:max] for ranges or val1,val2,val3 for lists
    3. Use the Bins field to specify number of bins (optional)
    4. Use the Range field to divide a range into equal-sized bins (optional)
    5. Bin Name will be auto-generated if left empty in format: {parameter}_v{start}_{end}
    6. Configure multiple cross coverage models for each WiFi specification using '+' button
    7. Illegal bins are optional and should be semicolon-separated
    8. Select which WiFi specifications to include in the combined output
    9. Click 'Generate' to create a single combined functional coverage file
    10. Click 'Save Inputs to JSON' to save all user inputs to a JSON file
    11. Click 'Download Input Fields' to save all user inputs to a text file in JSON format
    12. pkt_type is automatically set from Excel and not user-configurable
    
    The generated code will automatically handle all WiFi specifications in a single module.
    """
    
    instructions_label = ttk.Label(scrollable_frame, text=instructions, 
                                   font=("Arial", 9), foreground="darkblue", 
                                   wraplength=1700, justify="left")
    instructions_label.grid(row=current_row+1, column=0, pady=10, sticky="w")
    
    root.mainloop()

except Exception as e:
    print(f"Error creating GUI: {e}")
    messagebox.showerror("Error", f"Error creating GUI: {str(e)}")
    sys.exit(1)