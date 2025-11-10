# Zeit Project Code Style Guide

## Python Formatting

- Always run `ruff check --fix` after any file modification to automatically fix lint and formatting issues.
- Follow PEP 8 for all Python code.

## Type Hints

- Always add type hints to all functions, methods, and variables where possible.
- Use explicit types for function arguments and return values.
- Assume Python 3.10 or greater for all code.
- Prefer built-in type hint syntax (e.g., `str | None`, `int | float`) over `Optional` or `Union` from the typing module when possible.
- Use typing generics (e.g., `list[str]`, `dict[str, int]`) only when built-in syntax is not available or less clear.

## Imports

- Place all import statements at the top of each file.
- Order imports: standard library, third-party, local modules.

## Naming

- Use `snake_case` for variables and functions.
- Use `PascalCase` for classes.
- Constants should be `UPPER_CASE`.

## Linting

- All code must pass Ruff checks with no errors or warnings.

## General

- Keep code DRY (Don't Repeat Yourself).
- Prefer clarity and readability over cleverness.
- Use Google-style docstrings for all modules, classes, and functions.
- All test functions must have at least a 1-line docstring describing the test purpose.
- Use the AAA (Arrange/Act/Assert) structure for setting up tests:
  - Add `# Arrange`, `# Act`, and `# Assert` comments for non-trivial tests or fixtures.
```python
      def test_code():
            # Arrange
            test_list = [1,2,3]

            #Act
            actual_sum = my_func(test_list)
            expected_sum = 6

            # Assert
            assert actual_sum = expected_sum
```
  - For fixtures, include an `# Arrange` comment.
 	- For simple tests, comments are optional, but use them if there are several lines for each section.

         ```python
         assert sum([1,2]) == 3
 	- For non-trivial cases, assign expected and actual values separately, and use `assert actual == expected`.

	- Add descriptors to clarify, e.g., `assert actual_month == expected_month`.
 	- For multiple values, always use descriptors, e.g.:

  ```python
  assert actual_day == expedted_day
  assert actual_month == expected_month
  ```

  - All asserts should have an assert message
  -
- Prefer parameterized tests when checking multiple cases (e.g., using pytest.mark.parametrize).
- Always use temporary folders (e.g., pytest's tmp_path fixture) for filesystem interaction in tests to ensure cleanup.

---

**Agent Instructions:**

- Always run `ruff check --fix` after modifying any file.
- Always add type hints to all new or edited code.
- Always use Google-style docstrings for modules, classes, and functions.
- All test functions must have at least a 1-line docstring.
- Follow this guide for all code generation and edits unless otherwise instructed.
