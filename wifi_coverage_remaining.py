entries[param], bins_entries[param], range_entries[param], bin_name_entries[param], error_labels[param]):
                        
                        input_text = entry.get().strip()
                        if input_text:
                            parsed = parse_user_input(input_text)
                            if parsed is None:
                                entry.configure(background="lightcoral")
                                error_label.configure(text="Invalid input format")
                                invalid_entries.append(f"{param}: Invalid input format")
                                continue
                            
                            # Parse bins and range
                            bins_count = parse_bins_input(bins_entry.get())
                            range_div = parse_range_input(range_entry.get())
                            
                            # Check if input conflicts with range division
                            if range_div is not None and parsed["type"] == "list":
                                entry.configure(background="lightcoral")
                                error_label.configure(text="Range division not applicable for list values")
                                invalid_entries.append(f"{param}: Range division not applicable for list values")
                                continue
                            
                            # Get bin name
                            bin_name = bin_name_entry.get().strip()
                            if not bin_name:
                                bin_name = get_default_bin_name(parsed)
                            
                            param_inputs.append({
                                "parsed": parsed,
                                "bins_count": bins_count,
                                "range_div": range_div,
                                "bin_name": bin_name,
                                "original_input": input_text
                            })
                    
                    if param_inputs:
                        inputs[param] = param_inputs

            # Validate inputs against allowed values
            for param in parameters:
                if param in inputs and inputs[param] is not None:
                    for i, input_data in enumerate(inputs[param]):
                        parsed = input_data["parsed"]
                        entry = entries[param][i]
                        error_label = error_labels[param][i]
                        
                        # Check if input is within combined allowed range
                        if not is_input_within_combined_range(parsed, param, allowed_values):
                            entry.configure(background="lightcoral")
                            max_range = get_max_allowed_range(param, allowed_values)
                            error_label.configure(text=f"Outside allowed range: {max_range}")
                            invalid_entries.append(f"{param}: Outside allowed range")

            # If there are invalid entries, show error and return
            if invalid_entries:
                messagebox.showerror("Validation Error", 
                    "Please fix the following errors:\n" + "\n".join(invalid_entries))
                return

            # Generate SystemVerilog code for each generation
            for gen in generations:
                try:
                    covergroup_name = f"cg_{gen.lower()}"
                    code = f"covergroup {covergroup_name} @(posedge clk);\n"
                    
                    # Generate coverpoints
                    for param in parameters:
                        if param in inputs and inputs[param] is not None:
                            # Check if input is allowed for this generation
                            for input_data in inputs[param]:
                                parsed = input_data["parsed"]
                                allowed = allowed_values[gen].get(param, [])
                                
                                if is_input_allowed_for_generation(parsed, allowed):
                                    coverpoint_name = f"cov_{param.lower()}"
                                    code += f"    {coverpoint_name}: coverpoint {param} {{\n"
                                    
                                    # Generate bins
                                    bins_code = generate_systemverilog_bins(
                                        parsed, 
                                        input_data["bins_count"], 
                                        input_data["range_div"], 
                                        input_data["bin_name"], 
                                        param.lower()
                                    )
                                    code += bins_code
                                    code += "    }\n"
                        else:
                            # Use default values if checkbox is ticked
                            if check_vars[param].get():
                                allowed = allowed_values[gen].get(param, [])
                                if allowed:
                                    coverpoint_name = f"cov_{param.lower()}"
                                    code += f"    {coverpoint_name}: coverpoint {param} {{\n"
                                    
                                    # Generate bins from allowed values
                                    for item_type, item in allowed:
                                        if item_type == "range":
                                            min_val, max_val = item
                                            min_str = str(min_val) if min_val != float('-inf') else "0"
                                            max_str = str(max_val) if max_val != float('inf') else "999999"
                                            
                                            # Use default bins if available
                                            if default_bins[param] is not None and default_bins[param] > 1:
                                                code += f"        bins {param.lower()}_default[{default_bins[param]}] = {{[{min_str}:{max_str}]}};\n"
                                            else:
                                                code += f"        bins {param.lower()}_default = {{[{min_str}:{max_str}]}};\n"
                                        elif item_type == "value":
                                            code += f"        bins {param.lower()}_v{item} = {{{item}}};\n"
                                    
                                    code += "    }\n"
                    
                    # Generate cross coverage
                    if gen in cross_coverage_entries:
                        for (name_entry, coverpoints_entry), illegal_entry in zip(
                            cross_coverage_entries[gen], cross_coverage_illegal_entries[gen]):
                            
                            cross_name = name_entry.get().strip()
                            coverpoints_text = coverpoints_entry.get().strip()
                            illegal_text = illegal_entry.get().strip()
                            
                            if cross_name and coverpoints_text:
                                coverpoints = [cp.strip() for cp in coverpoints_text.split(",")]
                                illegal_bins = parse_illegal_bins(illegal_text)
                                
                                cross_code = generate_cross_coverage_code(cross_name, coverpoints, illegal_bins)
                                code += cross_code
                    
                    code += "endgroup\n\n"
                    
                    # Save to file
                    filename = f"coverage_{gen.lower()}.sv"
                    try:
                        with open(filename, 'w') as f:
                            f.write(code)
                        print(f"Generated {filename}")
                    except Exception as e:
                        print(f"Error writing file {filename}: {e}")
                        
                except Exception as e:
                    print(f"Error generating code for {gen}: {e}")
                    messagebox.showerror("Generation Error", f"Error generating code for {gen}: {e}")

            messagebox.showinfo("Success", f"SystemVerilog coverage files generated successfully!")
            
        except Exception as e:
            print(f"Error in validate_and_generate: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Generate button
    generate_btn = ttk.Button(scrollable_frame, text="Generate SystemVerilog Coverage", 
                             command=validate_and_generate)
    generate_btn.grid(row=current_row, column=0, columnspan=10, pady=20)

    # Status label
    status_label = ttk.Label(scrollable_frame, text="Ready to generate coverage files", foreground="green")
    status_label.grid(row=current_row + 1, column=0, columnspan=10, pady=10)

    # Help section
    help_frame = ttk.LabelFrame(scrollable_frame, text="Help & Examples", padding="10")
    help_frame.grid(row=current_row + 2, column=0, columnspan=10, sticky="ew", padx=5, pady=10)

    help_text = """
INPUT FORMATS:
• Range: [1:100], [0:$], [$:∞] ($ = negative infinity, ∞ = positive infinity)
• Values: 10,20,30,40 (comma-separated list)
• Single value: 42

RANGE DIVISION FEATURE:
• Input: [1:50000], Range: 1000 → Creates bins [1:1000], [1001:2000], [2001:3000], etc.
• Automatically generates bin names like param_r1, param_r2, param_r3, etc.
• Leave Range field empty for manual binning

BINS FIELD:
• For ranges: Number of bins to create (e.g., 5 creates 5 equal bins)
• For values: Number of bins to distribute values into
• Empty = single bin

CROSS COVERAGE:
• Coverpoints: cov_param1,cov_param2
• Illegal bins: cov_param1.bin_name,cov_param2.bin_name; cov_param1.bin2,cov_param2.bin2
• For auto-generated range bins: cov_param.param_r1,cov_param.param_r2

CHECKBOX BEHAVIOR:
• Checked = Use default values from Excel file
• Unchecked = Use custom input values
"""

    help_label = ttk.Label(help_frame, text=help_text, font=("Courier", 9), justify="left")
    help_label.pack(anchor="w")

    # Start GUI
    root.mainloop()

except Exception as e:
    print(f"Error creating GUI: {e}")
    messagebox.showerror("GUI Error", f"Error creating GUI: {e}")
    sys.exit(1)
