"""Serves RepeatMe on localhost and saves progress to progress.json next to this file.

Run it with start.bat (or `python server.py`); it opens the app in your browser.
"""
import http.server
import json
import os
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROGRESS = ROOT / "progress.json"
PORT = int(os.environ.get("REPEATME_PORT", 8765))
URL = f"http://localhost:{PORT}/"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_PUT(self):
        if self.path != "/progress.json":
            return self.send_error(404)
        try:
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            data = json.loads(body)
            if not isinstance(data.get("programs"), list):
                raise ValueError("missing programs list")
        except (ValueError, json.JSONDecodeError) as e:
            return self.send_error(400, str(e))
        # write to a temp file first so a crash never leaves a half-written progress.json
        tmp = PROGRESS.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(PROGRESS)
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        if self.command == "PUT":
            print(f"saved progress.json")


def main():
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError:
        # already running (e.g. start.bat clicked twice) - just open the app
        print(f"RepeatMe already running at {URL}")
        webbrowser.open(URL)
        return
    print(f"RepeatMe running at {URL}  -  progress is saved to {PROGRESS.name}")
    print("Close this window (or press Ctrl+C) to stop.")
    if "--no-browser" not in sys.argv:
        webbrowser.open(URL)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
