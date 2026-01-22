# Test Output Capture Documentation

> **Purpose**: This document explains how test output is captured and filtered for agent error identification in the Simplified Error Registry (SER) system.

**Last Updated:** 2026-01-21

---

## Overview

The test scripts (`test_backend.py`, `test_frontend.py`, `test_integration.py`) automatically capture test output and copy it to the clipboard. However, to make error identification efficient for the agent, **only relevant error sections are captured**, not the entire test output.

---

## Required Test Output Sections

The test scripts extract and copy only these sections to the clipboard:

### 1. FAILURES Section

**Marker**: `=== FAILURES ===`

**Content**: Detailed tracebacks and error messages for each failing test.

**Example**:
```
=== FAILURES ===
FAILED tests/test_example.py::test_function - AssertionError: assert 1 == 2
```

**Why Required**: Contains the specific error details needed for the agent to identify and fix errors.

---

### 2. ERRORS Section

**Marker**: `=== ERRORS ===`

**Content**: Collection errors, import errors, and other test setup failures.

**Example**:
```
=== ERRORS ===
ERROR tests/test_example.py - ImportError: cannot import name 'module'
```

**Why Required**: Identifies configuration and setup issues that prevent tests from running.

---

### 3. Short Test Summary Info

**Marker**: `=== short test summary info ===`

**Content**: Concise summary of all failures and errors.

**Example**:
```
=== short test summary info ===
FAILED tests/test_example.py::test_function
ERROR tests/test_example.py::test_other
```

**Why Required**: Provides a quick overview of all failures for the agent to prioritize fixes.

---

## Excluded Sections

The following sections are **NOT** captured to keep clipboard output focused:

- ✅ **Passing test output**: Individual passing test names and details
- ✅ **Test collection info**: Information about discovered tests
- ✅ **Coverage reports**: Code coverage statistics
- ✅ **Progress indicators**: Dots, percentages, and other progress output
- ✅ **Verbose test output**: Detailed output from passing tests

**Why Excluded**: These sections don't contain error information and would clutter the clipboard, making it harder for the agent to identify actual errors.

---

## How It Works

### Extraction Process

1. **Full Output Capture**: All test output is captured using `OutputCapture` class
2. **Section Detection**: The `extract_error_sections()` function scans for section markers:
   - `=== FAILURES ===`
   - `=== ERRORS ===`
   - `=== short test summary info ===`
3. **Content Extraction**: Only lines within these sections are extracted
4. **Clipboard Copy**: Extracted sections are copied to clipboard with a header indicating the test command used

### Fallback Behavior

