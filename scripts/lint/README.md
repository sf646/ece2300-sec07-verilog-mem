# ECE2300 Linting Tool Documentation
Author: Irwin Wang

Date: 07/18/2025 
## What this Tool Does
This tool is a custom linter for ECE2300. This tool uses a custom version of [Pyverilog](https://github.com/cornell-ece2300/pyverilog) a python verilog parser. To use this tool you need to install the custom version of Pyverilog alongside all its dependencies. This linter checks for custom rules that enforce the class's coding conventions. Although they may be restrictive or redundant these were built in the mind of always making the students ask questions and test their design more thoroughly. A big problem this tool hopes to solve is catching simulation-synthesis mismatches. If every test should pass in simulation everything should work during synthesis.

Please report any bugs, issues, or feedback to Professor Batten.

## How to use this Tool in our Labs
*FIX ONCE DECIDEDED HOW TO INSTALL*

To run this tool on ecelinux run the following on any of the hardware or test verilog files:
```
% ece2300-lint <PATH-TO-FILE>
```
If everything passes our checks nothing should be printed out by default. If there is printed output that means there is an error.

To see a list of all the rules that we can check (Not every rule applies to every file) run:
```
% ece2300-lint -l
```
This tool can be run by itself just like iverilog and verilator but is also part of the build system, and will be run in addition to the tests you write.

## How to Edit, Add, and Test this Tool
This tool at its foundation is just an application of a verilog parser. However with that being said it is flexible and could be used in other applications.

### How this Tool Works at a High Level
This linter has two main phases: (1) Preprocessing, (2) Linting.
**FIX LINKS**

The file [ece2300-lint]() is the main orchestrator and then calls on [preprocessor.py]() and [linter.py]()
Pyverilog (as it currently is during Summer 2025) only supports Verilog (and not even full Verilog). In ECE2300 we use many SystemVerilog Constructs. To make this tool work changes had to be made to Pyverilog to be able to parse our lab code. Even then exceptions had to be made for what can be parsed. See below for a short description of how Pyverilog works and how to begin tinkering with it.

**(1) Preprocessing**

Because we cannot parse everything we need to do some simple preprocessing. Synthesis specific constructs like (* keep=1 *) are removed, modules that contain functions and tasks have their entire body removed, and more. This is all being done in a temporary directory with a copy of your file so that this linter is not destructive. The second thing the preprocessor does is look for special comments. For test files we use the following special comment to direct the linter to the correct module or just not lint the test file. If you look at the test files in our lab files you will see these comments.
```
// ece2300-lint
`include xyz.v

// ece2300-lint off
```
The preprocessor then looks for constructs using regex that are explicitly never allowed. Although these are perfectly valid SystemVerilog many of these are outside the scope of this class or are prohibited to use for instructional purposes. When running the preprocessor this is one thing that can report errors.

The final thing that this preprocessor does is look for the `ECE2300_XPROP macro and the signals that use this. The preprocessor returns a list of signals that use xprop alongside the top level files we want to lint. Although we may want to lint on a single file, because Pyverilog flattens designs we need to make sure all included modules are parsable.

**(2) Linting**

Pyverilog takes in verilog and spits out an Abstract Syntax Tree (AST). This tree is what we use to determine relationships between variables and enable some more sophisticated rule checking. Our linter traverse this tree and checks our rules. How do we know what rules to check for? Well, we need a yaml file that defines rule sets and rules for each module. So our rules are _module based_ not file based. If you look at our [yaml file]() for our labs you will see rule sets and modules. The rule-sets are just to keep things in order and concise. Below we have a list of modules and their respecitive rulesets. Note that you can also define a list of rules directly for a module. The following are equivalent:
```
rule-sets:
  SetA:
    - rule1
    - rule2
    - rule3
modules:
  moduleA
    - SetA
```
```
rule-sets:
  SetA:
    - rule1
    - rule2
    - rule3
modules:
  moduleA: SetA
```
```
modules:
  moduleA
    - rule1
    - rule2
    - rule3
```
Sets can refer to other sets and a Module can have any combination or rules or sets. Note that it is the developers responsibility to make sure these rules are compatiable for each other and achieve the desired result. 

## How to test this Linter

Looking inside this linter here is the tree of files
```
├── ece2300-lint
├── linter.py
├── lint_rules.py
├── preprocessor.py
├── README.md
├── rulesets.yaml
└── tests
    ├── __init__.py
    ├── test_files
    │   ├── includes
    │   │   └── ...
    │   ├── invalid
    │   │   ├── ...
    │   └── valid
    │       ├── ...
    ├── test_linter.py
    └── testrules.yaml
```

The top level files are the actual tool files. Everything under tests is used to test the tools. To run the tests do the following (You need to be in the lint directory):
```
cd lint
pytest
```
[test_linter.py]() contains all the pytest logic that runs the tests. It will lint over invalid and valid folders. Invalid should have files that fail their specific rules while valid should have files that should pass. The include directory is where modules that need to be included go. Each file should start with the name of the rule. The testrules.yaml file is where the module rules are defined.

# How to Expand Functionality

## A Brief Explanantion of How Pyverilog works and what to look for
Pyverilog is based on PLY a python implementation of Lex-Yacc. Pyverilog has a whole suite of tools but for our purposes we only care about the parser which is located in the [vparser folder](https://github.com/cornell-ece2300/pyverilog/tree/develop/pyverilog/vparser). Here there are three relevant files: [ast.py](https://github.com/cornell-ece2300/pyverilog/tree/develop/pyverilog/vparser/ast.py), [lexer.py](https://github.com/cornell-ece2300/pyverilog/tree/develop/pyverilog/vparser/lexer.py), and [parser.py](https://github.com/cornell-ece2300/pyverilog/tree/develop/pyverilog/vparser/parser.py). 

To go about adding more features, say more parsing ability. You would do the following

1. Add the desired tokens to lexer.py This is how the parser can recognize keywords
2. Define Nodes in ast.py This is the representation of what you parse in the AST
3. Edit parser.py Note that this is the hardest part. Ordering of code matters and the docstrings as well. People more familiar with parsers will have a much better time tinkering than I did.

Note that this is still a very high overview of how to expand pyverilog that does not cover the many pitfalls in these steps (especially step 3).

## How to Add More Rules
When adding more rules there are three things you need to do.

**(1) Add it to [lint_rules.py]()**

Inside lint_rules.py there are many classes each of which define a rule. Here you need to define the name, ID (not as important), description and error message you wish to use. You may want to play aronud with the original Pyverilog to get a feel for how it works, what it outputs, and how to debug it.

**(2) Add it to the linter**

Now you have to put on your thinking caps and dive into the linting and add the logic to linter. A very basic how to traverse an AST is the following. The high level constructs in a module are always visted. Once the "Visitor" visits a block it does one of the following: either finds a custom vist_NODE() function, again these nodes were defined earlier in ast.py or goes to a generic visit function that automatically visits a nodes children. I would suggest adding custom checking logic to vist_NODE() functions or building on top of what is previously written. Make sure to include an _add_violation() to actually report an error when it is flagged.

**(3) Update your ruleset**

Go back to the [rulesets.yaml]() and add rule-sets or rules to modules.
