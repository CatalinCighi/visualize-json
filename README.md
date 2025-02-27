# jsontree - Directory Mapping Tool

A Python package that maps the structure of a directory while respecting `.gitignore` rules, with visualization capabilities and trimming options.

## Features

- Maps directory structure in JSON, YAML, or XML formats
- Automatically respects `.gitignore` rules
- Trims common directories like `.git`, `__pycache__`, etc.
- Interactive visualization of directory structure
- Web server for sharing the visualization
- Docker support for containerized usage
- Flexible command-line interface
- Can be used programmatically in other Python projects

## Installation

Install directly from GitHub:

```bash
# Install from the repository
pip install git+https://github.com/yourusername/jsontree.git

# Or after cloning the repository
git clone https://github.com/yourusername/jsontree.git
cd jsontree
pip install .
```

## Command Line Usage

Basic mapping:

```bash
# Map the current directory in JSON format (default)
jsontree

# Map a specific directory in YAML format
jsontree --directory /path/to/your/directory --format yaml
```

Trimming options:

```bash
# Map with common directories excluded
jsontree --trim

# Map with custom exclude patterns
jsontree --trim --exclude .git node_modules dist
```

Visualization options:

```bash
# Generate visualization HTML
jsontree --visualize

# Generate visualization and open in browser
jsontree --visualize --open

# Start a web server to view the visualization
jsontree --serve --port 8080
```

All options:

```bash
# Full example with all options
jsontree --directory /path/to/dir --format json --trim --exclude .git __pycache__ --visualize --serve --port 8080
```

Help information:

```bash
# Show all available options
jsontree --help

# Show version
jsontree --version
```

## Docker Usage

```bash
# Build the Docker image
docker build -t jsontree .

# Run the container mapping a directory
docker run -v /path/to/your/directory:/data jsontree

# Run with specific options
docker run -v /path/to/your/directory:/data jsontree --format yaml --trim
```

## Python API Usage

```python
from jsontree import mapper

# Basic mapping
result = mapper.create_map()

# Map with all options
result = mapper.create_map(
    directory="/path/to/your/directory",
    output_format="json",
    exclude_patterns=[".git", "__pycache__", "node_modules"],
    trim=True,
    visualize=True,
    verbose=True
)

# Get the paths to the generated files
structure_path = result["structure"]
visualization_path = result["visualization"]  # Only if visualize=True
```

Run a visualization server:

```python
from jsontree import server

# Create and run a server for a structure.json file
app = server.create_server("/path/to/structure.json", port=5000)
app.run(debug=True)
```

## Output Examples

### JSON Format

```json
{
    "/path/to/dir": {
        "files": ["file1.txt", "file2.py"],
        "dirs": ["subdir1", "subdir2"]
    },
    "/path/to/dir/subdir1": {
        "files": ["file3.log"],
        "dirs": []
    }
}
```

### YAML Format

```yaml
/path/to/dir:
  files:
  - file1.txt
  - file2.py
  dirs:
  - subdir1
  - subdir2
/path/to/dir/subdir1:
  files:
  - file3.log
  dirs: []
```

### XML Format

```xml
<structure>
  <directory path="/path/to/dir">
    <files>
      <file>file1.txt</file>
      <file>file2.py</file>
    </files>
    <subdirectories>
      <directory>subdir1</directory>
      <directory>subdir2</directory>
    </subdirectories>
  </directory>
  <directory path="/path/to/dir/subdir1">
    <files>
      <file>file3.log</file>
    </files>
    <subdirectories>
    </subdirectories>
  </directory>
</structure>
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