- **If no error sections found**: Nothing is copied to clipboard (tests passed)
- **If tests failed but sections not detected**: Full output is copied as fallback (shouldn't happen with pytest)

---

## Test Scripts

### Backend Tests (`test_backend.py`)

- **Command**: `task test:backend`
- **Test Runner**: pytest
- **Output Format**: pytest standard format
- **Sections Captured**: FAILURES, ERRORS, short test summary info

### Frontend Tests (`test_frontend.py`)

- **Command**: `task test:frontend`
- **Test Runner**: Vitest
- **Output Format**: Vitest format (similar to pytest)
- **Sections Captured**: FAIL sections, ERROR sections, test summary

### Integration Tests (`test_integration.py`)

- **Command**: `task test:integration`
- **Test Runner**: pytest (with `-m integration` marker)
- **Output Format**: pytest standard format
- **Sections Captured**: FAILURES, ERRORS, short test summary info

---

## Agent Workflow Integration

### How the Agent Uses Captured Output

1. **User runs test command**: `task test:backend`
2. **Script captures errors**: Only FAILURES/ERRORS/summary sections copied to clipboard
3. **User pastes output**: Agent receives focused error information
4. **Agent identifies errors**: Parses error types, messages, file locations
5. **Agent looks up fixes**: Uses Simplified Error Registry lookup order
6. **Agent applies fixes**: Implements fixes from `fix_repo.md` or creates new ones

### Benefits of Filtered Output

- ✅ **Faster error identification**: Agent doesn't need to parse through passing tests
- ✅ **Reduced token usage**: Smaller clipboard content = fewer tokens
- ✅ **Clearer error context**: Only relevant error information is present
- ✅ **Better fix matching**: Error signatures are easier to extract

---

## Verification

To verify that test output capture is working correctly:

### Test with Failing Tests

1. Create a test that intentionally fails:
   ```python
   def test_failure():
       assert 1 == 2
   ```

2. Run the test command:
   ```bash
   task test:backend
   ```

3. Check clipboard contents:
   - Should contain `=== FAILURES ===` section
   - Should contain `=== short test summary info ===` section
   - Should NOT contain passing test output
   - Should NOT contain test collection info

### Test with Passing Tests

1. Run tests that all pass:
   ```bash
   task test:backend
   ```

2. Check clipboard:
   - Should be empty or contain message: "All tests passed - nothing copied to clipboard"

---

## Troubleshooting

### Issue: No error sections in clipboard despite test failures

**Possible Causes**:
- Test runner output format changed
- Section markers not detected correctly
- Output encoding issues

**Solution**: Check the full console output. If error sections exist but aren't captured, the `extract_error_sections()` function may need updating for the specific test runner format.

### Issue: Too much output in clipboard

**Possible Causes**:
- Section detection not working
- Test runner using different format
- Fallback to full output triggered

**Solution**: Verify section markers match expected format. Check if test runner version changed output format.

### Issue: No output copied when tests fail

**Possible Causes**:
- Clipboard copy function failing
- Section detection not finding markers
- Output capture not working

**Solution**: 
- Check console output to see if errors are displayed
- Verify clipboard permissions on your system
- Check stderr for clipboard error messages (enhanced error handling will show specific errors)
- Common issues:
  - Windows: `clip` command not found (check PATH)
  - Linux: `xclip` not installed (`sudo apt install xclip`)
  - macOS: `pbcopy` should be available by default

### Issue: Clipboard operation errors

**Error Messages** (enhanced error handling shows these):
- `⚠️  Clipboard operation timed out` - Operation took longer than 5 seconds
- `⚠️  Clipboard command not found: [command]` - Required clipboard tool missing
- `⚠️  Clipboard operation failed: [error]` - Other clipboard failure

**Solution**: 
- Install missing clipboard tools (see above)
- Check system permissions
- Verify clipboard is accessible (try manual copy/paste)

---

## Implementation Details

### Function: `extract_error_sections()`

Located in each test script (`test_backend.py`, `test_frontend.py`, `test_integration.py`).

**Algorithm**:
1. Split output into lines
2. Scan for section markers (`=== FAILURES ===`, etc.)
3. Track which section we're in
4. Capture lines until next section or end
5. Return extracted sections with header

**Edge Cases Handled**:
- Section markers split across lines
- Multiple sections in output
- No error sections (tests passed)
- Different test runner formats (pytest vs Vitest)

### Function: `copy_to_clipboard()`

Located in each test script with enhanced error handling (updated 2026-01-21).

**Error Handling**:
- `subprocess.TimeoutExpired`: Clipboard operation timeout (5 second limit)
- `FileNotFoundError`: Clipboard command not found (e.g., `clip`, `pbcopy`, `xclip`)
- Generic `Exception`: Other clipboard failures

**Improvements**:
- Specific exception types for better debugging
- Error messages printed to stderr for troubleshooting
- Graceful fallback when clipboard operations fail

### Project-Specific Code

The `test_integration.py` script includes project-specific code for verification test workflows. When copying this script to a template:

1. **Remove `VERIFICATION_TEST_FILE` constant** (lines ~47-54)
2. **Remove verification test checks** in `filter_api_schema_files()` (lines ~309-312)
3. **Remove verification test messaging** in `main()` (lines ~395-404)

All project-specific sections are clearly marked with `PROJECT-SPECIFIC` comments for easy identification.

---

## Future Enhancements

Potential improvements to test output capture:

- [ ] Support for other test runners (Jest, Mocha, etc.)
- [ ] Configurable section markers (for custom test runners)
- [ ] Error count in header
- [ ] Timestamp in captured output
- [ ] Support for structured output formats (JSON)

---

## Related Documentation

- [SER Implementation Plan](../docs/SER_IMPLEMENTATION_PLAN.md) - Phase 2.3
- [Error Resolution Protocol](../.cursor/rules/global/errors.mdc) - How agent uses captured output
- [Test Scripts](../scripts/) - Implementation files

---

## Summary

Test output capture is designed to provide the agent with **only the essential error information** needed for error identification and fix lookup. By filtering out passing tests and irrelevant output, the agent can:

1. **Identify errors faster** - No need to parse through passing tests
2. **Use fewer tokens** - Smaller clipboard content
3. **Match fixes better** - Clear error signatures
4. **Focus on failures** - Only see what needs fixing

This focused approach makes the Simplified Error Registry workflow more efficient and effective.
