import customtkinter as ctk
from typing import Any, List, Literal, Type, \
    Optional, Tuple, Callable

class CTkLabelInput(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, label: str = '', input_class: Type[ctk.CTkBaseClass] = ctk.CTkEntry,
                 input_var: Optional[ctk.Variable] = None, input_args: Optional[dict[str, Any]] = None, label_args: Optional[dict[str, Any]] = None,
                 stacked: ctk.BooleanVar = False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        # ----- Attributes -----
        self.master = master
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var
        
        if input_class in (ctk.CTkCheckBox, ctk.CTkButton, ctk.CTkRadioButton):
            input_args['text'] = label
            input_args['variable'] = self.variable
            self.input = input_class(self, **input_args)
            self.input.grid(row=0, column=0, sticky='ew')
        else:
            self.label = ctk.CTkLabel(self, text=label, **label_args)
            if stacked:
                self.label.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
                if input_class not in (ctk.CTkComboBox, CTkSpinBox):
                    input_args['textvariable'] = self.variable
                else:
                    input_args['variable'] = self.variable
                self.input = input_class(self, **input_args)
                self.input.grid(row=1, column=0, columnspan=3, sticky='ew')
            else:
                self.label.grid(row=0, column=0, padx=5, pady=2, sticky='ew')
                if input_class not in (ctk.CTkComboBox, CTkSpinBox):
                    input_args['textvariable'] = self.variable
                else:
                    input_args['variable'] = self.variable
                self.input = input_class(self, **input_args)
                self.input.grid(row=0, column=1, columnspan=3, sticky='ew')
        
        self.columnconfigure(0, weight=1)
    
    def grid(self, sticky='ew', **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == ctk.CTkTextbox:
                return self.input.get('1.0', 'end')
            else:
                return self.input.get()
        except TypeError:
            return ""
    
    def set(self, value, *args, **kwargs):
        if type(self.variable) == ctk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input) in (ctk.CTkCheckBox, ctk.CTkRadioButton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == ctk.CTkTextbox:
            self.input.delete("1.0", ctk.END)
            self.input.insert("1.0", value)
        else:    # Must be CTkEntry with no variable
            self.input.delete(0, ctk.END)
            self.input.insert(0, value)

class CTkSpinBox(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, start: float = 0, end: float = 9999, increment: float = 1.0, scroll_inc: float | None = None,
                 variable: ctk.StringVar | ctk.IntVar | ctk.DoubleVar = None, font: ctk.CTkFont | None = None, width: int | None = None,
                 justify: Literal['right', 'center', 'left'] | None = None):
        super().__init__(master)
        self.start = start
        self.end = end
        self.inc = increment
        self.scroll_inc = scroll_inc or increment
        self.variable = variable or (
            ctk.DoubleVar(value=start) if isinstance(increment, float) else ctk.IntVar(value=start)
        )
        self.font = font
        self.justify = justify
        self.width = width
        self.repeat_delay = 400
        self.repeat_interval = 100
        # Continuous press state
        self._repeat_job = None
        self._repeat_func = None
        # Determine how many decimal places to display for floats
        self.decimals = self._get_decimal_places(increment)

        self.widgets()
        self.update_entry()

    def widgets(self):
        self.sub_btn = ctk.CTkButton(self, text='-', width=25, height=15, command=self.decrement)
        self.sub_btn.pack(side=ctk.LEFT, padx=(0, 2))
        self.sub_btn.bind("<ButtonPress-1>", lambda e: self._start_repeat(self.decrement))
        self.sub_btn.bind("<ButtonRelease-1>", lambda e: self._stop_repeat())
        self.entry = ctk.CTkEntry(self, width=self.width, height=15, textvariable=self.variable, font=self.font, justify=self.justify)
        self.entry.pack(side=ctk.LEFT)
        self.add_btn = ctk.CTkButton(self, text='+', width=25, height=15, command=self.increment)
        self.add_btn.pack(side=ctk.LEFT, padx=(2, 0))
        self.add_btn.bind("<ButtonPress-1>", lambda e: self._start_repeat(self.increment))
        self.add_btn.bind("<ButtonRelease-1>", lambda e: self._stop_repeat())
        # Keyboard + mouse bindings
        self.entry.bind("<MouseWheel>", self.on_scroll)
        self.entry.bind("<Up>", lambda e: self.increment())
        self.entry.bind("<Down>", lambda e: self.decrement())
        self.entry.bind("<Return>", lambda e: self.update_entry())
        self.entry.bind("<FocusOut>", lambda e: self.update_entry())

    def increment(self):
        """Increase value by increment."""
        value = float(self.variable.get()) + self.inc
        if value <= self.end:
            self.variable.set(round(value, self.decimals))
        self.update_entry()

    def decrement(self):
        """Decrease value by increment."""
        value = float(self.variable.get()) - self.inc
        if value >= self.start:
            self.variable.set(round(value, self.decimals))
        self.update_entry()

    def update_entry(self):
        """Validate and format the value in the entry."""
        try:
            value = float(self.variable.get())
        except ValueError:
            value = self.start
        value = min(max(value, self.start), self.end)
        self.variable.set(round(value, self.decimals))
    
    def on_scroll(self, event):
        """Handle mouse wheel scroll."""
        delta = self.scroll_inc if event.delta > 0 else -self.scroll_inc
        new_val = float(self.variable.get()) + delta
        new_val = min(max(new_val, self.start), self.end)
        self.variable.set(round(new_val, self.decimals))
        self.update_entry()
    
    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            else:
                return self.entry.get()
        except TypeError:
            return ""
    
    # -----------------------------
    # Continuous press handling
    # -----------------------------
    def _start_repeat(self, func):
        """Begin repeating increment/decrement when button is held."""
        self._repeat_func = func
        func()
        self._repeat_job = self.after(self.repeat_delay, self._do_repeat)

    def _do_repeat(self):
        """Perform repeat action."""
        if self._repeat_func:
            self._repeat_func()
            self._repeat_job = self.after(self.repeat_interval, self._do_repeat)

    def _stop_repeat(self):
        """Stop repeating when button is released."""
        if self._repeat_job:
            self.after_cancel(self._repeat_job)
            self._repeat_job = None
        self._repeat_func = None

    def _get_decimal_places(self, number: float) -> int:
        """Determine how many decimal places to display based on increment precision."""
        s = str(number)
        return len(s.split('.')[1]) if '.' in s else 0

class CTkLabelFrame(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, font: ctk.CTkFont | None = None, label: float | str = "", background: str | Tuple[str, str] = "transparent",
                 foreground: str | Tuple[str, str] | None = None, labelanchor: Literal['n', 'ns', 'ne', 'nw', 's', 'se', 'sw', 'e', 'ew', 'w'] = 'nw',
                 border_width: int | float | str | None = 2, border_color: str | Tuple[str, str] = "#ffffff", width: int = 0, height: int = 0,
                 label_bg: str | Tuple[str, str] = "transparent", label_fg: str | Tuple[str, str] | None = "#ffffff", corner_radius: int | str | None = None,
                 **kwargs):
        super().__init__(master, width=width, height=height, border_width=border_width, border_color=border_color, bg_color=background,
                         fg_color=foreground, corner_radius=corner_radius, **kwargs)
        # ----- Attributes -----
        self.label = label
        self.font = font
        self.labelanchor = labelanchor
        self.labelbg = label_bg
        self.labelfg = label_fg
        self.corner_radius = corner_radius
        self.internal_padx = 8
        self.internal_pady = (3, 8)

        self.lbl = ctk.CTkLabel(self,
                           text=self.label,
                           fg_color=self.labelbg,
                           text_color=self.labelfg,
                           font=self.font,
                           height=15,
                           corner_radius=corner_radius,
                           anchor=self.labelanchor)
        self.lbl.pack(side='top', fill='x', padx=2, pady=2)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        self._apply_internal_padding()

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        self._apply_internal_padding()
    
    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self._apply_internal_padding()
    
    def _apply_internal_padding(self):
        """Apply internal padding to avoid label overlap."""
        self.grid_propagate(False)
        self.pack_propagate(True)

        # Add internal padding automatically
        for slave in self.winfo_children():
            if slave != self.lbl:
                slave.pack_configure(padx=self.internal_padx, pady=self.internal_pady)

class RuleList(ctk.CTkFrame):
    def __init__(self, master, on_edit: Callable, on_remove: Callable, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # ----- Attributes -----
        self.on_edit = on_edit
        self.on_remove = on_remove
        self.rule_widgets = []

        self._create_widgets()

    def _create_widgets(self):
        """Create scrollable area for rule list."""
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", orientation='horizontal')
        self.scroll_frame.pack(fill="both", expand=True, padx=4, pady=4)

    def refresh(self, rules: List):
        """Rebuild rule list UI."""
        # Clear old widgets
        for widget in self.rule_widgets:
            widget.destroy()
        self.rule_widgets.clear()

        # Add a row for each rule
        for i, rule in enumerate(rules):
            row = ctk.CTkFrame(self.scroll_frame)
            row.pack(fill="x", pady=3, padx=2, ipady=4)

            # Checkbox for enabling/disabling
            var = ctk.BooleanVar(value=getattr(rule, "enabled", True))
            chk = ctk.CTkCheckBox(
                row,
                text=f"{rule.type} - {rule.params}",
                variable=var,
                command=lambda r=rule, v=var: self._toggle_rule(r, v),
                width=300,
            )
            chk.pack(side="left", padx=(8, 4), expand=True, fill="x")

            # Edit Button
            edit_btn = ctk.CTkButton(
                row,
                text="Edit",
                width=50,
                height=25,
                command=lambda idx=i: self.on_edit(idx)
            )
            edit_btn.pack(side="right", padx=4)

            # Remove Button
            rm_btn = ctk.CTkButton(
                row,
                text="X",
                width=25,
                height=25,
                fg_color="red",
                hover_color="#a00",
                command=lambda idx=i: self.on_remove(idx)
            )
            rm_btn.pack(side="right", padx=4)

            self.rule_widgets.append(row)

    def _toggle_rule(self, rule, var: ctk.BooleanVar):
        """Toggle rule on/off."""
        rule.enabled = var.get()
