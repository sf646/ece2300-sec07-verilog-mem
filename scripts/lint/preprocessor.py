#!/usr/bin/env python3
"""
Verilog Construct Checker
Scans Verilog files for prohibited constructs defined directly within this script.
Properly handles single-line and multi-line comments.
"""

import re
import argparse
import sys
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import os
import sys

# --- Configuration: Prohibited Constructs ---
# This dictionary contains all the rules for prohibited Verilog constructs.
# To add a new rule:
# 1. Find the appropriate category (e.g., 'data_types', 'statements').
# 2. Add a new dictionary to the list for that category.
# 3. The dictionary should have two keys:
#    - 'pattern': A raw string (r'...') containing the regular expression to match.
#    - 'description': A user-friendly message explaining why the construct is prohibited.
#
# Note: All patterns are treated as case-insensitive regular expressions.
# Use `\b` for word boundaries to avoid matching substrings (e.g., `\breg\b` won't match `register`).

PROHIBITED_CONSTRUCTS = {
    
    # Data Types & Declarations
    'data_types': [
        {'pattern': r'\breg\b', 'description': 'Legacy `reg` declarations are prohibited; use `logic`'},
        {'pattern': r'\binteger\b', 'description': '`integer` is a 32-bit signed variable, often unsynthesizable; use sized, signed `logic` instead'},
        {'pattern': r'\breal\b', 'description': '`real` type is not synthesizable'},
        {'pattern': r'\btime\b', 'description': '`time` type is not synthesizable'},
        {'pattern': r'\brealtime\b', 'description': '`realtime` type is not synthesizable'},
    ],
    
    # Operators
    'operators': [
    #    {'pattern': r'===',  'description': 'Case equality operator (===) is not synthesizable; use =='},
        {'pattern': r'!==',  'description': 'Case inequality operator (!==) is not synthesizable; use !='},
        {'pattern': r'/',    'description': 'Division operator (/) is prohibited'},
        {'pattern': r'%',    'description': 'Modulo operator (%) is prohibited'},
        {'pattern': r'\*\*', 'description': 'Power operator (**) is prohibited'},
    ],
    
    # Statements & Constructs (often for synthesizability)
    'statements': [
        {'pattern': r'\binitial\b', 'description': '`initial` blocks are generally not synthesizable for FPGA/ASIC logic'},
        {'pattern': r'#\d+', 'description': 'Delay statements (#delay) are for simulation only and are not synthesizable'},
        {'pattern': r'<=\s*#', 'description': 'Delayed non-blocking assignments are not synthesizable'},
        {'pattern': r'=\s*#', 'description': 'Delayed blocking assignments are not synthesizable'},
        {'pattern': r'\bcasex\b', 'description': '`casex` can cause simulation-synthesis mismatches due to its handling of X values'},
        {'pattern': r'\bfor\b', 'description': 'Synthesizable `for` loops must have constant bounds; often better to use `generate for` for replication'},
        {'pattern': r'\bwhile\b', 'description': '`while` loops are generally not synthesizable'},
        {'pattern': r'\brepeat\b', 'description': '`repeat` loops are generally not synthesizable'},
        {'pattern': r'\bforever\b', 'description': '`forever` loops are not synthesizable'},
        {'pattern': r'\bfork\b', 'description': '`fork`/`join` constructs are for simulation and not synthesizable'},
        {'pattern': r'\bjoin\b', 'description': '`fork`/`join` constructs are for simulation and not synthesizable'},
        {'pattern': r'\bdeassign\b', 'description': '`deassign` is not synthesizable'},
        {'pattern': r'\bforce\b', 'description': '`force` and `release` are for simulation/testbenches only'},
        {'pattern': r'\brelease\b', 'description': '`force` and `release` are for simulation/testbenches only'},
        {'pattern': r'\bspecify\b', 'description': '`specify` blocks are for simulation timing and are not for synthesis'},
        {'pattern': r'\bdefparam\b', 'description': '`defparam` is a legacy construct; use parameterized modules instead'},
    ],
    
    # Port & Sensitivity
    'port_sensitivity': [
        {'pattern': r'\binout\b', 'description': '`inout` ports are complex and often discouraged; use separate input and output ports with a mux'},
        {'pattern': r'\bnegedge\b', 'description': 'Negative edge-triggered logic is uncommon and can complicate timing analysis'},
    ],
    
    # Deprecated or Non-Synthesizable Constructs
    'gate_instances': [
        {'pattern': r'\b(nmos|pmos|cmos|rnmos|rpmos|rcmos)\b', 'description': 'Transistor-level primitives are not for general synthesis'},
        {'pattern': r'\b(tran|tranif0|tranif1|rtran|rtranif0|rtranif1)\b', 'description': 'Transfer-gate primitives are not for general synthesis'},
    ],
    'net_types': [
        {'pattern': r'\b(supply0|supply1|tri|triand|trior|tri0|tri1)\b', 'description': 'Legacy net types are prohibited; use `logic` and connect to 1\'b0 or 1\'b1'},
    ],
}

