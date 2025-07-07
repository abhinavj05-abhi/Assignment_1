# MODIFICATION 1: Replace the entire generate_code() function (around line 800+)

def generate_code():
    try:
        # Single combined result
        combined_result = "// Combined SystemVerilog Coverage Model\n"
        combined_result += "// Auto-generated from WiFi Functional Coverage Generator\n\n"
        combined_result += "module coverage_model;\n\n"
        combined_result += "// Clock signal\n"
        combined_result += "logic clk;\n\n"
        combined_result += "// Variables\n"
        
        # Add variable declarations for all parameters
        for param in parameters:
            combined_result += f"logic [{get_param_width(param)}-1:0] {param.lower()};\n"
        
        combined_result += "\n// Events\n"
        for gen in generations:
            combined_result += f"event trigger_{gen.lower()}_cov;\n"
        
        combined_result += "\n// Coverage Groups\n"
        
        # Process each generation
        for gen in generations:
            combined_result += f"\n// Coverage group for {gen}\n"
            combined_result += f"covergroup cg_{gen.lower()} @(posedge clk);\n"
            
            # Process parameters for this generation
            for param in parameters:
                param_has_content = False
                param_content = ""
                
                if check_vars[param].get():
                    # Use default values from Excel
                    if param in allowed_values[gen] and allowed_values[gen][param]:
                        param_content += f"    cov_{param.lower()}: coverpoint {param.lower()} {{\n"
                        
                        # Generate bins from allowed values
                        for item_type, item in allowed_values[gen][param]:
                            if item_type == "range":
                                min_val, max_val = item
                                min_str = str(min_val) if min_val != float('-inf') else "0"
                                max_str = str(max_val) if max_val != float('inf') else "999999"
                                
                                if default_bins[param] is not None and default_bins[param] > 1:
                                    param_content += f"        bins {param.lower()}_default[{default_bins[param]}] = {{[{min_str}:{max_str}]}};\n"
                                else:
                                    param_content += f"        bins {param.lower()}_default = {{[{min_str}:{max_str}]}};\n"
                                param_has_content = True
                            elif item_type == "value":
                                param_content += f"        bins {param.lower()}_v{item} = {{{item}}};\n"
                                param_has_content = True
                        
                        param_content += "    }\n"
                else:
                    # Use user-defined values
                    param_content += f"    cov_{param.lower()}: coverpoint {param.lower()} {{\n"
                    
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
                                param_content += bin_code + "\n"
                                param_has_content = True
                                error_labels[param][i].config(text="OK", foreground="green")
                            else:
                                error_labels[param][i].config(text="Code generation failed")
                    
                    param_content += "    }\n"
                
                # Only add parameter content if it has valid bins
                if param_has_content:
                    combined_result += param_content
            
            # Add cross coverage for this generation
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
                    combined_result += cross_code
            
            combined_result += "endgroup\n"
        
        # Add WiFi specs if any selected
        selected_specs = [spec for spec, var in wifi_specs_vars.items() if var.get()]
        if selected_specs:
            combined_result += f"\n// Selected WiFi Specifications: {', '.join(selected_specs)}\n"
            combined_result += "// Add your WiFi-specific coverage code here\n"
        
        combined_result += "\n// Instantiate coverage groups\n"
        for gen in generations:
            combined_result += f"cg_{gen.lower()} cg_{gen.lower()}_inst = new();\n"
        
        combined_result += "\nendmodule\n"
        
        # Create output window with single file
        output_window = tk.Toplevel(root)
        output_window.title("Generated SystemVerilog Coverage Model")
        output_window.geometry("1200x800")
        
        # Create single text widget
        text_widget = tk.Text(output_window, wrap="none", font=("Courier", 10))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", combined_result)
        
        # Add scrollbars
        h_scrollbar = ttk.Scrollbar(output_window, orient="horizontal", command=text_widget.xview)
        h_scrollbar.pack(side="bottom", fill="x")
        text_widget.config(xscrollcommand=h_scrollbar.set)
        
        v_scrollbar = ttk.Scrollbar(output_window, orient="vertical", command=text_widget.yview)
        v_scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=v_scrollbar.set)
        
        # Add save button
        def save_file():
            try:
                with open("coverage_model.sv", "w") as f:
                    f.write(combined_result)
                messagebox.showinfo("Success", "File saved as coverage_model.sv")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {e}")
        
        save_btn = ttk.Button(output_window, text="Save as coverage_model.sv", command=save_file)
        save_btn.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Error", f"Error generating code: {e}")
        print(f"Detailed error: {e}")


# MODIFICATION 2: Add this new helper function after the existing helper functions (around line 200)

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


# MODIFICATION 3: Update the cross coverage generation function (around line 150)

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
