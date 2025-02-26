import os
import json
import yaml
import logging
import shutil
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
from pathspec import PathSpec


# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def load_gitignore_patterns(gitignore_path):
    """
    Load .gitignore patterns using pathspec library.

    Args:
        gitignore_path (str): Path to the .gitignore file

    Returns:
        PathSpec: Compiled gitignore patterns
    """
    try:
        with open(gitignore_path, "r") as file:
            logger.info(f"Loaded .gitignore from {gitignore_path}")
            return PathSpec.from_lines("gitwildmatch", file)
    except FileNotFoundError:
        logger.info(
            f"No .gitignore file found at {gitignore_path}. Continuing without it."
        )
        return PathSpec.from_lines("gitwildmatch", [])


def map_directory(directory, pathspec):
    """
    Map the directory structure while respecting .gitignore rules.

    Args:
        directory (str): Directory to map
        pathspec (PathSpec): Compiled gitignore patterns

    Returns:
        dict: Mapped directory structure
    """
    structure = {}
    for root, dirs, files in os.walk(directory):
        logger.debug(f"Scanning directory: {root}")

        # Convert paths to be relative to the directory for proper pathspec matching
        rel_root = os.path.relpath(root, directory)

        # Filter directories and files using pathspec
        dirs[:] = [
            d
            for d in dirs
            if not pathspec.match_file(
                os.path.join(rel_root, d) if rel_root != "." else d
            )
        ]

        filtered_files = [
            f
            for f in files
            if not pathspec.match_file(
                os.path.join(rel_root, f) if rel_root != "." else f
            )
        ]

        if dirs or filtered_files:
            structure[root] = {"files": filtered_files, "dirs": dirs}
            logger.debug(
                f"Added to structure: {root} with {len(filtered_files)} files and {len(dirs)} directories"
            )

    return structure


def trim_structure(structure, exclude_patterns):
    """
    Trim a directory structure by excluding directories matching patterns.

    Args:
        structure (dict): The directory structure to trim
        exclude_patterns (list): List of patterns to exclude

    Returns:
        dict: Trimmed directory structure
    """
    # Create a new trimmed structure
    trimmed_structure = {}

    # Filter out paths containing exclude patterns
    for path, content in structure.items():
        # Check if path contains any exclude pattern
        if not any(pattern in path for pattern in exclude_patterns):
            # Filter dirs that contain exclude patterns
            filtered_dirs = [
                d
                for d in content.get("dirs", [])
                if not any(pattern in d for pattern in exclude_patterns)
            ]

            # Create filtered entry
            trimmed_structure[path] = {
                "files": content.get("files", []),
                "dirs": filtered_dirs,
            }

    logger.info(f"Original structure had {len(structure)} directories")
    logger.info(f"Trimmed structure has {len(trimmed_structure)} directories")

    return trimmed_structure


def save_output(data, format_type, output_path):
    """
    Save the mapped directory structure in the specified format.

    Args:
        data (dict): Mapped directory structure
        format_type (str): Output format ('json', 'yaml', or 'xml')
        output_path (str): Path to save the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if format_type == "json":
            with open(output_path, "w") as file:
                json.dump(data, file, indent=4)
            logger.info(f"Saved structure as JSON at {output_path}")

        elif format_type == "yaml":
            with open(output_path, "w") as file:
                yaml.dump(data, file, default_flow_style=False)
            logger.info(f"Saved structure as YAML at {output_path}")

        elif format_type == "xml":
            root = Element("structure")
            for path, content in data.items():
                dir_element = SubElement(root, "directory", {"path": path})
                files_element = SubElement(dir_element, "files")
                for file in content["files"]:
                    SubElement(files_element, "file").text = file
                dirs_element = SubElement(dir_element, "subdirectories")
                for subdir in content["dirs"]:
                    SubElement(dirs_element, "directory").text = subdir
            tree = ElementTree(root)
            tree.write(output_path)
            logger.info(f"Saved structure as XML at {output_path}")

        return True
    except Exception as e:
        logger.error(f"Error saving output: {e}")
        return False


def setup_visualization(directory, structure_path):
    """
    Sets up visualization resources in the target directory.

    Args:
        directory (str): Directory where visualization resources will be placed
        structure_path (str): Path to the structure.json file

    Returns:
        str: Path to the visualization HTML file
    """
    # Get the package root directory to copy the visualization template
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(os.path.dirname(current_dir), "visualize.html")

    # Copy the visualization HTML to the target directory
    viz_path = os.path.join(directory, "jsontree_visualize.html")

    try:
        # Copy the template
        shutil.copy2(template_path, viz_path)
        logger.info(f"Visualization interface copied to {viz_path}")

        return viz_path
    except Exception as e:
        logger.error(f"Error setting up visualization: {e}")
        return None


def create_map(
    directory=None,
    output_format="json",
    exclude_patterns=None,
    trim=False,
    visualize=False,
    verbose=False,
):
    """
    Main function that maps a directory and saves the output.

    Args:
        directory (str, optional): Directory to map. Defaults to current working directory.
        output_format (str, optional): Output format. Defaults to "json".
        exclude_patterns (list, optional): List of patterns to exclude when trimming.
        trim (bool, optional): Whether to trim the output. Defaults to False.
        visualize (bool, optional): Whether to set up visualization. Defaults to False.
        verbose (bool, optional): Enable verbose logging. Defaults to False.

    Returns:
        dict: Dictionary containing paths to the saved files
    """
    # Set logging level based on verbosity
    if verbose:
        logger.setLevel(logging.DEBUG)

    # Set directory to map
    directory_to_map = os.path.abspath(directory or os.getcwd())

    # Default exclude patterns if none provided
    if exclude_patterns is None and trim:
        exclude_patterns = [
            ".git",
            "venv",
            "__pycache__",
            ".egg-info",
            "dist",
            "build",
            "site-packages",
            ".ipynb_checkpoints",
        ]

    # Path to gitignore file
    gitignore_path = os.path.join(directory_to_map, ".gitignore")

    logger.info(f"Starting directory mapping for {directory_to_map}...")

    # Load gitignore patterns
    pathspec = load_gitignore_patterns(gitignore_path)

    # Map directory structure
    mapped_structure = map_directory(directory_to_map, pathspec)

    # Trim structure if requested
    if trim:
        mapped_structure = trim_structure(mapped_structure, exclude_patterns)

    # Path to save output
    output_path = os.path.join(directory_to_map, f"structure.{output_format}")

    # Output paths dictionary
    result_paths = {"structure": output_path}

    logger.info("Saving output...")

    # Save output in specified format
    save_success = save_output(mapped_structure, output_format, output_path)

    if save_success:
        logger.info(f"Process completed. Directory structure saved at {output_path}")

        # Set up visualization if requested
        if visualize and output_format == "json":
            viz_path = setup_visualization(directory_to_map, output_path)
            if viz_path:
                result_paths["visualization"] = viz_path
                logger.info(f"Visualization ready at {viz_path}")
            else:
                logger.warning("Failed to set up visualization")

        return result_paths
    else:
        logger.error("Failed to save directory structure")
        return None
