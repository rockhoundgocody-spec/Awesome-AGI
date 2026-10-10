#!/usr/bin/env python3
"""Minimal dev server: renders README.md as a styled HTML page on port 3000.

Reads README.md fresh on every request so edits are reflected immediately.
Serves static files (images, etc.) from the repo root.
"""
import html
import http.server
import os
import socketserver
import pathlib

import markdown

PORT = int(os.environ.get("PORT", "3000"))
ROOT = pathlib.Path(__file__).resolve().parent

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Awesome AGI Resources</title>
<style>
  :root {{
    --bg: #0d1117;
    --fg: #c9d1d9;
    --accent: #58a6ff;
    --border: #30363d;
    --code-bg: #161b22;
    --link: #58a6ff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
  }}
  .container {{
    max-width: 980px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
  }}
  h1, h2, h3, h4 {{ color: #f0f6fc; margin-top: 2rem; }}
  h1 {{ border-bottom: 1px solid var(--border); padding-bottom: .3rem; }}
  h2 {{ border-bottom: 1px solid var(--border); padding-bottom: .3rem; }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1rem 0;
    display: block;
    overflow-x: auto;
  }}
  th, td {{
    border: 1px solid var(--border);
    padding: .5rem .75rem;
    text-align: left;
  }}
  th {{ background: var(--code-bg); }}
  img {{ max-width: 100%; border-radius: 8px; }}
  code {{
    background: var(--code-bg);
    padding: .15rem .35rem;
    border-radius: 4px;
    font-size: .9em;
  }}
  blockquote {{
    border-left: 4px solid var(--accent);
    margin: 1rem 0;
    padding: .5rem 1rem;
    background: var(--code-bg);
    border-radius: 0 6px 6px 0;
  }}
  hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
  ul {{ padding-left: 1.5rem; }}
  li {{ margin: .25rem 0; }}
</style>
</head>
<body>
<div class="container">
{content}
</div>
</body>
</html>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        # Strip query string for path matching (preview proxy adds ?previewFE_version=1)
        path = self.path.split("?", 1)[0]
        # Serve the rendered README at the root path
        if path in ("", "/"):
            self.serve_readme()
            return
        # Let the default handler serve static files (images, etc.)
        super().do_GET()

    def serve_readme(self):
        readme_path = ROOT / "README.md"
        try:
            md_text = readme_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.send_error(404, "README.md not found")
            return
        extensions = ["tables", "fenced_code", "sane_lists", "attr_list"]
        html_body = markdown.markdown(md_text, extensions=extensions)
        page = TEMPLATE.format(content=html_body)
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Suppress noisy request logs; keep error logs
        if args and "404" in str(args[0]):
            super().log_message(fmt, *args)


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving README.md on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
