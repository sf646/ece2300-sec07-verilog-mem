import subprocess
import pytest
from pathlib import Path

def run_linter(file_path):
    """
    Run the linter on the specified file and return the output.
    """
    result = subprocess.run(
        ['ece2300-lint', str(file_path), '-t', '-I', str(file_path.parent), '-I', str(file_path.parent.parent / 'includes')],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

class TestLinter:
    """ 
    Test suite for the ECE2300 linter.
    """

    @pytest.mark.parametrize("test_file", Path("tests/test_files/valid").glob("*.v"))
    def test_valid_files(self, test_file):
        """
        Test that all valid code files pass the linter without errors.
        """
        returncode, stdout, stderr = run_linter(test_file)
        assert returncode == 0, f"Valide file {test_file.name} should pass linter but failed with: {stderr}"
    
    @pytest.mark.parametrize("test_file", Path("tests/test_files/invalid").glob("*.v"))
    def test_invalid_files(self, test_file):
        """
        Test that all invalid code files fail the linter with appropriate error messages.
        """
        returncode, stdout, stderr = run_linter(test_file)
        assert returncode != 0, f"Invalid file {test_file.name} should fail linter but passed"
    
    @pytest.mark.parametrize("test_file", Path("tests/test_files/invalid").glob("*.v"))
    def test_specific_error_message(self, test_file):
        """
        Test that the linter catches specific rule violations based on filename
        """
        returncode, stdout, stderr = run_linter(test_file)

        rule_name = self._extract_rule_name_from_filename(test_file.name)

        if rule_name:
            assert returncode != 0, f"File {test_file.name} should fail linter"
            assert f"[{rule_name}]" in stdout, f"Expected rule [{rule_name}] not found in output: {stdout}"
        else:
            assert returncode != 0, f"Invalid file {test_file.name} should fail linter"

        
    def _extract_rule_name_from_filename(self, filename):
        """Extract rule name from filename like 'LATCH_example.py' -> 'LATCH'"""
        # Remove extension
        name_without_ext = filename.rsplit('.', 1)[0]
        
        # Check if filename starts with a known rule name
        known_rules = [
            'LATCH', 'CASEINFER', 'ASSIGNORDER', 'CASEDEFAULT', 'XASSIGN', 
            'CASEINCOMPLETE', 'XPROP', 'ALWAYSFF', 'ALWAYSSTAR', 'BLKSEQ', 
            'NONBLKCOMBI', 'ASYNCRESET', 'NEGEDGE', 'GATEONLY', 'BADLHS', 
            'BADRHS', 'COMPLEXLHS', 'COMPLEXRHS', 'PRIMONLY'
        ]
        
        for rule in known_rules:
            if name_without_ext.startswith(rule):
                return rule
        
        return None