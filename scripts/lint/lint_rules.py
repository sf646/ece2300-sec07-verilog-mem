class Rules:
    """A namespace for all linting rule definitions."""

#------------------------------
# Inferred Latch Rules
#------------------------------

    class LATCH:
        name = "LATCH"
        ID = "R101"
        description = "Signal driven in an if-statement must have a top-level default in an always_comb block."
        error_message = "Signal '{name}' (driven in if-stmt) lacks a complete (every bit is assigned) top-level default in always_comb."

    class ASSIGNORDER:
        name = "ASSIGNORDER"
        ID = "R102"
        description = "Non-conditional assignments must appear at the top of an always_comb block, before any conditionals."
        error_message = "Non-conditional assignment found after a conditional statement. Move all default assignments to the top."
    
#------------------------------
# X Optimism Rules
#------------------------------

    class CASEDEFAULT:
        name = "CASEDEFAULT"
        ID = "R201"
        description = "Case statements must have a 'default' case to prevent latches and X-optimism."
        error_message = "Case statement lacks a 'default' case."

    class XASSIGN:
        name = "XASSIGN"
        ID = "R202"
        description = "To prevent X-optimism, signals driven in a case statement should be assigned 'x' in the default case."
        error_message = "Signal '{name}' is not assigned 'x' in the default case."

    class CASEINCOMPLETE:
        name = "CASEINCOMPLETE"
        ID = "R203"
        description = "All signals assigned in the case statement must also be assigned in the default case."
        error_message = "Signal '{name}' is assigned in some case paths but not in default case. Assign all signals in the always_comb block in the default case."

    class XPROP:
        name = "XPROP"
        ID = "R204"
        description = "Signals driven in a case statement should be assigned 'x' in the default case to prevent X-optimism."
        error_message = "Signal '{name}' conditionally assigned in {type} in always_comb (always_ff) does not appear as the first argument of an ECE2300_XPROP (ECE2300_SEQ_XPROP) macro call found anywhere in this file."
    
    class WRONGXPROP:
        name = "WRONGXPROP"
        ID = "R205"
        description = "The signal in the xprop macro is using the incorrect xprop macro."
        error_message = "Signal '{name} is found in an ECE2300_XPROP (ECE2300_SEQ_XPROP) however it is in a always_ff (always_comb). Please use the other macro."

#------------------------------
# Always Block Rules
#------------------------------

    class ALWAYSFF:
        name = "ALWAYSFF"
        ID = "R301"
        description = "Combinational logic (always_comb, always @*) should only be used in this module."
        error_message = "The always_ff construct is disallowed by configuration. Please stick to combinational logic or gate level modeling."

    class ALWAYSSTAR:
        name = "ALWAYSSTAR"
        ID = "R302"
        description = "Never use a generic always block."
        error_message = "Generic 'always @(...)' block found. Use 'always_comb', 'always_ff', or 'always_latch' instead."

    class BLKSEQ:
        name = "BLKSEQ"
        ID = "R303"
        description = "Don't use block assignment (=) in an always_ff block."
        error_message = "Blocking assignment ('=') used in 'always_ff' block. Use non-blocking ('<=') for sequential logic."

    class NONBLKCOMBI:
        name = "NONBLKCOMBI"
        ID = "R304"
        description = "Don't use non blocking assignment (<=) in an always_comb block."
        error_message = "Non-blocking assignment ('<=') used in 'always_comb' or 'always @*' block. Use blocking ('=') for combinational logic."

    class ASYNCRESET:
        name = "ASYNCRESET"
        ID = "R305"
        description = "Do not use asynchronous reset. Use synchronous reset."
        error_message = "Asynchronous reset detected in 'always_ff' block. Only 'posedge clk' is allowed in sensitivity list."

    class NEGEDGE:
        name = "NEGEDGE"
        ID = "R306"
        description = "Do not use Negedge only posedge."
        error_message = "Negative edge sensitivity ('negedge') in 'always_ff' block is not allowed. Only 'posedge clk' is permitted."

#------------------------------
# Gate Level Rules
#------------------------------

    class NOSPBLK:
        name = "NOSPBLK"
        ID = "R401"
        description = "No special blocks allowed. Checked Always, Initial, Function, Task, GenerateStatement, SystemCall"
        error_message = "RTL construct '{type}'. Module '{name}' gate-level only."
    
    class BADLHS:
        name = "BADLHS"
        ID = "R402"
        description = "Right-hand side of an assignment must be a gate-level primitive or a wire. It should be a Lvalue"
        error_message = "Malformed LHS for 'assign'."
    
    class BADRHS:
        name = "BADRHS"
        ID = "R403"
        description = "Left-hand side of an assignment must be a wire or a gate-level primitive. It should be an Rvalue."
        error_message = "Malformed RHS for 'assign'."
    
    class COMPLEXLHS:
        name = "COMPLEXLHS"
        ID = "R404"
        description = "Left-hand side of an assignment must be a single wire or gate-level primitive."
        error_message = "LHS of 'assign' is not a simple signal or part-select. Found type: {type}"

    class COMPLEXRHS:
        name = "COMPLEXRHS"
        ID = "R405"
        description = "Right-hand side of an assignment must be an identifier, identifier[msb:lsb], or a simple literal."
        error_message = "RHS of 'assign' {detail_msg}. In gate-level/structural mode, RHS must be an identifier, identifier[msb:lsb], or a simple literal."

    class PRIMONLY:
        name = "PRIMONLY"
        ID = "R406"
        description = "Only AND, OR, XOR, NOT, and their respective combinations"
        error_message = "Non-primitive gate/module founds. Allowed: {list_of_gates}."
    
    class NOMODULE:
        name = "NOMODULE"
        ID = "R407"
        description = "No module instantiation allowed inside a gate-level module."
        error_message = "No module instantiation is allowed. A module with name {module_name} was found. Gate level modules should use gate primatives to build the module."

