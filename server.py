import os
import json
import argparse
import webbrowser
import threading
import time
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify


def create_server(structure_path, port=5000, open_browser=True):
    """
    Create a Flask server to visualize the directory structure.

    Args:
        structure_path (str): Path to the structure.json file
        port (int): Port to run the server on
        open_browser (bool): Whether to open the browser automatically

    Returns:
        Flask app instance
    """
    # Get the directory containing the structure file
    structure_dir = os.path.dirname(os.path.abspath(structure_path))
    structure_file = os.path.basename(structure_path)

    # Create Flask app
    app = Flask(__name__, static_folder=structure_dir)

    @app.route("/")
    def index():
        # Serve the visualization HTML file
        from pkg_resources import resource_filename

        html_path = resource_filename("jsontree", "visualize.html")
        with open(html_path, "r") as f:
            html_content = f.read()
        return html_content

    @app.route("/structure.json")
    def serve_structure():
        # Serve the structure.json file
        return send_from_directory(structure_dir, structure_file)

    @app.route("/api/structure")
    def api_structure():
        # Return the structure as JSON API endpoint
        try:
            with open(os.path.join(structure_dir, structure_file), "r") as f:
                structure_data = json.load(f)
            return jsonify(structure_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Open browser in a separate thread
    if open_browser:

        def open_browser_delayed():
            time.sleep(1.0)  # Wait for server to start
            webbrowser.open(f"http://localhost:{port}")

        threading.Thread(target=open_browser_delayed).start()

    return app


def run_server():
    """
    Run the Flask server from command line.
    """
    parser = argparse.ArgumentParser(
        description="Run a visualization server for directory structure"
    )
    parser.add_argument("structure_path", help="Path to structure.json file")
    parser.add_argument("--port", type=int, default=5000, help="Port to run server on")
    parser.add_argument(
        "--no-browser", action="store_true", help="Do not open browser automatically"
    )

    args = parser.parse_args()

    app = create_server(
        args.structure_path, port=args.port, open_browser=not args.no_browser
    )

    print(f"Starting server at http://localhost:{args.port}")
    app.run(debug=True, port=args.port)


if __name__ == "__main__":
    run_server()