def preprocess_code(verilog_code: str) -> str:
        output = []
        in_multiline, in_string, i, n = False, False, 0, len(verilog_code)
        while i < n:
            if in_multiline:
                if verilog_code[i:i+2] == '*/': in_multiline = False; i += 2
                else:
                    if verilog_code[i] == '\n': output.append('\n')
                    i += 1
                continue
            if in_string:
                if verilog_code[i] == '"' and (i == 0 or verilog_code[i-1] != '\\'): in_string = False; output.append('"'); i += 1
                elif verilog_code[i] == '\\' and i + 1 < n: output.append('  '); i += 2
                else: output.append(' ' if verilog_code[i] != '\n' else '\n'); i += 1
                continue
            if verilog_code[i:i+2] == '//': i = verilog_code.find('\n', i); i = n if i == -1 else i; continue
            if verilog_code[i:i+2] == '/*': in_multiline = True; i += 2; continue
            if verilog_code[i] == '"': in_string = True; output.append('"'); i += 1; continue
            output.append(verilog_code[i]); i += 1
        return "".join(output)

class VerilogChecker:
    def __init__(self):
        self.prohibited_constructs = PROHIBITED_CONSTRUCTS

    def _check_constructs(self, clean_code: str, filename: str) -> List[Dict]:
        errors = []
        lines = clean_code.split('\n')
        for category, patterns_info in self.prohibited_constructs.items():
            for rule in patterns_info:
                pattern, description = rule.get('pattern', ''), rule.get('description', f"Prohibited construct: {rule.get('pattern', '')}")
                if not pattern: continue
                try:
                    regex = re.compile(pattern, re.IGNORECASE)
                    for line_num, line in enumerate(lines, 1):
                        for match in regex.finditer(line):
                            errors.append({'file': filename, 'line': line_num, 'column': match.start() + 1, 'construct': match.group(), 'description': description, 'line_content': line.strip()})
                except re.error as e:
                    print(f"Warning: Invalid regex pattern '{pattern}' in category '{category}': {e}", file=sys.stderr)
        return errors
    
    def check_content(self, verilog_content: str, filename: str) -> List[Dict]:
        """
        Checks a string of Verilog content for prohibited constructs.
        
        Args:
            verilog_content (str): The Verilog code to check.
            filename (str): The original filename, for reporting purposes.

        Returns:
            List[Dict]: A list of error dictionaries found in the content.
        """
        # Preprocess to remove comments/strings before checking
        processed_content = preprocess_code(verilog_content)
        # Run the checks on the preprocessed content
        return self._check_constructs(processed_content, filename)

#--------------------
# Helper functions
#--------------------

def find_include_file(filename, include_dir):
    for i in include_dir:
        test = Path(os.path.join(i, filename)).resolve()
        if test.is_file():
            return test

    print(f"Warning: Could not find included file '{filename}' in any include directory.", file=sys.stderr) 
    return None

