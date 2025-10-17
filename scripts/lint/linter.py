import sys
import os
import argparse
import yaml
import re
import pathlib
import json
from typing import List, Optional
from lint.lint_rules import Rules
import pyverilog
from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import *
from pyverilog.dataflow.visit import NodeVisitor

XPROP_MACRO_REGEX = re.compile(r"`ECE2300_XPROP\d*\s*\(\s*(\w+)")

def load_lint_config(config_filepath='lint/lint_config.yaml'):
    """
    Load and resolve lint rules from a YAML file with support for recursive rule-set expansion.

    Structure:
    rule-sets:
      base:
        - rule1
        - rule2
      extended:
        - base
        - rule3

    modules:
      mod1:
        - extended
        - ruleX
      mod2: extended

    Output:
    {
      'mod1': ['rule1', 'rule2', 'rule3', 'ruleX']
    }
    """
    final_config = {}

    if not os.path.exists(config_filepath):
        print(os.getcwd())
        print(f"Info: Config file '{config_filepath}' not found.", file=sys.stderr)
        return final_config

    try:
        with open(config_filepath, 'r') as f:
            user_config = yaml.safe_load(f)

        if not isinstance(user_config, dict):
            raise ValueError("Config file must be a YAML dictionary.")

        rule_sets = user_config.get('rule-sets', {})
        modules = user_config.get('modules', {})

        if not isinstance(rule_sets, dict) or not isinstance(modules, dict):
            raise ValueError("'rule-sets' and 'modules' must be dictionaries.")

        def resolve_rule_set(name, seen=None):
            if seen is None:
                seen = set()
            if name in seen:
                return []
            seen.add(name)

            result = set()
            rules = rule_sets.get(name, [])
            if not isinstance(rules, list):
                print(f"Warning: Rule set '{name}' is not a list. Skipping.", file=sys.stderr)
                return result

            for item in rules:
                if item in rule_sets:
                    result.update(resolve_rule_set(item, seen))
                else:
                    result.add(item)
            return result

        for module, items in modules.items():
            # If items is a string, convert to list
            if isinstance(items, str):
                items = [items]

            if not isinstance(items, list):
                print(f"Warning: Module '{module}' should map to a list or a single string. Skipping.", file=sys.stderr)
                continue

            resolved_rules = set()
            for item in items:
                if item in rule_sets:
                    resolved_rules.update(resolve_rule_set(item))
                else:
                    resolved_rules.add(item)

            final_config[module] = sorted(resolved_rules)

    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file '{config_filepath}': {e}.", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error loading config file '{config_filepath}': {e}.", file=sys.stderr)

    return final_config

LINT_CONFIG = {} # Will be populated by load_lint_config in main

def is_x_assignment(assignment_node):
    """
    Checks if an assignment node is an 'x' assignment.
    """
    #There is no assignment (it would have to be one of the two)
    if not isinstance(assignment_node, (NonblockingSubstitution, BlockingSubstitution)):
        return False
    #Get right side
    rhs = assignment_node.right
    if (isinstance(rhs, Rvalue) and hasattr(rhs, 'var')):
        rhs = rhs.var   
    #If its an int use Regex to check if it is an x
    if isinstance(rhs, IntConst) or isinstance(rhs, UnsizedBitConst):
        val = rhs.value.lower()
        if val == 'x' or val == "'x": return True
        m = re.match(r"(\d*)?'([bBhHdDoOxX])([xXzZ?]+)$", val)
        if m:
            value_part = m.group(3)
            if all(c in 'xXzZ?' for c in value_part):
                return True
        if val in ("'bx", "'bX", "'bz", "'bZ", "'b?"): return True
 
    return False

