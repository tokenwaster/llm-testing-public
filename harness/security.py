"""Browser protections for reports and untrusted model artifacts."""
import base64
import hashlib
import html
import re
from html.parser import HTMLParser


PREVIEW_CSP = ("default-src 'none'; script-src 'unsafe-inline'; "
               "style-src 'unsafe-inline'; img-src data: blob:; "
               "media-src data: blob:; font-src data:; connect-src 'none'; "
               "form-action 'none'; base-uri 'none'")
REPORT_ONLY_CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                   "img-src 'self' data:; object-src 'none'; base-uri 'none'; "
                   "form-action 'none'; frame-ancestors 'self'")


def isolated_preview(source: str) -> str:
    storage = '''<script>(()=>{for(const name of ['localStorage','sessionStorage']){
      const values=new Map();const storage={get length(){return values.size;},
        key(i){return Array.from(values.keys())[i]??null;},
        getItem(k){return values.get(String(k))??null;},
        setItem(k,v){values.set(String(k),String(v));},
        removeItem(k){values.delete(String(k));},clear(){values.clear();}};
      Object.defineProperty(window,name,{value:storage,configurable:false});
    }})();</script>'''
    return ('<!doctype html><meta http-equiv="Content-Security-Policy" content="'
            + html.escape(PREVIEW_CSP, quote=True) + '">' + storage + source)


def _hash(source: str) -> str:
    digest = hashlib.sha256(source.encode('utf-8')).digest()
    return "'sha256-" + base64.b64encode(digest).decode('ascii') + "'"


class _Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.handlers = []
        self.extra_hashes = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'meta' and attributes.get('name') == 'preview-script-hashes':
            self.extra_hashes.extend(re.findall(r"'sha256-[A-Za-z0-9+/]{43}='", attributes.get('content', '')))
        if tag == 'script':
            self.current = []
        for name, value in attrs:
            if name.startswith('on') and value:
                self.handlers.append(value)
            if tag == 'iframe' and name == 'srcdoc' and value:
                child = _Scripts()
                child.feed(value)
                self.scripts.extend(child.scripts)
                self.handlers.extend(child.handlers)

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'script' and self.current is not None:
            self.scripts.append(''.join(self.current))
            self.current = None


def secure_report(source: str) -> str:
    """Hash the final authored scripts, including SEO and sharing additions.

    This is defense in depth, not HTML sanitization. All untrusted values still
    require contextual escaping before rendering. srcdoc remains isolated.
    """
    source = re.sub(r'<meta data-report-csp[^>]*>', '', source)
    parser = _Scripts()
    parser.feed(source)
    hashes = sorted({_hash(s) for s in parser.scripts + parser.handlers} | set(parser.extra_hashes))
    scripts = ' '.join(hashes) or "'none'"
    if parser.handlers or parser.extra_hashes:
        scripts = "'unsafe-hashes' " + scripts
    policy = (f"default-src 'none'; script-src {scripts}; "
              "style-src 'unsafe-inline'; img-src 'self' data: blob:; "
              "font-src 'self' data:; media-src 'self' blob:; "
              "connect-src 'self'; frame-src 'self' about:; "
              "object-src 'none'; base-uri 'none'; form-action 'none'")
    tag = '<meta data-report-csp http-equiv="Content-Security-Policy" content="' + html.escape(policy, quote=True) + '">'
    return source.replace('<head>', '<head>' + tag, 1)


def preview_hashes(source: str) -> list[str]:
    parser = _Scripts()
    parser.feed(source)
    return sorted({_hash(s) for s in parser.scripts + parser.handlers})


def json_for_script(value) -> str:
    import json
    return (json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
            .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))
