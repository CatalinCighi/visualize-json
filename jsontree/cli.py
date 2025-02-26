import argparse
import os
import sys
import webbrowser
from . import mapper
from . import server


def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Map a directory structure with respect to .gitignore rules."
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Path to the directory to map (default: current working directory)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml", "xml"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "-t",
        "--trim",
        action="store_true",
        help="Trim the output by excluding common directories like .git, __pycache__, etc.",
    )

    parser.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        help="Patterns to exclude when trimming (use with --trim)",
    )

    parser.add_argument(
        "-v",
        "--visualize",
        action="store_true",
        help="Generate an HTML visualization of the directory structure (works only with JSON format)",
    )

    parser.add_argument(
        "-o",
        "--open",
        action="store_true",
        help="Open the visualization in a web browser after generating (use with --visualize)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )

    parser.add_argument(
        "--serve",
        action="store_true",
        help="Start a web server to visualize the directory structure",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on (default: 5000)",
    )

    args = parser.parse_args()

    # Show version if requested
    if args.version:
        from . import __version__

        print(f"jsontree version {__version__}")
        return 0

    # Check for visualization format compatibility
    if args.visualize and args.format != "json":
        print(
            "Warning: Visualization only works with JSON format. Switching to JSON format."
        )
        args.format = "json"

    try:
        result_paths = mapper.create_map(
            directory=args.directory,
            output_format=args.format,
            exclude_patterns=args.exclude,
            trim=args.trim,
            visualize=args.visualize,
            verbose=args.verbose,
        )

        if result_paths:
            # Open visualization in browser if requested
            if args.open and args.visualize and "visualization" in result_paths:
                viz_path = result_paths["visualization"]
                print(f"Opening visualization in browser: {viz_path}")
                webbrowser.open(f"file://{viz_path}")

            # Start web server if requested
            if args.serve and "structure" in result_paths:
                structure_path = result_paths["structure"]
                if args.format != "json":
                    print(
                        "Warning: Server visualization requires JSON format. Please re-run with --format json"
                    )
                else:
                    print(f"Starting server at http://localhost:{args.port}")
                    app = server.create_server(structure_path, port=args.port)
                    app.run(debug=True, port=args.port)

            return 0
        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
