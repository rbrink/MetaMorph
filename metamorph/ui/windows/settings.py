import customtkinter as ctk
from tkinter import messagebox

from core.config import Config, ThemeManager
from core.utils import center_dialog
from ui.widgets import CTkLabelInput

class PreferencesWindow(ctk.CTkToplevel):
    """Modern preferences window for MetaMorph."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Preferences")
        self.geometry(center_dialog(parent, 600, 500))
        self.iconbitmap(Config.WIN_ICO['settings'])
        self.grab_set()
        self.transient(master=parent)
        
        self.fields = {}

        Config.load_config()
        self.hbpresets = Config.load_hb_presets()

        self._build_ui()

    def _build_ui(self):
        """Create tabbed preferences layout."""
        self.tabview = ctk.CTkTabview(self, anchor='w')
        self.tabview.pack(fill="both", expand=True, padx=15, pady=15)

        # Tabs
        paths_tab = self.tabview.add("Paths")
        presets_tab = self.tabview.add("Presets")
        theme_tab = self.tabview.add("Appearance")
        misc_tab = self.tabview.add("Other")

        # --- PATHS TAB ---
        self._add_path_input(paths_tab, "HandBrake CLI")
        self._add_path_input(paths_tab, "HB Presets JSON")
        self._add_dir_input(paths_tab, "Output Directory")
        self._add_dir_input(paths_tab, "Log Directory")

        # --- PRESETS TAB ---
        self._add_hb_presets_section(presets_tab)

        # --- APPEARANCE TAB ---
        self._add_theme_section(theme_tab)

        # --- OTHER TAB ---
        self._add_checkbox(misc_tab, "Delete Original")

        # --- BUTTONS ---
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(button_frame, text="Apply", command=self.save_settings).pack(side="right", padx=5)

    # -------------------- COMPONENT HELPERS --------------------

    def _add_path_input(self, parent, key):
        frame = ctk.CTkFrame(parent)
        var = ctk.StringVar(value=Config.get(key))
        entry = CTkLabelInput(frame, label=key+":", input_class=ctk.CTkEntry, label_args={'anchor': 'w', 'font': ("Helvetica", 10), 'height': 25},
                              input_var=var, input_args={'textvariable': var, 'width': 400, 'height': 25}, stacked=True)
        entry.grid(row=0, column=0, padx=(0, 5), sticky='ew')
        ctk.CTkButton(frame, text=f"Browse", width=50, command=lambda: self._browse_file(var)
                      ).grid(row=0, column=1, pady=(20, 0), sticky='s')
        frame.pack(fill='x', padx=10, pady=5)
        self.fields[key] = var

    def _add_dir_input(self, parent, key):
        frame = ctk.CTkFrame(parent)
        var = ctk.StringVar(value=Config.get(key))
        entry = CTkLabelInput(frame, label=key+":", input_class=ctk.CTkEntry, label_args={'anchor': 'w', 'font': ("Helvetica", 10), 'height': 25},
                              input_var=var, input_args={'textvariable': var, 'width': 400, 'height': 25}, stacked=True)
        entry.grid(row=0, column=0, padx=(0, 5), sticky='ew')
        ctk.CTkButton(frame, text=f"Browse", width=50, command=lambda: self._browse_file(var)
                      ).grid(row=0, column=1, pady=(20, 0), sticky='s')
        frame.pack(fill='x', padx=10, pady=5)
        self.fields[key] = var

    def _add_hb_presets_section(self, parent):
        """Preset category + name combo pairs."""
        preset_cat_var = ctk.StringVar()
        preset_name_var = ctk.StringVar(value=Config.get("HB Preset"))

        def update_presets(*args):
            selected_cat = preset_cat_var.get()
            presets = self.hbpresets.get(selected_cat, {})
            preset_names = list(presets.keys())
            preset_combo.input.configure(values=preset_names)
            print(f"DEBUG: preset_names: {preset_names}")
            if preset_names:
                preset_name_var.set(preset_names[0])

        cat_combo = CTkLabelInput(parent, label="Preset Category:", input_class=ctk.CTkComboBox, label_args={'anchor': 'w'}, input_var=preset_cat_var,
                                  input_args={'values': list(self.hbpresets.keys()), 'variable': preset_cat_var,
                                              'command': lambda choice=None: update_presets()})
        cat_combo.pack(pady=5, anchor='w')

        preset_combo = CTkLabelInput(parent, label="Preset Name:", input_class=ctk.CTkComboBox, label_args={'anchor': 'w'}, input_var=preset_name_var,
                                     input_args={'variable': preset_name_var})
        preset_combo.pack(pady=5, anchor='w')

        # Preselect current preset
        for cat, presets in self.hbpresets.items():
            if Config.get("HB Preset") in presets:
                preset_cat_var.set(cat)
                preset_combo.input.configure(values=list(presets.keys()))
                break

        self.fields["HB Preset"] = preset_name_var

    def _add_theme_section(self, parent):
        appearance_var = ctk.StringVar(value=self._get_theme_name_from_data(Config.get("UI Appearance")))
        accent_var = ctk.StringVar(value=Config.get("UI Accent"))

        # Instant theme preview
        def on_theme_change(*_):
            theme = Config.APPEARANCE_MODES[appearance_var.get()]
            Config.set("UI Appearance", theme)
            Config.set("UI Accent", accent_var.get())
            ThemeManager.apply(self.master, Config)

        appearance_combo = CTkLabelInput(parent, label="UI Appearance:", input_class=ctk.CTkComboBox, input_var=appearance_var,
                                         input_args={'values': list(Config.APPEARANCE_MODES.keys()), 'variable':appearance_var,
                                                     'command': lambda choice=None: on_theme_change()})
        appearance_combo.pack(pady=5, anchor='w')

        accent_combo = CTkLabelInput(parent, label="Accent Color:", input_class=ctk.CTkComboBox, input_var=accent_var,
                                    input_args={'values': list(Config.COLOR_THEMES.keys()), 'variable': accent_var,
                                                'command': lambda choice=None: on_theme_change()})
        accent_combo.pack(pady=5, anchor='w')

        self.fields["UI Appearance"] = appearance_var
        self.fields["UI Accent"] = accent_var

    def _add_checkbox(self, parent, key):
        var = ctk.BooleanVar(value=Config.get(key))
        chk = ctk.CTkCheckBox(parent, text=key, variable=var)
        chk.pack(anchor="w", padx=10, pady=5)
        self.fields[key] = var

    # -------------------- FILE / DIR HELPERS --------------------

    def _browse_file(self, var):
        path = ctk.filedialog.askopenfilename(title="Select File")
        if path:
            var.set(path)

    def _browse_dir(self, var):
        path = ctk.filedialog.askdirectory(title="Select Directory")
        if path:
            var.set(path)

    # -------------------- SAVE --------------------

    def _get_theme_name_from_data(self, value):
        for name, data in Config.APPEARANCE_MODES.items():
            if isinstance(value, dict) and data.get("appearance_mode") == value.get("appearance_mode"):
                return name
        return "System"

    def save_settings(self):
        """Save preferences and apply instantly."""
        for key, var in self.fields.items():
            Config.set(key, var.get())

        Config.save_config()
        ThemeManager.apply(self.master, Config)
        
        messagebox.showinfo("Settings", "Settings saved and applied successfully.")
        self.destroy()
