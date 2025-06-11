# Test Suite for MARTin Interface

This directory contains the comprehensive test suite for the MARTin Interface project.

## Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── unit/                # Unit tests for individual components
│   ├── test_martin_adapter.py
│   ├── test_metadata.py
│   ├── test_project.py
│   ├── test_roi_elements.py
│   ├── test_sample.py
│   ├── test_search_directories.py
│   ├── test_constants.py
│   ├── test_dataset.py
│   ├── test_general_parameters.py
│   └── test_holder.py
├── integration/         # Integration tests
│   ├── test_adapter_integration.py
│   └── test_validation_integration.py
├── notebooks/           # Notebook-specific tests
│   └── test_notebooks.py
└── test_mocks.py       # Mock tests for external dependencies
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements_test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests with coverage
pytest --cov=martin_interface --cov-report=html

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest tests/unit/test_martin_adapter.py

# Run a specific test class
pytest tests/unit/test_martin_adapter.py::TestAdapter

# Run a specific test method
pytest tests/unit/test_martin_adapter.py::TestAdapter::test_adapter_init_invalid_path
```

## Test Coverage

Generate coverage reports:

```bash
# Terminal report
pytest --cov=martin_interface --cov-report=term-missing

# HTML report
pytest --cov=martin_interface --cov-report=html
# Open htmlcov/index.html in browser

# XML report (for CI/CD)
pytest --cov=martin_interface --cov-report=xml
```

## Writing Tests

### Unit Tests

Unit tests should:
- Test individual functions/methods in isolation
- Use mocks for external dependencies
- Be fast and deterministic
- Follow the AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_function_name(self, mock_dependency):
    # Arrange
    mock_dependency.return_value = "expected"
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == "expected"
    mock_dependency.assert_called_once()
```

### Integration Tests

Integration tests should:
- Test interaction between multiple components
- Use real file I/O when necessary
- Test complete workflows
- May be slower than unit tests

### Fixtures

Common fixtures are defined in `conftest.py`:
- `temp_dir`: Temporary directory for file operations
- `sample_*_dict`: Sample data dictionaries
- `mock_*`: Pre-configured mock objects
- `create_test_files`: Creates test files in temp directory

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions configuration
- name: Run tests
  run: |
    pip install -r requirements_test.txt
    pytest --cov=martin_interface --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Debugging Tests

### Run tests with verbose output
```bash
pytest -vv
```

### Run tests with print statements visible
```bash
pytest -s
```

### Run tests with full traceback
```bash
pytest --tb=long
```

### Run tests with pdb on failure
```bash
pytest --pdb
```

## Performance Testing

Run performance benchmarks:
```bash
pytest tests/benchmarks/ --benchmark-only
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what they test
3. **Speed**: Keep tests fast, mock expensive operations
4. **Coverage**: Aim for >80% code coverage
5. **Maintenance**: Update tests when code changes

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the project is installed in development mode:
   ```bash
   pip install -e .
   ```

2. **File not found**: Tests should use fixtures for file paths, not hardcoded paths

3. **Flaky tests**: Use proper teardown and avoid time-dependent tests

4. **Mock issues**: Ensure mocks match the actual interface

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if needed0, "std_deviation": 25.0}]
        
        stats_data = {
            "row": 0,
            "col": 0,
            "adjusted_average": 100.0,
            "adjusted_average_std_deviation": 10.0,
            "relative_adjusted_average_std_deviation": 10.0,
            "normalized_average": 0.5,
            "normalized_average_std_deviation": 0.05,
            "relative_normalized_average_std_deviation": 10.0
        }
        
        sample = Sample(spots=spots_data, spot_statistics=stats_data, parameters=None)
        
        assert sample.data_statistics is not None
        assert sample.data_statistics.adjusted_average == 100.0
    
    def test_init_spots_polygon_parameters(self):
        """Test init_spots with polygon parameters."""
        spots_data = [
            {"mean_minus_min": 100.0, "normalized_mean": 0.5, 
             "spot": 0, "row": 0, "col": 0, "min": 50.0, 
             "max": 200.0, "mean": 150.