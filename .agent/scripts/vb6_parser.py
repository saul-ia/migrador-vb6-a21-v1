import re
import json
import sys
import os

def parse_frm(file_path):
    """
    Simulates parsing a VB6 .frm file to extract controls.
    Real implementation would use a proper grammar parser.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    controls = []
    with open(file_path, 'r', encoding='latin1') as f:
        content = f.read()

    # Naive Regex for demonstration
    # Begin VB.CommandButton cmdSave
    matches = re.findall(r'Begin VB\.(\w+) (\w+)', content)
    
    for type_name, name in matches:
        controls.append({
            "type": type_name,
            "name": name,
            "migrated_type": map_type(type_name)
        })

    return {"file": os.path.basename(file_path), "controls": controls}

def map_type(vb_type):
    mapping = {
        "CommandButton": "MatButton",
        "TextBox": "MatInput",
        "Label": "MatLabel",
        "CheckBox": "MatCheckbox"
    }
    return mapping.get(vb_type, "Unknown")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vb6_parser.py <path_to_frm>")
        sys.exit(1)
    
    result = parse_frm(sys.argv[1])
    print(json.dumps(result, indent=2))
