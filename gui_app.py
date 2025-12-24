"""
Requirements Analyzer GUI Application
Main tkinter GUI for analyzing integrity requirements
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from requirements_analyzer import RequirementsAnalyzer
from visualizations import RequirementsVisualizer


class RequirementsGUI:
    """Main GUI application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Integrity Requirements Analyzer")
        self.root.geometry("1400x900")
        
        # Set icon and theme
        self.root.configure(bg='#f0f0f0')
        
        # Initialize analyzer and visualizer
        self.analyzer = RequirementsAnalyzer()
        self.visualizer = RequirementsVisualizer()
        
        # Track loaded files
        self.current_file = None
        self.comparison_file = None
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
        
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Requirements File", command=self.load_file)
        file_menu.add_command(label="Load Comparison File", command=self.load_comparison_file)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg='#2E86AB', height=80)
        header_frame.pack(fill='x', side='top')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame, 
            text="Integrity Requirements Analyzer",
            font=('Arial', 24, 'bold'),
            bg='#2E86AB',
            fg='white'
        )
        title_label.pack(pady=20)
    
    def create_main_content(self):
        """Create main content area with tabs"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # File selection section
        file_frame = tk.LabelFrame(main_frame, text="File Selection", font=('Arial', 10, 'bold'), 
                                  bg='#f0f0f0', padx=10, pady=10)
        file_frame.pack(fill='x', pady=(0, 10))
        
        # Current file
        tk.Label(file_frame, text="Current File:", bg='#f0f0f0', font=('Arial', 9)).grid(
            row=0, column=0, sticky='w', pady=5
        )
        self.current_file_label = tk.Label(
            file_frame, text="No file loaded", bg='white', relief='sunken',
            anchor='w', font=('Arial', 9), padx=5
        )
        self.current_file_label.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Button(
            file_frame, text="Browse...", command=self.load_file,
            bg='#2E86AB', fg='white', font=('Arial', 9, 'bold'),
            cursor='hand2', padx=15
        ).grid(row=0, column=2, pady=5)
        
        # Comparison file
        tk.Label(file_frame, text="Comparison File:", bg='#f0f0f0', font=('Arial', 9)).grid(
            row=1, column=0, sticky='w', pady=5
        )
        self.comparison_file_label = tk.Label(
            file_frame, text="No comparison file (optional)", bg='white', relief='sunken',
            anchor='w', font=('Arial', 9), padx=5
        )
        self.comparison_file_label.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        tk.Button(
            file_frame, text="Browse...", command=self.load_comparison_file,
            bg='#F18F01', fg='white', font=('Arial', 9, 'bold'),
            cursor='hand2', padx=15
        ).grid(row=1, column=2, pady=5)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Analyze button
        analyze_frame = tk.Frame(main_frame, bg='#f0f0f0')
        analyze_frame.pack(fill='x', pady=(0, 10))
        
        self.analyze_btn = tk.Button(
            analyze_frame, text="🔍 Analyze Requirements", command=self.analyze,
            bg='#06A77D', fg='white', font=('Arial', 12, 'bold'),
            cursor='hand2', padx=20, pady=10, state='disabled'
        )
        self.analyze_btn.pack()
        
        # Tabbed interface
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.overview_tab = tk.Frame(self.notebook, bg='white')
        self.changes_tab = tk.Frame(self.notebook, bg='white')
        self.impact_tab = tk.Frame(self.notebook, bg='white')
        self.details_tab = tk.Frame(self.notebook, bg='white')
        
        self.notebook.add(self.overview_tab, text='📊 Overview')
        self.notebook.add(self.changes_tab, text='🔄 Changed Requirements')
        self.notebook.add(self.impact_tab, text='⚠️ Impact Analysis')
        self.notebook.add(self.details_tab, text='📋 Details')
        
        # Initialize each tab
        self.init_overview_tab()
        self.init_changes_tab()
        self.init_impact_tab()
        self.init_details_tab()
    
    def init_overview_tab(self):
        """Initialize overview tab"""
        info_label = tk.Label(
            self.overview_tab,
            text="Load a requirements file and click 'Analyze' to see the overview dashboard.",
            font=('Arial', 11),
            bg='white',
            fg='#666'
        )
        info_label.pack(expand=True)
    
    def init_changes_tab(self):
        """Initialize changes tab"""
        # Create treeview for changes
        columns = ('ID', 'Type', 'Section', 'Category', 'Impact Level')
        
        # Scrollbar
        scroll_frame = tk.Frame(self.changes_tab, bg='white')
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.changes_tree = ttk.Treeview(
            scroll_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        self.changes_tree.pack(fill='both', expand=True)
        
        scrollbar.config(command=self.changes_tree.yview)
        
        # Configure columns
        self.changes_tree.column('#0', width=50, anchor='center')
        self.changes_tree.heading('#0', text='#')
        
        for col in columns:
            self.changes_tree.heading(col, text=col)
            if col == 'ID':
                self.changes_tree.column(col, width=100, anchor='center')
            elif col == 'Type':
                self.changes_tree.column(col, width=100, anchor='center')
            elif col == 'Impact Level':
                self.changes_tree.column(col, width=100, anchor='center')
            else:
                self.changes_tree.column(col, width=200)
        
        # Bind double-click to show details
        self.changes_tree.bind('<Double-1>', self.show_change_details)
        
        # Info message
        info_label = tk.Label(
            self.changes_tab,
            text="Load both current and comparison files to see changes. Double-click a row for details.",
            font=('Arial', 9),
            bg='white',
            fg='#999'
        )
        info_label.pack(side='bottom', pady=5)
    
    def init_impact_tab(self):
        """Initialize impact analysis tab"""
        info_label = tk.Label(
            self.impact_tab,
            text="Impact analysis will appear here after comparing two files.",
            font=('Arial', 11),
            bg='white',
            fg='#666'
        )
        info_label.pack(expand=True)
    
    def init_details_tab(self):
        """Initialize details tab"""
        # Create scrolled text widget for details
        details_frame = tk.Frame(self.details_tab, bg='white')
        details_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(
            details_frame,
            text="Requirement Details",
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(anchor='w', pady=(0, 10))
        
        self.details_text = scrolledtext.ScrolledText(
            details_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            bg='#f9f9f9',
            padx=10,
            pady=10
        )
        self.details_text.pack(fill='both', expand=True)
        self.details_text.insert('1.0', 'Select a requirement to view details...')
        self.details_text.config(state='disabled')
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            relief='sunken',
            anchor='w',
            bg='#ddd',
            font=('Arial', 9)
        )
        self.status_bar.pack(side='bottom', fill='x')
    
    def load_file(self):
        """Load main requirements file"""
        filepath = filedialog.askopenfilename(
            title="Select Requirements File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if filepath:
            self.status_bar.config(text=f"Loading {os.path.basename(filepath)}...")
            self.root.update()
            
            success = self.analyzer.load_excel(filepath)
            
            if success:
                self.current_file = filepath
                self.current_file_label.config(text=os.path.basename(filepath))
                self.analyze_btn.config(state='normal')
                self.status_bar.config(text=f"Loaded: {os.path.basename(filepath)}")
                messagebox.showinfo("Success", f"File loaded successfully!\n\nTotal requirements: {len(self.analyzer.df)}")
            else:
                messagebox.showerror("Error", "Failed to load file. Please check the file format.")
                self.status_bar.config(text="Error loading file")
    
    def load_comparison_file(self):
        """Load comparison file for change detection"""
        filepath = filedialog.askopenfilename(
            title="Select Comparison File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if filepath:
            self.status_bar.config(text=f"Loading comparison file...")
            self.root.update()
            
            success = self.analyzer.load_comparison_file(filepath)
            
            if success:
                self.comparison_file = filepath
                self.comparison_file_label.config(text=os.path.basename(filepath))
                self.status_bar.config(text=f"Comparison file loaded: {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "Failed to load comparison file.")
                self.status_bar.config(text="Error loading comparison file")
    
    def analyze(self):
        """Perform analysis"""
        if self.analyzer.df is None:
            messagebox.showwarning("No Data", "Please load a requirements file first.")
            return
        
        self.status_bar.config(text="Analyzing requirements...")
        self.root.update()
        
        # Generate statistics
        stats = self.analyzer.generate_statistics()
        
        # Update overview tab
        self.update_overview_tab(stats)
        
        # If comparison file is loaded, detect changes
        if self.analyzer.df_old is not None:
            changes = self.analyzer.detect_changes()
            impact = self.analyzer.analyze_impact()
            
            self.update_changes_tab(changes)
            self.update_impact_tab(impact)
            
            self.status_bar.config(
                text=f"Analysis complete. {len(changes)} changes detected."
            )
        else:
            self.status_bar.config(text="Analysis complete. No comparison file loaded.")
        
        # Switch to overview tab
        self.notebook.select(0)
    
    def update_overview_tab(self, statistics):
        """Update overview tab with statistics"""
        # Clear existing content
        for widget in self.overview_tab.winfo_children():
            widget.destroy()
        
        # Create visualization
        try:
            canvas = self.visualizer.create_overview_dashboard(statistics, self.overview_tab)
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        except Exception as e:
            error_label = tk.Label(
                self.overview_tab,
                text=f"Error creating visualization: {str(e)}",
                font=('Arial', 10),
                bg='white',
                fg='red'
            )
            error_label.pack(expand=True)
    
    def update_changes_tab(self, changes):
        """Update changes tab with detected changes"""
        # Clear existing items
        for item in self.changes_tree.get_children():
            self.changes_tree.delete(item)
        
        # Add changes to tree
        for idx, change in enumerate(changes, 1):
            values = (
                change.get('id', 'N/A'),
                change.get('type', 'N/A'),
                change.get('section', 'N/A'),
                change.get('category', 'N/A'),
                change.get('impact_level', 'N/A')
            )
            
            # Color code by impact level
            tag = change.get('impact_level', 'LOW')
            self.changes_tree.insert('', 'end', text=idx, values=values, tags=(tag,))
        
        # Configure tags for color coding
        self.changes_tree.tag_configure('HIGH', background='#ffcccc')
        self.changes_tree.tag_configure('MEDIUM', background='#fff4cc')
        self.changes_tree.tag_configure('LOW', background='#ccffcc')
    
    def update_impact_tab(self, impact_analysis):
        """Update impact analysis tab"""
        # Clear existing content
        for widget in self.impact_tab.winfo_children():
            widget.destroy()
        
        # Create visualization
        try:
            canvas = self.visualizer.create_impact_chart(impact_analysis, self.impact_tab)
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
            # Add summary text
            summary_frame = tk.Frame(self.impact_tab, bg='white')
            summary_frame.pack(side='bottom', fill='x', padx=10, pady=10)
            
            summary_text = f"""
            High Impact Changes: {impact_analysis.get('high_impact_count', 0)} | 
            Medium Impact Changes: {impact_analysis.get('medium_impact_count', 0)} | 
            Low Impact Changes: {impact_analysis.get('low_impact_count', 0)}
            """
            
            tk.Label(
                summary_frame,
                text=summary_text,
                font=('Arial', 10, 'bold'),
                bg='white'
            ).pack()
            
        except Exception as e:
            error_label = tk.Label(
                self.impact_tab,
                text=f"Error creating visualization: {str(e)}",
                font=('Arial', 10),
                bg='white',
                fg='red'
            )
            error_label.pack(expand=True)
    
    def show_change_details(self, event):
        """Show details of selected change"""
        selection = self.changes_tree.selection()
        if not selection:
            return
        
        item = self.changes_tree.item(selection[0])
        req_id = item['values'][0]
        
        # Get requirement details
        details = self.analyzer.get_requirement_details(req_id)
        
        if details:
            # Format details
            details_text = "=" * 80 + "\n"
            details_text += f"REQUIREMENT DETAILS - ID: {req_id}\n"
            details_text += "=" * 80 + "\n\n"
            
            for key, value in details.items():
                details_text += f"{key}:\n{value}\n\n"
            
            # Update details tab
            self.details_text.config(state='normal')
            self.details_text.delete('1.0', 'end')
            self.details_text.insert('1.0', details_text)
            self.details_text.config(state='disabled')
            
            # Switch to details tab
            self.notebook.select(3)
    
    def export_csv(self):
        """Export current data to CSV"""
        if self.analyzer.df is None:
            messagebox.showwarning("No Data", "No data to export. Please load a file first.")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if filepath:
            # Ask what to export
            export_type = messagebox.askquestion(
                "Export Type",
                "Export changes only?\n\nYes = Export changes\nNo = Export all requirements"
            )
            
            if export_type == 'yes' and self.analyzer.changes:
                success = self.analyzer.export_to_csv(filepath, 'changes')
            else:
                success = self.analyzer.export_to_csv(filepath, 'all')
            
            if success:
                messagebox.showinfo("Success", f"Data exported to:\n{filepath}")
                self.status_bar.config(text=f"Exported to {os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "Failed to export data.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        Integrity Requirements Analyzer
        Version 1.0
        
        A standalone application for analyzing system requirements,
        detecting changes, and performing impact analysis.
        
        Features:
        • Excel file parsing
        • Change detection
        • Impact analysis
        • Interactive visualizations
        • CSV export
        
        © 2025
        """
        messagebox.showinfo("About", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = RequirementsGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == "__main__":
    main()
