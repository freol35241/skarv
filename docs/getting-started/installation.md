# Installation

## Requirements

Skarv requires Python 3.10 or higher.

## Installing Skarv

### Using pip

The easiest way to install Skarv is using pip:

```bash
pip install skarv
```

### From Source

If you want to install from the latest development version:

```bash
git clone https://github.com/freol/skarv.git
cd skarv
pip install -e .
```

### Development Installation

For development work, install with development dependencies:

```bash
git clone https://github.com/freol/skarv.git
cd skarv
pip install -e ".[dev]"
```

## Dependencies

Skarv has the following dependencies:

- **eclipse-zenoh**: For key expression handling and pattern matching
- **Python 3.10+**: For modern Python features and type hints

## Verifying Installation

To verify that Skarv is installed correctly:

```python
import skarv

# Test basic functionality
@skarv.subscribe("test/*")
def test_handler(sample):
    print(f"Test successful: {sample.key_expr} = {sample.value}")

skarv.put("test/installation", "working")
```

If you see the output "Test successful: test/installation = working", then Skarv is installed correctly!

## Next Steps

- [Quick Start Tutorial](quick-start.md)
- [Overview](../user-guide/overview.md) 