def extract_included_modules(file_content: str) -> Optional[List[str]]:
    """
    Parses for the special `// ece2300-lint` or `// ece2300-lint off` comments.
    Returns: List of Modules if found
    Returns: Empty List if `ece2300-lint off` is found
    Returns: None if no special comment is found
    """
        
    # # # Remove tha labN tags before an import
    # include_pattern = re.compile(r'include\s+"lab\d+/(.*?)"')  
    # file_content = include_pattern.sub(r'include "\1"', file_content)

    # Look for ece2300-lint off comment (returns empty list)
    off_pattern = re.compile(r"//\s*ece2300-lint\s+off", re.IGNORECASE)
    if off_pattern.search(file_content):
        return []
    
    # Look for ece2300-lint comment followed by include line
    lint_pattern = re.compile(r"//\s*ece2300-lint\s*\n\s*`include\s+\"([^\"]+)\"", re.IGNORECASE)
    lint_match = lint_pattern.search(file_content)
    
    if lint_match:
        module_name = lint_match.group(1)
        return [module_name]
    
    # If neither comment is present, return None
    return None

def extract_all_includes(file_content: str) -> List[str]:
    """Finds all `include` statements in a file's content."""
    return re.findall(r'`include\s+"([^"]+)"', file_content)

def preprocess_unparsable_file(content: str) -> str:
    """
    Special preprocessing for the TinyRV1 file.
    This function removes the body of the module definition
    """
    module_pattern = re.compile(r'(\bmodule\b\s+\w+\s*\(.*?\);)(.*?)(endmodule)', re.DOTALL)
    
    def replace_body(match):
        module_declaration = match.group(1)
        empty_content = '\n // Module content removed during preprocessing\n'
        endmodule = match.group(3)
        return module_declaration + empty_content + endmodule
    
    processed_content = module_pattern.sub(replace_body, content)
    return processed_content    

def clean_and_save_file(source_path: Path, build_dir: Path, cannot_parse: bool = False) -> Optional[Tuple[Path, str]]:
    """
    Cleans a file, saves it, and returns the destination path and cleaned content.
    If the can_parse flag is set, it preprocesses the file by removing the entire body of the module
    """

    pattern_to_remove = re.compile(r"\(\*\s*keep\s*=\s*1\s*\*\)")
    # Remove specific macros
    ece2300_macro_pattern = re.compile(
        r'^\s*`ECE2300_(?:UNUSED|UNDRIVEN)\s*\([^)]*\)\s*;\s*(?:\/\/.*)?$',
        re.MULTILINE
    )
    # Turn any include filtpath to just an include module
    # `include "lab3/foo/bar/baz.v"   ->  `include "baz.v"    
    include_pattern = re.compile(r'`include\s+"(?:.*/)?([^/"]+)"')

    # Remove the ECE2300 Macro
    ece2300_xprop_pattern = re.compile(
        r'^\s*`ECE2300(?:_SEQ)?(?:_XPROP)?\d*\s*'   # macro name
        r'\(\s*[^,]+,\s*.+?\)\s*;'                  # 2 arguments inside (...)
        r'\s*(?:\/\/.*)?$',                         # optional trailing comment
        re.MULTILINE
    )

    dest_path = build_dir /  source_path.name
    try:
        original_content = source_path.read_text(encoding='utf-8')
        cleaned_content = pattern_to_remove.sub('', original_content)
        cleaned_content = ece2300_macro_pattern.sub('', cleaned_content)
        cleaned_content = ece2300_xprop_pattern.sub('', cleaned_content)

        # Change the import statements from labN/module to just module
        cleaned_content = include_pattern.sub(r'`include "\1"', cleaned_content)

        if cannot_parse:
            cleaned_content = preprocess_unparsable_file(cleaned_content)
        
        dest_path.write_text(cleaned_content, encoding='utf-8')
        return dest_path, cleaned_content
    except IOError as e:
        print(f"Error processing file {source_path}: {e}", file=sys.stderr)
        return None

