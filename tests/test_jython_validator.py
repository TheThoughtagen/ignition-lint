from ignition_lint.reporting import LintSeverity
from ignition_lint.validators.jython import JythonValidator


def validate(script: str):
    validator = JythonValidator()
    return validator.validate_script(script, context="test")


def test_detects_indentation():
    issues = validate("value = 1\nprint(value)\n")
    codes = {issue.code for issue in issues}
    assert "JYTHON_INDENTATION_REQUIRED" in codes


def test_detects_syntax_error():
    issues = validate("\tif value > 5\n\t\treturn 'high'")
    assert any(issue.severity == LintSeverity.ERROR for issue in issues)


def test_detects_best_practices():
    issues = validate(
        "\turl = 'http://localhost'\n\tresponse = system.net.httpClient().post(url)"
    )
    codes = {issue.code for issue in issues}
    assert "JYTHON_HARDCODED_LOCALHOST" in codes
    assert "JYTHON_HTTP_WITHOUT_EXCEPTION_HANDLING" in codes


def test_clean_script_produces_no_issues():
    script = "\ttry:\n\t\treturn system.date.now()\n\texcept Exception as err:\n\t\tsystem.perspective.print(str(err))"
    assert validate(script) == []


class TestPy2Preprocessing:
    """Ensure Python 2 constructs don't cause spurious JYTHON_SYNTAX_ERROR."""

    def test_print_statement_no_syntax_error(self):
        script = '\tprint "hello world"'
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes
        assert "JYTHON_PRINT_STATEMENT" in codes

    def test_print_variable_no_syntax_error(self):
        script = "\tprint value"
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes
        assert "JYTHON_PRINT_STATEMENT" in codes

    def test_print_multiple_args_no_syntax_error(self):
        script = '\tprint "x =", x, "y =", y'
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes

    def test_print_redirect_no_syntax_error(self):
        script = "\tprint >>sys.stderr, 'error'"
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes

    def test_except_comma_syntax_no_error(self):
        script = "\ttry:\n\t\tpass\n\texcept Exception, e:\n\t\tpass"
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes

    def test_raise_comma_syntax_no_error(self):
        script = '\traise ValueError, "bad value"'
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes

    def test_genuine_syntax_error_still_caught(self):
        script = "\tif x >\n\t\tpass"
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" in codes

    def test_print_function_call_unchanged(self):
        """print(x) should not be mangled by preprocessing."""
        script = "\tprint(42)"
        issues = validate(script)
        codes = {i.code for i in issues}
        assert "JYTHON_SYNTAX_ERROR" not in codes
