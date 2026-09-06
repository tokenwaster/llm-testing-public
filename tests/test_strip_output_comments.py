import json

from harness.util import strip_output_comments


def test_embedded_model_output_and_executable_literals_survive_document_processing():
    output = 'const x = 1; // note\n/* open across a response */\nhttps://example.com'
    payload = json.dumps({'output': output})
    page = '<script>const CASES=' + payload + ';</script><pre>/* unclosed</pre>'
    processed = strip_output_comments(page)
    serialized = processed.split('const CASES=', 1)[1].split(';</script>', 1)[0]
    assert json.loads(serialized)['output'] == output
    assert processed.endswith('<pre>/* unclosed</pre>')
    css = '<style>.x:after{content:"/* literal */"}</style>'
    assert strip_output_comments(css) == css
