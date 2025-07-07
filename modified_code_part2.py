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