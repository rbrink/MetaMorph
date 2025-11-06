import customtkinter as ctk
from typing import Optional

from core.utils import center_dialog
from core.config import Config
from core.rules import RenameRule
from ui.widgets import CTkLabelInput, CTkSpinBox

class RuleDialog(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTkBaseClass, existing: Optional[RenameRule] = None):
        super().__init__(master)
        # ----- Window Setup -----
        self.title("Add/Edit Rename Rule")
        self.geometry(center_dialog(master, 400, 300))
        self.after(250, lambda: self.iconbitmap(Config.WIN_ICO['ruledialog']))
        self.transient(master)
        self.grab_set()
        # ----- Attributes -----
        self.master = master
        self.existing = existing
        self.result: Optional[RenameRule] = None
        self.rule_types = [
            'Replace',
            'Regex_Replace',
            'Insert',
            'Remove',
            'Change_Case',
            'Numbering',
            'Change_Ext',
            'Trim',
            'Prefix_Suffix',
            'New_Name'
        ]
        self.param_frames = {}

        self.create_widgets()

    def create_widgets(self):
        frm = ctk.CTkFrame(self)
        self.type_var = ctk.StringVar()
        self.type_input = CTkLabelInput(frm, label="Rule Type:", input_class=ctk.CTkComboBox, input_var=self.type_var,
                                        input_args={'variable': self.type_var, 'values': list(self.rule_types),
                                                    'state': 'readonly', 'width': 200})
        self.type_input.grid(row=0, column=1, pady=10, sticky= ctk.W)
        self.type_var.trace_add('write', lambda *args: self._update_visibility())
        frm.pack(fill= ctk.BOTH, expand=True, padx=10, pady=10)
        # ----- Replace -----
        f_replace = ctk.CTkFrame(frm)
        self.replace_old = CTkLabelInput(f_replace, label="Old Text:", input_class=ctk.CTkEntry)
        self.replace_old.grid(row=0, column=0)
        self.replace_new = CTkLabelInput(f_replace, label="New Text:", input_class=ctk.CTkEntry)
        self.replace_new.grid(row=1, column=0)
        self.replace_case = ctk.BooleanVar(value=True)
        CTkLabelInput(f_replace, label="Case sensitive", input_class=ctk.CTkCheckBox, input_var=self.replace_case,
                      ).grid(row=3, column=0, columnspan=2)
        self.param_frames['replace'] = f_replace
        # ----- Regex Replace -----
        f_regex = ctk.CTkFrame(frm)
        self.regex_icase = ctk.BooleanVar(value=False)
        self.regex_pattern = CTkLabelInput(f_regex, label="Pattern:", input_class=ctk.CTkEntry)
        self.regex_pattern.grid(row=0, column=0)
        self.regex_repl = CTkLabelInput(f_regex, label="Replacement:", input_class=ctk.CTkEntry)
        self.regex_repl.grid(row=1, column=0)
        CTkLabelInput(f_regex, label="Ignore case", input_class=ctk.CTkCheckBox,
                   input_var=self.regex_icase).grid(row=2, column=0, columnspan=2)
        self.param_frames["regex_replace"] = f_regex
        # --- Insert ---
        f_insert = ctk.CTkFrame(frm)
        self.insert_tags = ctk.BooleanVar(value=False)
        self.insert_pos = CTkLabelInput(f_insert, label="Position", input_class=CTkSpinBox,
                                     input_args={'start': 0, 'end': 9999, 'width': 50})
        self.insert_pos.grid(row=0, column=0)
        self.insert_text = CTkLabelInput(f_insert, label="Text:", input_class=ctk.CTkEntry)
        self.insert_text.grid(row=1, column=0)
        CTkLabelInput(f_insert, label="Enable tags", input_class=ctk.CTkCheckBox,
                   input_var=self.insert_tags).grid(row=2, column=0, columnspan=2)
        self.param_frames["insert"] = f_insert
        # --- Remove ---
        f_remove = ctk.CTkFrame(frm)
        self.remove_start = CTkLabelInput(f_remove, label="Start index", input_class=CTkSpinBox,
                                       input_args={'start': 0, 'end': 9999, 'width': 50})
        self.remove_start.grid(row=0, column=0)
        self.remove_length = CTkLabelInput(f_remove, label="Length:", input_class=CTkSpinBox,
                                        input_args={'start': 0, 'end': 9999, 'width': 50})
        self.remove_length.grid(row=0, column=0)
        self.param_frames["remove"] = f_remove
        # --- Change Case ---
        f_case = ctk.CTkFrame(frm)
        cm_options = ["lower", "upper", "title", "capitalize"]
        self.case_mode = CTkLabelInput(f_case, label="Mode:", input_class=ctk.CTkComboBox,
                                    input_args={'values': cm_options, 'state': "readonly"})
        self.case_mode.input.set(cm_options[0])
        self.case_mode.grid(row=0, column=1)
        self.param_frames["change_case"] = f_case
        # --- Numbering ---
        f_num = ctk.CTkFrame(frm)
        self.num_template = CTkLabelInput(f_num, label="Template", input_class=ctk.CTkEntry)
        self.num_template.grid(row=0, column=0)
        self.num_template.input.insert(0, "{name}_{num:3}")
        self.num_start = CTkLabelInput(f_num, label="Start:", input_class=CTkSpinBox,
                                    input_args={'start': 0, 'end': 9999, 'width': 50})
        self.num_start.grid(row=1, column=0)
        self.num_inc = CTkLabelInput(f_num, label="Increment:", input_class=CTkSpinBox,
                                  input_args={'start': 0, 'end': 9999, 'width': 50})
        self.num_inc.grid(row=2, column=0)
        self.param_frames["numbering"] = f_num
        # --- Change Ext ---
        f_ext = ctk.CTkFrame(frm)
        self.new_ext = CTkLabelInput(f_ext, label="New Extension:", input_class=ctk.CTkEntry)
        self.new_ext.grid(row=0, column=0)
        self.param_frames["change_ext"] = f_ext
        # --- Trim ---
        f_trim = ctk.CTkFrame(frm)
        trim_options = ['left', 'right', 'both']
        self.trim_side = CTkLabelInput(f_trim, label="Side:", input_class=ctk.CTkComboBox,
                                    input_args={'values': trim_options, 'state': "readonly"
                                    })
        self.trim_side.grid(row=0, column=0)
        self.trim_side.input.set(trim_options[0])
        self.trim_count = CTkLabelInput(f_trim, label="Count:", input_class=CTkSpinBox,
                                     input_args={'start': 0, 'end':999, 'width': 5})
        self.trim_count.grid(row=1, column=0)
        self.param_frames["trim"] = f_trim
        # --- Prefix/Suffix ---
        f_ps = ctk.CTkFrame(frm)
        self.ps_tags = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(f_ps, text="Enable tags", variable=self.ps_tags).grid(row=2, column=0, columnspan=2)
        self.ps_prefix = CTkLabelInput(f_ps, label="Prefix:", input_class=ctk.CTkEntry)
        self.ps_prefix.grid(row=0, column=0)
        self.ps_suffix = CTkLabelInput(f_ps, label="Suffix:", input_class=ctk.CTkEntry)
        self.ps_suffix.grid(row=1, column=0)
        CTkLabelInput(f_ps, label="Enable tags", input_class=ctk.CTkCheckBox,
                   input_var=self.ps_tags).grid(row=2, column=0, columnspan=2)
        self.param_frames["prefix_suffix"] = f_ps
        # --- New Name ---
        f_tpl = ctk.CTkFrame(frm)
        self.tpl_entry = CTkLabelInput(f_tpl, label="Template:", input_class=ctk.CTkEntry, input_args={'width': 300})
        self.tpl_entry.input.insert(0, "{show} ({year}) S{season:02}E{episode:02} - {title}.mkv")
        self.tpl_entry.grid(row=0, column=0)
        self.param_frames["new_name"] = f_tpl
        # ----- Buttons -----
        btns_frame = ctk.CTkFrame(frm)
        ctk.CTkButton(btns_frame, text="OK", command=self._on_ok).pack(side='left', padx=5)
        ctk.CTkButton(btns_frame, text="Cancel", command=self.destroy).pack(side='left', padx=5)
        btns_frame.grid(row=99, column=0, columnspan=2, pady=10)

        frm.columnconfigure(1, weight=1)
        self.type_input.input.set(self.rule_types[0])
        self._update_visibility()

        if self.existing: self._load_existing(self.existing)

    def _update_visibility(self, *args):
        for f in self.param_frames.values(): f.grid_forget()
        t = self.type_var.get().lower()
        if t in self.param_frames:
            self.param_frames[t].grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)

    def _load_existing(self, rule: RenameRule):
        self.type_var.set(rule.type); self._update_visibility()
        p = rule.params
        t = rule.type.lower()
        if t == "replace":
            self.replace_old.input.insert(0, p.get("old","")); self.replace_new.input.insert(0, p.get("new",""))
            self.replace_case.set(p.get("case_sensitive", True))
        elif t == "regex_replace":
            self.regex_pattern.input.insert(0, p.get("pattern","")); self.regex_repl.input.insert(0, p.get("repl",""))
            self.regex_icase.set(p.get("ignore_case", False))
        elif t == "insert":
            self.insert_pos.input.delete(0,"end"); self.insert_pos.input.insert(0, p.get("pos",0))
            self.insert_text.input.insert(0, p.get("text","")); self.insert_tags.set(p.get("use_tags", False))
        elif t == "remove":
            self.remove_start.input.delete(0,"end"); self.remove_start.input.insert(0, p.get("start",0))
            self.remove_length.input.delete(0,"end"); self.remove_length.input.insert(0, p.get("length",1))
        elif t == "change_case":
            self.case_mode.set(p.get("mode","lower"))
        elif t == "numbering":
            self.num_template.input.delete(0,"end"); self.num_template.input.insert(0, p.get("template","{name}_{num:3}"))
            self.num_start.input.delete(0,"end"); self.num_start.input.insert(0, p.get("start",1))
            self.num_inc.input.delete(0,"end"); self.num_inc.input.insert(0, p.get("increment",1))
        elif t == "change_ext":
            self.new_ext.input.insert(0, p.get("ext",""))
        elif t == "trim":
            self.trim_side.set(p.get("side","both"))
            self.trim_count.input.delete(0,"end"); self.trim_count.input.insert(0, p.get("count",1))
        elif t == "prefix_suffix":
            self.ps_prefix.input.insert(0, p.get("prefix","")); self.ps_suffix.input.insert(0, p.get("suffix",""))
            self.ps_tags.set(p.get("use_tags", False))
        elif t == "new_name":
            self.tpl_entry.input.delete(0,"end")
            self.tpl_entry.input.insert(0, p.get("template","{name}.{ext}"))

    def _on_ok(self):
        t = self.type_var.get()
        params = {}
        key = t.lower()
        if key == "replace":
            params = {"old": self.replace_old.get(), "new": self.replace_new.get(),
                      "case_sensitive": self.replace_case.get()}
        elif key == "regex_replace":
            params = {"pattern": self.regex_pattern.get(), "repl": self.regex_repl.get(),
                      "ignore_case": self.regex_icase.get()}
        elif key == "insert":
            params = {"pos": int(self.insert_pos.get()), "text": self.insert_text.get(),
                      "use_tags": self.insert_tags.get()}
        elif key == "remove":
            params = {"start": int(self.remove_start.get()), "length": int(self.remove_length.get())}
        elif key == "change_case":
            params = {"mode": self.case_mode.get()}
        elif key == "numbering":
            params = {"template": self.num_template.get(),
                      "start": int(self.num_start.get()), "increment": int(self.num_inc.get())}
        elif key == "change_ext":
            params = {"ext": self.new_ext.get()}
        elif key == "trim":
            params = {"side": self.trim_side.get(), "count": int(self.trim_count.get())}
        elif key == "prefix_suffix":
            params = {"prefix": self.ps_prefix.get(), "suffix": self.ps_suffix.get(),
                      "use_tags": self.ps_tags.get()}
        elif key == "new_name":
            params = {"template": self.tpl_entry.get()}

        self.result = RenameRule(type=t, params=params)
        self.destroy()
