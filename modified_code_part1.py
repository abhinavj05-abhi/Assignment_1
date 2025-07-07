import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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

# MODIFICATION 2: Add this new helper function
def get_param_width(param):
    """Get appropriate bit width for parameter based on allowed values"""
    try:
        max_val = 0
        for gen in generations:
            if param in allowed_values[gen]:
                for item_type, item in allowed_values[gen][param]:
                    if item_type == "range":
                        a, b = item
                        if b != float('inf'):
                            max_val = max(max_val, b)
                    elif item_type == "value":
                        max_val = max(max_val, item)
        
        # Calculate required bits
        if max_val <= 0:
            return 8  # Default 8 bits
        elif max_val <= 255:
            return 8
        elif max_val <= 65535:
            return 16
        elif max_val <= 4294967295:
            return 32
        else:
            return 64
    except Exception as e:
        print(f"Error calculating parameter width for {param}: {e}")
        return 8  # Default fallback

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

# MODIFICATION 3: Update the cross coverage generation function
def generate_cross_coverage_code(cross_name, coverpoints, illegal_bins):
    try:
        coverpoint_code = f"    {cross_name}: cross {', '.join(coverpoints)} {{\n"
        if illegal_bins:
            illegal_code = "\n".join(f"        illegal_bins {illegal_bin};" for illegal_bin in illegal_bins)
            coverpoint_code += illegal_code + "\n"
        coverpoint_code += "    }\n"
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