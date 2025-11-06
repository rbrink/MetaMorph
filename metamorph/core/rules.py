import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class RenameRule:
    """ Data class representing a single renaming rule. """
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"{self.type} {self.params}"

def split_name_ext(path: Path):
    """ Split filename into name and extension(s) """
    return path.stem, path.suffix.lstrip('.')

def format_date(path: Path, fmt: str):
    """ Format file date based on given format string """
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts).strftime(fmt)
    except Exception:
        return datetime.now().strftime(fmt)
    
def apply_tags(template: str, path: Path, seqnum: int | None = None, metadata: dict | None = None):
    name, ext = path.stem, path.suffix.lstrip('.')
    result = template.replace('{name}', name).replace('{ext}', ext)
    # Date substitution
    result = re.sub(r'\{date:([^}]+)\}', lambda m: format_date(path, m.group(1)), result)

    # Sequential numbering
    result = re.sub(r'\{num(?::(\d+))?\}', lambda m: str(seqnum).zfill(int(m.group(1))) if seqnum and m.group(1) else str(seqnum or ''), result)

    # Metadata substitution (standard keys and CSV)
    if metadata:
        # Normal metadata fields
        for key, value in metadata.items():
            result = re.sub(rf'\{{{re.escape(key)}(?::(\d+))?\}}', lambda m: str(value).zfill(int(m.group(1))) if m.group(1) else str(value), result)

    # CSV column substitution {Csv:1} or {Csv:Header}
    result = re.sub(r'\{Csv:([^}]+)\}', lambda m: str(metadata.get(f'Csv:{m.group(1)}', '')), result)

    return result

def apply_rule_to_path(rule: RenameRule, path: Path, seqnum: Optional[int]=None, metadata: Optional[Dict[str,Any]]=None) -> Path:
    original_name = path.stem
    original_ext = path.suffix
    target_name = original_name
    t = rule.type.lower()

    if t == "replace":
        old = rule.params.get("old", "")
        new = rule.params.get("new", "")
        if rule.params.get("use_tags", False):
            new = apply_tags(new, path, seqnum)
        if rule.params.get("case_sensitive", True):
            target_name = target_name.replace(old, new)
        else:
            target_name = re.sub(re.escape(old), new, target_name, flags=re.IGNORECASE)

    elif t == "change_case":
        mode = rule.params.get("mode", "lower")
        if mode == "lower":
            target_name = target_name.lower()
        elif mode == "upper":
            target_name = target_name.upper()
        elif mode == "title":
            target_name = target_name.title()
        elif mode == "capitalize":
            target_name = target_name.capitalize()

    elif t == "prefix_suffix":
        prefix = rule.params.get("prefix", "")
        suffix = rule.params.get("suffix", "")
        if rule.params.get("use_tags", False):
            prefix = apply_tags(prefix, path, seqnum)
            suffix = apply_tags(suffix, path, seqnum)
        target_name = f"{prefix}{target_name}{suffix}"

    elif t == "numbering":
        template = rule.params.get("template", "{name}_{num:3}")
        target_name = apply_tags(template, path, seqnum)
    elif t in ("custom_template", "new_name"):
        template = rule.params.get("template", "{Csv:1}")
        target_name = apply_tags(template, path, seqnum, metadata)
        target_name = sanitize_filename(target_name)
        new_ext = ""  # extension comes from template, so don’t append original
        return path.with_name(target_name)

    # extension change
    new_ext = original_ext
    if t == "change_ext":
        new_ext_val = rule.params.get("ext", "")
        if new_ext_val.startswith("."):
            new_ext = new_ext_val
        else:
            new_ext = "." + new_ext_val if new_ext_val else ""

    return path.with_name(sanitize_filename(target_name + new_ext))

def sanitize_filename(name: str) -> str:
    # Replace characters invalid on Windows + generally problematic
    return re.sub(r'[<>:"/\\|?*]', "_", name)
