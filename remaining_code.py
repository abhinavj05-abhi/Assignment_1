cross_coverage = f"  {cross_name}: cross cov_{coverpoints_str.replace('cov_', '').replace(', ', ', cov_')} {{"
                    
                    # Add illegal bins if specified
                    if illegal_list:
                        cross_coverage += "\n"
                        for illegal_condition in illegal_list:
                            cross_coverage += f"    illegal_bins illegal_{illegal_condition.replace('.', '_').replace(',', '_and_')} = binsof({illegal_condition.replace('.', '.').replace(',', ') intersect binsof(')});\n"
                    
                    cross_coverage += "\n  };"
                    cross_coverages.append(cross_coverage)

                # Generate the complete covergroup for this generation
                if coverpoints or cross_coverages:
                    code += f"covergroup cg_{gen.lower().replace(' ', '_')} @(posedge clk);\n"
                    code += "\n".join(coverpoints)
                    if coverpoints and cross_coverages:
                        code += "\n"
                    code += "\n".join(cross_coverages)
                    code += "\nendgroup\n\n"

            # Display the generated code
            if code:
                result_window = tk.Toplevel(root)
                result_window.title("Generated SystemVerilog Code")
                result_window.geometry("1000x700")
                
                text_widget = tk.Text(result_window, wrap=tk.WORD, font=("Courier", 10))
                scrollbar_result = ttk.Scrollbar(result_window, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scrollbar_result.set)
                
                text_widget.insert(tk.END, code)
                text_widget.config(state=tk.DISABLED)
                
                text_widget.pack(side="left", fill="both", expand=True)
                scrollbar_result.pack(side="right", fill="y")
                
                # Add copy button
                def copy_to_clipboard():
                    result_window.clipboard_clear()
                    result_window.clipboard_append(code)
                    messagebox.showinfo("Success", "Code copied to clipboard!")
                
                copy_btn = ttk.Button(result_window, text="Copy to Clipboard", command=copy_to_clipboard)
                copy_btn.pack(pady=10)
                
                # Add save button
                def save_to_file():
                    try:
                        from tkinter import filedialog
                        file_path = filedialog.asksaveasfilename(
                            defaultextension=".sv",
                            filetypes=[("SystemVerilog files", "*.sv"), ("All files", "*.*")]
                        )
                        if file_path:
                            with open(file_path, 'w') as f:
                                f.write(code)
                            messagebox.showinfo("Success", f"Code saved to {file_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save file: {e}")
                
                save_btn = ttk.Button(result_window, text="Save to File", command=save_to_file)
                save_btn.pack(pady=5)
            else:
                messagebox.showwarning("No Code Generated", "No valid inputs found for any generation.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error generating code: {e}")
            print(f"Detailed error: {e}")
            import traceback
            traceback.print_exc()

    # Generate button
    generate_btn = ttk.Button(scrollable_frame, text="Generate SystemVerilog Code", command=validate_and_generate)
    generate_btn.grid(row=current_row, column=0, columnspan=6, pady=20)

    # Status bar
    status_frame = ttk.Frame(root)
    status_frame.pack(fill="x", side="bottom")
    
    status_label = ttk.Label(status_frame, text=f"Ready - Loaded {len(parameters)} parameters and {len(generations)} generations")
    status_label.pack(side="left", padx=5, pady=2)

    # Start GUI
    print("Starting GUI...")
    root.mainloop()

except Exception as e:
    print(f"Error creating GUI: {e}")
    import traceback
    traceback.print_exc()
    if 'root' in locals():
        root.destroy()
    sys.exit(1)