MODULE_BLOCK_REGEX = re.compile(
    r'\bmodule\s+([a-zA-Z_]\w*)\b(.*?)\bendmodule\b',
    flags=re.DOTALL
)
XPROP_MACRO_REGEX = re.compile(
    r"`ECE2300(?:_XPROP)?\d*\s*\(\s*([^,]+)\s*,\s*(?:[^)]+)\s*\)"
)
SEQ_XPROP_MACRO_REGEX = re.compile(
    r"`ECE2300_SEQ(?:_XPROP)?\d*\s*\(\s*([^,]+)\s*,\s*(?:[^)]+)\s*\)"
)

def extract_module_xprop_signals_from_file(file_content):
    """
    Parses a file's content by finding module blocks and extracts XPROP signals from each.
    
    Returns:
        A dictionary mapping each found module name to its list of XPROP signals.
    """
    comb_results: Dict[str, List[str]] = {}
    seq_results: Dict[str, List[str]] = {}

    # Pre-process to remove comments
    content_no_comments = preprocess_code(file_content)
    
    # Use finditer to find all module ... endmodule blocks
    for match in MODULE_BLOCK_REGEX.finditer(content_no_comments):

        # group(1) is the module name from our regex: ([a-zA-Z_]\w*)
        module_name = match.group(1)
        
        # The entire matched text (the module block)
        module_body = match.group(2)
        
        # Now, find all XPROP signals within this specific module's body
        comb_signals = XPROP_MACRO_REGEX.findall(module_body)

        # Find all the Sequential XPROP signals
        seq_signals = SEQ_XPROP_MACRO_REGEX.findall(module_body)

        if comb_signals:
            if module_name not in comb_results:
                comb_results[module_name] = []
            comb_results[module_name].extend(comb_signals)
        
        if seq_signals:
            if module_name not in seq_results:
                seq_results[module_name] = []
            seq_results[module_name].extend(seq_signals)
            
    return comb_results, seq_results

