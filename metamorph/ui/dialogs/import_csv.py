import csv
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox

from core.config import Config, Logger
from core.utils import center_dialog
from ui.widgets import CTkLabelInput

class ImportCSVWizard(ctk.CTkToplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # ----- Window Setup -----
        self.title("Import CSV Wizard")
        self.geometry(center_dialog(parent, 600, 625))
        self.after(250, lambda: self.iconbitmap(Config.WIN_ICO['epswizard']))
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        # ----- Attributes -----
        self.logger = Logger.get_logger(__name__)
        self.is_header = ctk.BooleanVar(value=False)
        self.file_encoding = ["UTF-8", "UTF-16", "ANSI", "ASCII"]
        self.loaded_csv_data = []
        self.data = []

        self.create_widgets()

    def create_widgets(self):
        # ----- Input -----
        input_frame = ctk.CTkFrame(self)
        self.csv_file = CTkLabelInput(input_frame, label="Filename:", input_class=ctk.CTkEntry, 
                                      input_args={'width': 300})
        self.csv_file.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky='w')
        ctk.CTkButton(input_frame, text="...", font=ctk.CTkFont(size=16), width=30,
                      command=self._load_csv_file).grid(row=0, column=3, padx=5)
        self.column_separator = CTkLabelInput(input_frame, label="Column Separator:", input_class=ctk.CTkEntry, 
                                              input_args={'width': 50})
        self.column_separator.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.column_separator.set(";")
        self.first_header = CTkLabelInput(input_frame, label="First line is header", input_class=ctk.CTkCheckBox, input_var=self.is_header,
                                          input_args={'variable': self.is_header})
        self.first_header.grid(row=1, column=2, padx=5, pady=2, sticky='e')
        self.encode_type = CTkLabelInput(input_frame, label="File encodeing:", input_class=ctk.CTkComboBox,
                                         input_args={'values': list(self.file_encoding), 'state': 'readonly'})
        self.encode_type.input.set(self.file_encoding[0])
        self.encode_type.grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ctk.CTkLabel(input_frame, text="After import the values will be abvailable using the {Csv:X} tag"
                     ).grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky='w')
        input_frame.pack(fill='both', padx=10, pady=10)
        # ----- Data View -----
        data_frame = ctk.CTkFrame(self)
        style = ttk.Style()
        style.configure("Treeview", font=("Courier New", 9), rowheight=15)
        self.csv_data = ttk.Treeview(data_frame, columns=(), show="headings", height=20, style="Treeview")
        self.csv_data.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(data_frame, orient='vertical', command=self.csv_data.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.csv_data.configure(yscrollcommand=scrollbar.set)
        data_frame.grid_rowconfigure(0, weight=1)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.pack(fill='both', expand=True, padx=5)
        # ----- Import/Cancel -----
        btn_frame = ctk.CTkFrame(self)
        ctk.CTkButton(btn_frame, text="Cancel", width=70, command=self.destroy).pack(side='right', padx=2)
        self.btn_import = ctk.CTkButton(btn_frame, text="Import", state='disabled', width=70, command=self.on_import)
        self.btn_import.pack(side='right', padx=2)
        btn_frame.pack(side='bottom', fill='x', padx=5, pady=10)

    def on_import(self):
        if not self.loaded_csv_data:
            messagebox.showwarning('No Data', 'Please load a CSV file first.')
            return

        headers = list(self.csv_data['columns'])
        # normalize headers: if header looks like "1:Title" -> use "Title"
        normalized_headers = []
        for h in headers:
            if isinstance(h, str) and ":" in h:
                normalized_headers.append(h.split(":", 1)[1].strip() or h)
            else:
                normalized_headers.append(h)

        self.data = []
        for row in self.loaded_csv_data:
            row_dict = {}
            for i, value in enumerate(row):
                header = normalized_headers[i] if i < len(normalized_headers) else f'Col{i+1}'
                # main key (header name) and two Csv: keys (by index and by header name)
                row_dict[header] = value
                row_dict[f'Csv:{i+1}'] = value
                row_dict[f'Csv:{header}'] = value
            self.data.append(row_dict)

        self.destroy()

    def _load_csv_file(self):
        filename = ctk.filedialog.askopenfilename(
            initialdir="/",
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"),)
            )
        if not filename:
            return
        # ----- Update UI -----
        self.csv_file.input.delete(0, tk.END)
        self.csv_file.input.insert(0, filename)

        delimiter = self.column_separator.get() or ','
        
        # ----- Clear Previous Content -----
        for item in self.csv_data.get_children():
            self.csv_data.delete(item)
        self.csv_data['columns'] = ()
        self.loaded_csv_data.clear()

        encoding = self.encode_type.get().lower()
        try:
            with open(filename, 'r', newline='', encoding=encoding) as file:
                reader = csv.reader(file, delimiter=delimiter)
                try:
                    first_row = next(reader, None)
                except StopIteration:
                    self.logger.error("CSV file empty")
                    messagebox.showerror("Error", "CSV file empty")
                    return
                if self.is_header.get():
                    header = [f"{i+1}:{h.strip()}" or f"col{i+1}" for i, h in enumerate(first_row)]
                    self.csv_data['columns'] = tuple(header)
                    for col in header:
                        self.csv_data.heading(col, text=col)
                        self.csv_data.column(col, anchor=tk.W, width=100)
                else:
                    num_cols = len(first_row)
                    cols = [f"{i+1}:" for i in range(num_cols)]
                    self.csv_data['columns'] = tuple(cols)
                    for col in cols:
                        self.csv_data.heading(col, text=col)
                        self.csv_data.column(col, anchor=tk.W, width=100)
                    self.csv_data.insert("", tk.END, values=first_row)
                    self.loaded_csv_data.append(first_row)
                for row in reader:
                    cols = list(self.csv_data['columns'])
                    if len(row) < len(cols):
                        row = row + "" * (len(cols) - len(row))
                    elif len(row) > len(cols):
                        row = row[:len(cols)]
                    self.csv_data.insert("", tk.END, values=row)
                    self.loaded_csv_data.append(row)
        except Exception as e:
            self.logger.error(f"Failed to load CSV file {e}")
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")
        self.btn_import.configure(state="normal")
