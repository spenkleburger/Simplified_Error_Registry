# Errors and Fixes Log

> **Note**: This file is processed daily by the consolidation app at 2 AM. 
> `### Error:` entries → fix_repo.md; `### Agent Process Issue:` entries → coding_tips.md. Contents are then cleared (file is kept).

## YYYY-MM-DD Session

### Error: ErrorType: Error message

**Timestamp:** YYYY-MM-DDTHH:MM:SSZ  
**File:** `path/to/file.py`  
**Line:** 42  
**Error Type:** `ErrorType`  
**Tags:** `tag1`, `tag2`, `tag3` (auto-generated)

**Error Context:**
```
Traceback (most recent call last):
  File "path/to/file.py", line 42, in function_name
    code_that_caused_error
ErrorType: Error message
```

**Fix Applied:**
```python
# Before
code_before_fix

# After
code_after_fix
```

**Explanation:** Brief explanation of why the fix works.

**Result:** ✅ Solved  
**Success Count:** 1  
**Test Command:** `task test`  
**Test Result:** All tests passed

---

### Agent Process Issue: Issue description

**Timestamp:** YYYY-MM-DDTHH:MM:SSZ  
**Issue Type:** `agent-process`  
**Tags:** `agent-process`, `category-tag`, `specific-tag`

**Issue Description:**
Detailed description of the agent process issue that occurred.

**Rule Established:**
The rule or guideline that should be followed to avoid this issue in the future.

**Example:**
- ✅ Good example
- ✅ Another good example
- ❌ Bad example to avoid

**Result:** ✅ Documented

---
