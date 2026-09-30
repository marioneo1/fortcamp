"""Local-only board preview server; serves runtime assets without starting the game."""
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        original=super().translate_path(path)
        relative=Path(original).relative_to(Path.cwd())
        if relative.parts and relative.parts[0]=='assets':return str(ROOT/'frontend/public'/relative)
        return str(ROOT/relative)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