def main(args_list=None) -> Tuple[List[str], Dict[str, List[str]]]:
    parser = argparse.ArgumentParser(description='Recursively clean and check Verilog files and their dependencies.')
    parser.add_argument('file', help='The top-level Verilog file or include list to start processing.')
    parser.add_argument('-I', '--include-dir', action='append', default=[],
                       help='Directory to search for included files. Can be specified multiple times.')
    parser.add_argument('--temp-dir', default='temp', help='Temporary directory for intermediate files. Defaults to "temp".')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose error output.')
    parser.add_argument('-t', '--test', action='store_true', default=False, help='Run tests instead of linting a file.')
    
    args = parser.parse_args(args_list)

    #--------------------------------------
    # Setup
    #--------------------------------------

    initial_file = Path(args.file).resolve()
    if not initial_file.is_file():
        print(f"Error: Initial file not found: {initial_file}", file=sys.stderr)
        sys.exit(1)

    temp_dir = Path(args.temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    #--------------------------------------
    # Get top level files
    # These are the files we actually want
    # to lint. We need to preprocess many
    # files just to lint the top level
    #--------------------------------------

    top_level = set()
    # Extract the file we want to lint
    input_file = extract_included_modules(initial_file.read_text(encoding='utf-8'))
    if input_file:
        # If a special comment was found, add the module name to the top level
        for file_path in input_file:
            basename = os.path.basename(file_path)
            top_level.add((basename, file_path))
    elif input_file is not None:
        # Exit here no linting will be done
        return ([], {})
    else:
        # If no special comment is found, just add the initial file
        top_level.add((os.path.basename(initial_file), initial_file))

    #--------------------------------------
    # Processing all the files
    #--------------------------------------

    # Get the filepath of the module we want to process, should be only a single file
    # TODO: update datastructures used now that we have a single file
    path = None
    for item in top_level:
        path = find_include_file(item[1], args.include_dir)
    
    # Creates datastructures for processing
    files_to_process_q = deque([path])
    visited_paths: Set[Path] = {path}
    all_errors: Dict[str, List[Dict]] = {}

    # This will hold the final paths of the cleaned files in the temporary directory
    final_build_paths: List[str] = []
    # This will hold all the xprop signals found in the modules
    module_to_xprop_signals: Dict[str, List[str]] = {} 
    module_to_xprop_seq_signals : Dict[str, List[str]] = {}
    checker = VerilogChecker()
    
    while files_to_process_q:
        current_path = files_to_process_q.popleft()
        
        try:
            content = current_path.read_text(encoding='utf-8')
        except IOError as e:
            print(f"Error reading file {current_path}: {e}", file=sys.stderr)
            continue # Skip to the next file in the queue
        
        # Get the xprop for the current file
        comb_signals_in_file, seq_signals_in_file = extract_module_xprop_signals_from_file(content)

        # Add to comb dictonary
        if comb_signals_in_file:
            for module, signals in comb_signals_in_file.items():
                if module not in module_to_xprop_signals:
                    module_to_xprop_signals[module] = []
                module_to_xprop_signals[module].extend(signals)
        
        # Add to seq dictonary
        if seq_signals_in_file:
            for module, signals in seq_signals_in_file.items():
                if module not in module_to_xprop_seq_signals:
                    module_to_xprop_seq_signals[module] = []
                module_to_xprop_seq_signals[module].extend(signals)
        
        # We never check for comments again because this shouldnt happen
        # The only module that should have comments is the test files and 
        # test files should not reference each other so we can safely ignore them
        # We are assuming these modules are normal and can be parsed

        # Check if this file contains Any Unparsable modules
        current_file_has_tinyRV1 = 'tinyrv1' in os.path.basename(current_path)
        current_file_has_ProcScycleCtrl = 'ProcScycleCtrl' in os.path.basename(current_path)
        current_file_has_ProcSimpleCtrl = 'ProcSimpleCtrl' in os.path.basename(current_path)

        can_parse = current_file_has_tinyRV1 or current_file_has_ProcScycleCtrl or current_file_has_ProcSimpleCtrl

        result = clean_and_save_file(current_path, temp_dir, cannot_parse=can_parse)
        if not result:
            continue # Error during clean/save

        dest_path, cleaned_content = result
        final_build_paths.append(str(dest_path))
        
        # Check the cleaned content (skip checking for Non parsable files since content was removed)
        if not can_parse:
            errors = checker.check_content(cleaned_content, str(current_path))
            if errors:
                all_errors[str(current_path)] = errors
        
        # Find its dependencies for further processing
        includes_to_add = extract_all_includes(content)

        # Add newly found dependencies to the queue if they haven't been seen
        for include_name in includes_to_add:
            found_path = find_include_file(include_name, args.include_dir)
            if found_path and found_path not in visited_paths:
                visited_paths.add(found_path)
                files_to_process_q.append(found_path)

    # --- Final Reporting ---
    total_errors = sum(len(errs) for errs in all_errors.values())

    if total_errors > 0:
        print(f"Found {total_errors} prohibited construct(s) in the cleaned files.\n")
        for file, errors in all_errors.items():
            for error in errors:
                print(f"{file}:{error['line']}:{error['column']}: {error['description']} ('{error['construct']}')")
        # We want to allow the linter to run and report errors during testing
        if not args.test:
            sys.exit(1)
    first_elements = [t[0] for t in top_level]
    final_build_paths = [ item for item in final_build_paths if os.path.basename(item) in first_elements]
    return (final_build_paths, module_to_xprop_signals, module_to_xprop_seq_signals)
    
def cli():
    try:
        processed_paths = main()
        print(processed_paths)  # stdout usable for scraping
        sys.exit(0)
    except SystemExit as e:
        sys.exit(e.code)

if __name__ == '__main__':
    cli()