class VerilogLinter(NodeVisitor):
    """
    A Pyverilog NodeVisitor subclass that performs linting checks on Verilog ASTs.
    It identifies violations based on the loaded configuration.
    """
    def __init__(self, config):
        super(VerilogLinter, self).__init__()
        #Just check if the config has the rule, if so the rule is present
        self.config = config
        #Ruleset for the specific module
        self.current_ruleset = []
        #Stores Violations
        self.violations = []

        #Tracks the module being processed
        self.current_module_name = None

        #Tracks the state of always_comb blocks
        self._in_always_comb = False

        #Tracks line number of always_comb block
        self._always_comb_lineno = -1

        #Set of signals that are assigned at the top of always_comb
        self._always_comb_top_level_full_defaults = set()

        #Set of signals that already have violations to prevent duplicates
        self._rule1_signals_flagged_in_current_always = set()

        #Xprop macro signals found in the current module
        self._xprop_macro_comb_out_signals_found_by_regex = set()
        self._xprop_macro_seq_out_signals_found_by_regex = set()

        self.current_module_xprop_comb = [] 
        self.current_module_xprop_seq = [] 

        self._conditionally_assigned_signals_info = {}

    def _add_violation(self, rule_class, node, **kwargs, ):
        """
        Adds violation if found

        rule_id: The ID of the rule that was violated.
        message: The message to display for the violation.
        lineno: The line number where the violation occurred.
        """
        if rule_class.name in self.current_ruleset:
            message = rule_class.error_message.format(**kwargs)
            v = (self.current_module_name, rule_class.name, message, node.lineno)
            if v not in self.violations:
                self.violations.append(v)

    def find_assignments_in_node(self, node, signal_name, found_assignments):
        """
        Finds all assignments associated with a given signal name in the AST node.
        node: The AST node to search within.

        signal_name: The name of the signal to search for.
        found_assignments: A list to append found assignment nodes.
        """
        #Basic substitution checks
        if isinstance(node, (BlockingSubstitution, NonblockingSubstitution)):
            assignments_info = self._get_assigned_lhs_info(node)
            for name, _, _ in assignments_info:
                if name == signal_name:
                    found_assignments.append(node)
        #Recursivley check children in block            
        elif isinstance(node, Block) and node.statements:
            for stmt in node.statements:
                self.find_assignments_in_node(stmt, signal_name, found_assignments)
        #Recursively check children in true and false statement        
        elif isinstance(node, IfStatement):
            if node.true_statement:
                self.find_assignments_in_node(node.true_statement, signal_name, found_assignments)
            if node.false_statement:
                self.find_assignments_in_node(node.false_statement, signal_name, found_assignments)
        #Check all branches of a Case statement        
        elif isinstance(node, CaseStatement) and node.caselist:
            for case_item in node.caselist:
                if case_item.statement:
                    self.find_assignments_in_node(case_item.statement, signal_name, found_assignments)
    
    def _get_assigned_lhs_info(self, statement_node):
        """
        Extract info about the left hand side of an assignment

        statement_node: The node to check

        Returns a set of tuples with (signal_name, type_of_assignment, line_number)
        """
        assigned_info = set()
        #Check if the statement is an assignment, if its not we dont care
        if not isinstance(statement_node, (NonblockingSubstitution, BlockingSubstitution)):
            return assigned_info
        #Check the left side
        lvalue = statement_node.left
        if isinstance(lvalue, Lvalue):
            #Get the value we want
            var_primary_node = lvalue.var
            
            if isinstance(var_primary_node, Concat):
                concat_info = self._extract_concat_signals(var_primary_node, statement_node.lineno)
                assigned_info.update(concat_info)
            else:
                base_name_node = var_primary_node

                #If the left side is a range/bit select we want the base name
                while hasattr(base_name_node, 'var') and not isinstance(base_name_node, Identifier):
                    if base_name_node == base_name_node.var: 
                        break
                    base_name_node = base_name_node.var
                
                #Need to add special case if LHS is a concatenation

                if isinstance(base_name_node, Identifier):
                    base_name = base_name_node.name
                    is_full_assignment = isinstance(var_primary_node, Identifier)
                    assign_type = 'full' if is_full_assignment else 'partial'
                    assigned_info.add((base_name, assign_type, statement_node.lineno))

        #Return name of the signal, type of assignment and line number
        return assigned_info
    
    def _extract_concat_signals(self, concat_node, line_number):
        """
        Recursively extract signals from a concatenation, handling nested concatenations
        
        concat_node: The Concat node to process
        line_number: Line number for tracking
        
        Returns a set of tuples: (signal_name, assign_type, line_number)
        where assign_type is 'full' or 'partial' based on whether the signal is bit/part selected
        """
        concat_signals = set()
        
        if not isinstance(concat_node, Concat):
            return concat_signals
        
        # Process each element in the concatenation
        for item in concat_node.list:
            if isinstance(item, Concat):
                # Nested concatenation - recurse
                nested_signals = self._extract_concat_signals(item, line_number)
                concat_signals.update(nested_signals)
            else:
                # Regular signal - extract base name and determine if full or partial
                base_name_node = item
                original_item = item  # Keep reference to original to check if it's an Identifier
                
                # Traverse to get base identifier (handle bit/part selects)
                while hasattr(base_name_node, 'var') and not isinstance(base_name_node, Identifier):
                    if base_name_node == base_name_node.var:
                        break
                    base_name_node = base_name_node.var
                
                if isinstance(base_name_node, Identifier):
                    base_name = base_name_node.name
                    # Check if this is a full assignment (original item is Identifier) or partial (bit/part select)
                    is_full_assignment = isinstance(original_item, Identifier)
                    assign_type = 'full' if is_full_assignment else 'partial'
                    concat_signals.add((base_name, assign_type, line_number))
        
        return concat_signals

    def _collect_all_lhs_in_statement_tree(self, statement_node, collected_lhs_info=None):
            """
            This function is for getting all the signal names assigned (both blocking and nonblocking) in a statement tree like ifs/cases

            statement_node: The node to start from
            collected_lhs_info: The set of signals already collected
            """
            if collected_lhs_info is None: collected_lhs_info = set()
            if statement_node is None: return collected_lhs_info

            #If there is a assignment, get the info using the normal method
            if isinstance(statement_node, (NonblockingSubstitution, BlockingSubstitution)):
                collected_lhs_info.update(self._get_assigned_lhs_info(statement_node))
            #This is a begin - end construct 
            elif isinstance(statement_node, Block):
                if statement_node.statements:
                    #Iterate through all statements in the block and collect using normal method (Assume they could be trees)
                    for stmt in statement_node.statements: self._collect_all_lhs_in_statement_tree(stmt, collected_lhs_info)
            #This is a If statement
            elif isinstance(statement_node, IfStatement):
                #Traverse the true statement first
                self._collect_all_lhs_in_statement_tree(statement_node.true_statement, collected_lhs_info)
                #If an else exists traverse that too
                if statement_node.false_statement: self._collect_all_lhs_in_statement_tree(statement_node.false_statement, collected_lhs_info)
            #this is for a case statement
            elif isinstance(statement_node, CaseStatement):
                #If there is a case statement, traverse all statemnets
                if statement_node.caselist:
                    for case_item in statement_node.caselist: self._collect_all_lhs_in_statement_tree(case_item.statement, collected_lhs_info)
            return collected_lhs_info

    def _find_blocking_assignments_in_statement(self, statement_node, blocking_assignments_found):
        """
        Recursively finds any blocking assignments within a statement tree.
        statement_node: The AST node of the statement to check.

        blocking_assignments_found: A list to append found BlockingSubstitution nodes.
        """
        if statement_node is None:
            return

        if isinstance(statement_node, BlockingSubstitution):
            blocking_assignments_found.append(statement_node)
        
        # Recursively check compound statements
        elif isinstance(statement_node, Block):
            if statement_node.statements:
                for stmt in statement_node.statements:
                    self._find_blocking_assignments_in_statement(stmt, blocking_assignments_found)
        elif isinstance(statement_node, IfStatement):
            self._find_blocking_assignments_in_statement(statement_node.true_statement, blocking_assignments_found)
            if statement_node.false_statement:
                self._find_blocking_assignments_in_statement(statement_node.false_statement, blocking_assignments_found)
        elif isinstance(statement_node, (CaseStatement, CasexStatement, CasezStatement)): # Covers all case types
            if statement_node.caselist:
                for case_item in statement_node.caselist:
                    self._find_blocking_assignments_in_statement(case_item.statement, blocking_assignments_found)
        #We dont allow this using the restrictions on the constructs so theoretically should not reach here
        elif isinstance(statement_node, ForStatement):
            self._find_blocking_assignments_in_statement(statement_node.statement, blocking_assignments_found)
        elif isinstance(statement_node, WhileStatement):
            self._find_blocking_assignments_in_statement(statement_node.statement, blocking_assignments_found)
        elif isinstance(statement_node, Repeat):
            self._find_blocking_assignments_in_statement(statement_node.statement, blocking_assignments_found)
        elif isinstance(statement_node, ForeverStatement):
             self._find_blocking_assignments_in_statement(statement_node.statement, blocking_assignments_found)
    
    def _find_nonblocking_assignments_in_statement(self, statement_node, nonblocking_assignments_found):
        """
        Recursively finds any non-blocking assignments within a statement tree.
        statement_node: The AST node of the statement to check.

        nonblocking_assignments_found: A list to append found NonblockingSubstitution nodes.
        """
        if statement_node is None:
            return

        if isinstance(statement_node, NonblockingSubstitution):
            nonblocking_assignments_found.append(statement_node)
        
        # Recursively check compound statements
        elif isinstance(statement_node, Block):
            if statement_node.statements:
                for stmt in statement_node.statements:
                    self._find_nonblocking_assignments_in_statement(stmt, nonblocking_assignments_found)
        elif isinstance(statement_node, IfStatement):
            self._find_nonblocking_assignments_in_statement(statement_node.true_statement, nonblocking_assignments_found)
            if statement_node.false_statement:
                self._find_nonblocking_assignments_in_statement(statement_node.false_statement, nonblocking_assignments_found)
        elif isinstance(statement_node, (CaseStatement, CasexStatement, CasezStatement)):
            if statement_node.caselist:
                for case_item in statement_node.caselist:
                    self._find_nonblocking_assignments_in_statement(case_item.statement, nonblocking_assignments_found)
        
        #We dont allow this using the restrictions on the constructs so theoretically should not reach here
        elif isinstance(statement_node, ForStatement):
            self._find_nonblocking_assignments_in_statement(statement_node.statement, nonblocking_assignments_found)
        elif isinstance(statement_node, WhileStatement): 
            self._find_nonblocking_assignments_in_statement(statement_node.statement, nonblocking_assignments_found)
        elif isinstance(statement_node, Repeat):
             self._find_nonblocking_assignments_in_statement(statement_node.statement, nonblocking_assignments_found)
        elif isinstance(statement_node, ForeverStatement):  
             self._find_nonblocking_assignments_in_statement(statement_node.statement, nonblocking_assignments_found)
    
    def _is_simple_netlist_target(self, target_node):
        """
        Checks if an LHS or RHS target is a simple Identifier or a Partselect of an Identifier.

        target_node: The AST node representing the variable part (e.g., from Lvalue.var or Rvalue.var).
        """
        if isinstance(target_node, Identifier):
            return True
        if isinstance(target_node, Partselect):
            # Ensure the base of the partselect is a simple Identifier
            if isinstance(target_node.var, Identifier):
                return True
        if isinstance(target_node, Pointer):      
            if isinstance(target_node.var, Identifier) and isinstance(target_node.ptr, IntConst):
                return True
        return False

    def _is_simple_literal_rhs(self, rhs_var_node):
        """
        Checks if the RHS is a simple literal (constant).

        Used for assignments like 'assign a = 1'b0;'
        """
        if isinstance(rhs_var_node, (IntConst, FloatConst, StringConst, UnsizedBitConst)):
            return True
        return False


    def generic_visit(self, node): 
        """
        Overrides the generic_visit method to handle different node types. Had to modify to be able traverse

        node: The node to visit.
        """
        #Tuples were causing issues with the original generic_visit
        if isinstance(node, tuple):
            for item in node:
                if item:
                   self.visit(item)
        elif hasattr(node, 'children') and callable(node.children):
            for c in node.children():
                self.visit(c)

    def visit_Source(self, node):
        """
        Visits the top-level 'Source' node of the AST.

        node: The source node to visit.
        """
        #Two possible structures of the AST
        #1. Description object -> list of defintions
        #2. Definitions list (no description object)

        if hasattr(node, 'description') and node.description:
            if hasattr(node.description, 'definitions') and node.description.definitions:
                 for item in node.description.definitions: self.visit(item)
        elif hasattr(node, 'definitions') and node.definitions:
             for item in node.definitions: self.visit(item)
        else:
            self.generic_visit(node)

    def visit_Definition(self, node):
        """
        Visiting of a defintion node

        node: The definition node to visit.
        """ 
        if node.definition: self.visit(node.definition)

    def visit_ModuleDef(self, node):
        """
        Visting Module definitions

        node: The module definition node to visit.
        """
        #Set the rules, if they are defined in the config get them, else just no rules
        if (node.name in self.config):
            self.current_ruleset = self.config.get(node.name)
        else:
            self.current_ruleset = []
        
        if (node.name in self._xprop_macro_comb_out_signals_found_by_regex):
            self.current_module_xprop_comb = self._xprop_macro_comb_out_signals_found_by_regex.get(node.name)
        else:
            self.current_module_xprop_comb = []
        
        if (node.name in self._xprop_macro_seq_out_signals_found_by_regex):
            self.current_module_xprop_seq = self._xprop_macro_seq_out_signals_found_by_regex.get(node.name)
        else:
            self.current_module_xprop_seq = []

        self.current_module_name = node.name
        #Reset signals 
        self._conditionally_assigned_signals_info = {}

        if node.items:
            for item in node.items:
                #The follow are our gate level checks, however since there is no longer a gate level rule, I need to check these rules individully
                if isinstance(item, (Always, Initial, Function, Task, GenerateStatement, SystemCall)):
                    self._add_violation(Rules.NOSPBLK, node, type=type(item).__name__,  name=node.name)
                #Go deeper into tree and visit children
                if isinstance(item, Always):
                    self.visit_Always(item) 
                elif not isinstance(item, Always):
                    self.visit(item)

        self.current_module_name = None

    def visit_Assign(self, node):
        #Gate-level assign check:
        #Case 1: assign signal_or_partselect = literal
        #Case 2: assign signal_or_partselect = signal_or_partselect
        #No other operations allowed on RHS.

        lhs_node = None
        rhs_node = None

        #Check if the item is a valid assign structure
        if node.left and isinstance(node.left, Lvalue) and node.left.var:
            lhs_node = node.left.var
        else:
            #Continue to check RHS if possible, but overall assign is invalid
            self._add_violation(Rules.BADLHS, node.left)
        
        if node.right and isinstance(node.right, Rvalue) and node.right.var:
            rhs_node = node.right.var
        else:
            self._add_violation(Rules.BADRHS, node.right)
            #LHS might have been checked, but overall assign is invalid

        if lhs_node and rhs_node:
            is_lhs_simple_target = self._is_simple_netlist_target(lhs_node)
            is_rhs_simple_target = self._is_simple_netlist_target(rhs_node)
            is_rhs_simple_literal = self._is_simple_literal_rhs(rhs_node)

            if not is_lhs_simple_target:
                self._add_violation(Rules.COMPLEXLHS, node.left, type=type(lhs_node).__name__)
            
            if is_lhs_simple_target:
                if not (is_rhs_simple_target or is_rhs_simple_literal):
                    # RHS is not a simple target and not a simple literal, so it must be complex
                    detail_msg = f"is not a simple signal, part-select, or literal. Found type: {type(rhs_node).__name__}"
                    if isinstance(rhs_node, (Operator, UnaryOperator, Concat, Repeat, Pointer, FunctionCall, SystemCall)):
                        detail_msg = f"contains an operation or complex construct ({type(rhs_node).__name__})"
                    self._add_violation(Rules.COMPLEXRHS, node, detail_msg=detail_msg)
    
    def visit_InstanceList(self, node):
        ALLOWED_GATES = {'and', 'or', 'not', 'xor', 'nand', 'nor', 'xnor'}
        DISALLOWED_GATES = {
            # Switch-level primitives
            'tran', 'tranif0', 'tranif1',
            'rtran', 'rtranif0', 'rtranif1',
            'nmos', 'pmos', 'rnmos', 'rpmos',
            'cmos', 'rcmos',

            # Supply primitives
            'supply0', 'supply1',

            # Pull devices
            'pullup', 'pulldown', 'pull0', 'pull1',

            # Enable gates / buffers
            'buf', 'bufif0', 'bufif1',
            'notif0', 'notif1',

            # Strength and high impedance (used in some contexts)
            'strong0', 'strong1', 'weak0', 'weak1',
            'highz0', 'highz1',
        }

        if node.module.lower() in DISALLOWED_GATES:
            self._add_violation(Rules.PRIMONLY, node, list_of_gates={', '.join(ALLOWED_GATES)})
        # If the module is not in allowed or disallowed, there is a high probability it is a user defined module    
        if node.module.lower() not in ALLOWED_GATES and node.module.lower() not in DISALLOWED_GATES:
            self._add_violation(Rules.NOMODULE, node, module_name=node.module)
            # We are in a module declaration, so we need to check if any of the ports are using concatenation which might not be allowed
            for instance in node.instances:
                if instance.portlist:
                    for portarg in instance.portlist:
                        if isinstance(portarg.argname, Concat):
                            detail_msg = f"A port to a module contains a concatenation which is not allowed."
                            self._add_violation(Rules.COMPLEXRHS, node, detail_msg=detail_msg)
                            return True

    def visit_Always(self, node):
        """
        Visits an 'always' block in the AST. (Or always comb equivalent)

        node: The always block node to visit.
        """
        #Rule: Check for disallowed always_ff this should technically get caught by the preprocessor
        if isinstance(node, AlwaysFF):
            self._add_violation(Rules.ALWAYSFF, node)

        #Rule: Check for generic 'always @(...)' when specific types are required
        if  isinstance(node, Always) and not isinstance(node, AlwaysComb) and not isinstance(node, AlwaysFF) and not isinstance(node, AlwaysLatch): # This is a plain 'always @(...)'
            self._add_violation(Rules.ALWAYSSTAR, node)

        is_target_always_block = False

        #Check if the always block is a combinational block
        if isinstance(node, AlwaysComb):
            is_target_always_block = True
        # Check if the always block is a star or all sensitivity list
        elif node.sens_list and isinstance(node.sens_list, SensList) and node.sens_list.list:
            #Iterate through the sensitivity list to check flag
            for sens_item in node.sens_list.list:
                if isinstance(sens_item, Sens) and (sens_item.type == 'star' or sens_item.type == 'all'):
                    is_target_always_block = True; break
                if isinstance(sens_item, Sens) and isinstance(sens_item.sig, Identifier) and sens_item.sig.name == '*':
                    is_target_always_block = True; break
        statements_to_process = []
        #No statements here
        if node.statement is None: pass
        elif isinstance(node.statement, Block):
            #Store whole block
            if node.statement.statements: statements_to_process = node.statement.statements
        #Single statement
        else: statements_to_process = [node.statement]
        
        if isinstance(node, AlwaysFF):
            #Visit all the children statements
            if statements_to_process:
                for stmt in statements_to_process:
                    self.visit(stmt)
            
            # --- XPROP Rule: Check for missing XPROPs using Regex results ---
            for sig_name, (assign_lineno, cond_type_str) in self._conditionally_assigned_signals_info.items():
                if sig_name not in self.current_module_xprop_seq:
                    self._add_violation(Rules.XPROP, node, name=sig_name, type=cond_type_str)
                if sig_name in self.current_module_xprop_comb:
                    self._add_violation(Rules.WRONGXPROP, node, name=sig_name)
        
        #If its not a always_comb or star sensitivity list, we dont care just keep going and check children
        if not is_target_always_block:
            #Here is the always_ff or always_latch block, need to check rules
            blocking_assignments = []
            if node.statement:
                self._find_blocking_assignments_in_statement(node.statement, blocking_assignments)
            
            for ba_node in blocking_assignments:
                self._add_violation(Rules.BLKSEQ, ba_node)
            #Check for Asynchronous resets by only allow posedge clk in the sens list
            for sens_item in node.sens_list.list:
                if isinstance(sens_item, Sens):
                    if not isinstance(sens_item.sig, Identifier) or (sens_item.sig.name != 'clk' and sens_item.sig.name != 'clk_in'):
                        self._add_violation(Rules.ASYNCRESET, node)
                if isinstance(sens_item, Sens) and sens_item.type == 'negedge':
                    self._add_violation(Rules.NEGEDGE, node)
            return

        # If we are here, we are in an always_comb block
        nonblocking_assignments = []
        if node.statement:
            self._find_nonblocking_assignments_in_statement(node.statement, nonblocking_assignments)
        
        for nba_node in nonblocking_assignments:
            self._add_violation(Rules.NONBLKCOMBI, nba_node)

        #Save original state
        original_in_always_comb = self._in_always_comb
        original_top_level_full_defaults = self._always_comb_top_level_full_defaults.copy()
        original_rule1_signals_flagged = self._rule1_signals_flagged_in_current_always.copy()
        original_always_comb_lineno = self._always_comb_lineno

        #Set the state for entering an always comb block
        self._in_always_comb = True
        #get unique line number
        self._always_comb_lineno = node.lineno
        #Reset  flags
        self._always_comb_top_level_full_defaults = set()
        
        #New signal added
        self._always_comb_top_level_x_defaults = set()
        
        self._rule1_signals_flagged_in_current_always = set()
        
        #This is for the first rule. Identifies all the non conditional assignments at the top level
        direct_conditional_encountered_in_pass1 = False
        if statements_to_process:
            #Iterate through all the statements in the always_comb block
            for stmt in statements_to_process:
                is_assignment = isinstance(stmt, (NonblockingSubstitution, BlockingSubstitution))
                is_conditional = isinstance(stmt, (IfStatement, CaseStatement, CasexStatement, CasezStatement))
                if not direct_conditional_encountered_in_pass1:
                    if is_assignment:
                        #Get the assigned LHS info
                        lhs_info_set = self._get_assigned_lhs_info(stmt)
                        for name, assign_type, _ in lhs_info_set:
                            if assign_type == 'full':
                                #add to list of signals assigned at the top level
                                self._always_comb_top_level_full_defaults.add(name)
                                if is_x_assignment(stmt):
                                    self._always_comb_top_level_x_defaults.add(name)
                    #If its not an assignment, we need to check if it is a conditional statement
                    elif is_conditional:
                        #Set the conditional flag to found
                        direct_conditional_encountered_in_pass1 = True
                elif is_assignment:
                    # If we have a conditional statement AND we have a non conditional assigment we have a violation if the rule is enabled
                    self._add_violation(Rules.ASSIGNORDER, stmt)
        
        #Visit all the children statements
        if statements_to_process:
                for stmt in statements_to_process:
                    self.visit(stmt)
            
        # --- XPROP Rule: Check for missing XPROPs using Regex results ---
        for sig_name, (assign_lineno, cond_type_str) in self._conditionally_assigned_signals_info.items():
            if sig_name not in self.current_module_xprop_comb:
                self._add_violation(Rules.XPROP, node, name=sig_name, type=cond_type_str)
            if sig_name in self.current_module_xprop_seq:
                self._add_violation(Rules.WRONGXPROP, node, name=sig_name)

        #we are done so restore the state
        self._in_always_comb = original_in_always_comb
        self._always_comb_lineno = original_always_comb_lineno
        self._always_comb_top_level_full_defaults = original_top_level_full_defaults
        self._rule1_signals_flagged_in_current_always = original_rule1_signals_flagged

    def visit_IfStatement(self, node):
        """
        Visits an 'if' statement in the AST.

        node: The if statement node to visit.
        """
        signals_in_if = self._collect_all_lhs_in_statement_tree(node)
        for name, _, lineno in signals_in_if:
            # If a signal is not already recorded as conditionally assigned record it
            if name not in self._conditionally_assigned_signals_info: 
                self._conditionally_assigned_signals_info[name] = (lineno, "if-statement")

        # signals_driven_in_if_structure = self._collect_all_lhs_in_statement_tree(node)
        base_names_in_if = {name for name, _, _ in signals_in_if}

        #Only apply latch rules inside an identified always_comb
        if self._in_always_comb: 
            #Iterate through all the unique driven signals in the if statement
            for name in base_names_in_if:
                #Checks for top level default
                has_any_top_default = name in self._always_comb_top_level_full_defaults
                # Key to make sure we dont repeat violations
                rule_key_any = (self._always_comb_lineno, name, Rules.LATCH.name)
                if not has_any_top_default:
                    if rule_key_any not in self._rule1_signals_flagged_in_current_always:
                        self._add_violation(Rules.LATCH, node, name=name)
                        if Rules.LATCH.name in self.current_ruleset:
                            self._rule1_signals_flagged_in_current_always.add(rule_key_any)

        # Original traversal
        if node.cond: self.visit(node.cond)
        if node.true_statement: self.visit(node.true_statement)
        if node.false_statement: self.visit(node.false_statement)

    def visit_Block(self, node):
        """
        Visits a block statement in the AST.

        node: The block statement node to visit.
        """
        if node.statements:
            for stmt_node in node.statements:
                self.visit(stmt_node)

    def visit_CaseStatement(self, node):
        """
        Visit a case statement in the AST.

        node: The case statement node to visit.
        """ 
        if self._in_always_comb:        
            #Rule 3: Check for default case and X assignments in default case
            has_default_case = False
            default_case_node = None
            
            #Check if the case statement has a default case
            if node.caselist:
                for case_item in node.caselist:
                    #Check if this is a default case
                    if case_item.cond is None or (isinstance(case_item.cond, str) and case_item.cond == 'default'):
                        has_default_case = True
                        default_case_node = case_item
                        break
                    
            #Rule 3A: Check if default case is present
            if not has_default_case:
                self._add_violation(Rules.CASEDEFAULT, node)
            
            #Rule 3B: If default case exists, check if assignments in default case are X values
            if has_default_case and default_case_node:
                #Get all signals assigned in any part of the case statement
                all_case_assignments = self._collect_all_lhs_in_statement_tree(node)
                all_case_signals = {name for name, _, _ in all_case_assignments}
                
                #Get assignments in the default case
                default_assignments = self._collect_all_lhs_in_statement_tree(default_case_node.statement)
                default_assigns_signals = {name for name, _, _ in default_assignments}
                
                #Check if all assigned signals in the case statement are assigned X in default
                for signal_name in all_case_signals:
                    #If the signal is assigned in default case, check if it's assigned X
                    if signal_name in default_assigns_signals:
                        #Find the assignment statement(s) in default case for this signal
                        default_signal_assignments = []
                        
                        self.find_assignments_in_node(default_case_node.statement, signal_name, default_signal_assignments)
                        
                        #Check if any assignment for this signal in default case is not to X
                        non_x_assignments = []
                        for assign_stmt in default_signal_assignments:
                            if not is_x_assignment(assign_stmt):
                                non_x_assignments.append(assign_stmt)
                        
                        if non_x_assignments:
                            #At least one assignment in default case is not to X
                            self._add_violation(Rules.XASSIGN, node, name=signal_name)
                    else:
                        #Signal is not assigned in default case at all
                        self._add_violation(Rules.CASEINCOMPLETE, node, name=signal_name)
            # End Rule 3
        #Visit the condition and case items                    
        if node.comp: self.visit(node.comp)
        if node.caselist:
            for item in node.caselist: self.visit(item)

    def visit_Case(self, node):
        """
        Visits the case item within a case statement.
        node: The case item node to visit.
        """
        #Visit the conditiona and statement
        if node.cond:
            if isinstance(node.cond, list):
                for c in node.cond:
                    if c: self.visit(c)
            elif isinstance(node.cond, tuple):
                for c in node.cond:
                    if c: self.visit(c)
            else:
                self.visit(node.cond)
        if node.statement: self.visit(node.statement)

   
def main(args_list: Optional[List[str]] = None):
    """
    Main function to parse command line arguments and run the linter.
    """
    global LINT_CONFIG
    INFO = "Verilog Linter for Combinational Logic Conventions"
    VERSION = pyverilog.__version__
    parser = argparse.ArgumentParser(
        description=f"{INFO} (PyVerilog {VERSION})",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Example: python verilog_linter.py -I ./includes -D DEBUG=1 file1.v file2.v"
    )

    parser.add_argument('filelist', metavar='FILE', nargs='+', help='One or more Verilog files to lint.')
    parser.add_argument("-I", "--include", dest="include", action="append", default=[], help="Include path (can be specified multiple times).")
    parser.add_argument("-D", dest="define", action="append", default=[], help="Define a macro (e.g., -D SYNTHESIS).")
    parser.add_argument("-c", "--config", dest="config_file", default="lint_config.yaml", help="Config file path (default: lint_config.yaml).")
    parser.add_argument("-xc", "--xpropcomb", dest="comb_xprop_list", default=None, help="JSON string of a dictionary mapping modules to signals that use comb Xprop.\n Example: '{\"module_a\": [\"sig1\", \"sig2\"]}'")
    parser.add_argument("-xs", "--xpropseq", dest="seq_xprop_list", default=None, help="JSON string of a dictionary mapping modules to signals that use seq Xprop.\n Example: '{\"module_a\": [\"sig1\", \"sig2\"]}'")
    parser.add_argument("-o", "--override", dest="override", default=None, help="JSON dictionary of rules to override for current module")
    
    args = parser.parse_args(args_list)

    filelist = args.filelist

    comb_xprop_dict = {}
    seq_xprop_dict = {}
    if args.comb_xprop_list:
        try:
            comb_xprop_dict = json.loads(args.comb_xprop_list)
            if not isinstance(comb_xprop_dict, dict):
                raise ValueError("The provided JSON must be an object/dictionary.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: Invalid format for -x/--xprop argument. It must be a valid JSON string.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            print(f"Example: '{{\"module_a\": [\"sig1\"]}}'", file=sys.stderr)
            sys.exit(1)

    if args.seq_xprop_list:
        try:
            seq_xprop_dict = json.loads(args.seq_xprop_list)
            if not isinstance(seq_xprop_dict, dict):
                raise ValueError("The provided JSON must be an object/dictionary.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: Invalid format for -x/--xprop argument. It must be a valid JSON string.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            print(f"Example: '{{\"module_a\": [\"sig1\"]}}'", file=sys.stderr)
            sys.exit(1)
    
    override_dictonary = {}
    if args.override:
        try:
            override_dictonary = json.loads(args.override)
            if not isinstance(override_dictonary, dict):
                raise ValueError("The provided JSON must be an object/dictionary.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error: Invalid format for -o/--override argument. It must be a valid JSON string.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            print(f"Example: '{{\"module_a\": [\"rule1\", \"rule2\"]}}'", file=sys.stderr)
            sys.exit(1)
    
    LINT_CONFIG = load_lint_config(args.config_file)
    #If override is provided, update the config with the overrides, this should only be for one module
    if override_dictonary:
        LINT_CONFIG.update(override_dictonary) # Update the xprop_dict with overrides

    if not filelist:
        print("No Verilog files provided.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    total_violations_across_files = 0
    for f_path in filelist:
        if not os.path.exists(f_path):
            print(f"Error: File not found: {f_path}", file=sys.stderr)
            total_violations_across_files += 1 # Count as an error
            continue
        
        current_file_violations = 0
        violation_output_lines = [] # For writing to file
        include_dirs = [os.path.dirname(f_path)] + (args.include or [])
        
        #------------------------------------------------
        # Change the directory to the temporary directory
        #------------------------------------------------
        original_dir = os.getcwd()
        os.chdir(args.include[0])
        
        try:
            ast, directives = parse([f_path], preprocess_include=include_dirs, preprocess_define=args.define)
            linter = VerilogLinter(config=LINT_CONFIG)
            linter._xprop_macro_comb_out_signals_found_by_regex = comb_xprop_dict
            linter._xprop_macro_seq_out_signals_found_by_regex = seq_xprop_dict

            linter.visit(ast)

            # ast.show()

            if linter.violations:
                current_file_violations = len(linter.violations)
                total_violations_across_files += current_file_violations
                
                print(f"Found {current_file_violations} violation(s):")
                violation_output_lines.append(f"Violations for file: {f_path}\n")
                violation_output_lines.append(f"Found {current_file_violations} violation(s):\n")

                sorted_violations = sorted(linter.violations, key=lambda x: (x[0] or "", x[3], x[1]))
                for mod_name, rule_id, msg, lineno in sorted_violations:
                    module_prefix = f"Module '{mod_name}'" if mod_name else ""
                    
                    console_output = f"  - {module_prefix}: [{rule_id}] {msg}"
                    file_output_line = f"- {module_prefix}: [{rule_id}] {msg}\n"
                    
                    print(console_output)
                    violation_output_lines.append(file_output_line)

        except Exception as e:
            error_message = f"Error processing file {f_path}: {e}"
            print(error_message, file=sys.stderr)

            import traceback
            traceback.print_exc()
            total_violations_across_files +=1 #Count critical error as a violation for exit code
        
        #--------------------------
        # Change back directories
        #-------------------------
        os.chdir(original_dir)

    if total_violations_across_files > 0:
        print(f"\nLinting finished with {total_violations_across_files} total violation(s)/error(s).")
        sys.exit(1)
    else:
        return

def cli():
    """ Command line interface wrapper"""
    try:
        total_violations, _ = main()
        sys.exit(1 if total_violations > 0 else 0)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    cli()