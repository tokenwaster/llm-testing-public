
from harness.util import strip_output_comments


def test_css_comments_outside_pre_are_stripped():
    html = "<style>/* a note */ .x { color:red; }</style>"
    out = strip_output_comments(html)
    assert "a note" not in out
    assert ".x { color:red; }" in out


def test_js_line_comments_outside_pre_are_stripped():
    html = "<script>\n  // explain\n  var x = 1;\n</script>"
    out = strip_output_comments(html)
    assert "explain" not in out
    assert "var x = 1;" in out


def test_urls_survive():
    html = '<a href="https://example.com/x">e</a>'
    assert "https://example.com/x" in strip_output_comments(html)


def test_a_models_block_comment_is_left_alone():
    html = "<pre>/* the model wrote this */\nconst x = 1;</pre>"
    assert strip_output_comments(html) == html


def test_a_models_line_comment_is_left_alone():
    html = "<pre>const x = 1; // the model's own note\n</pre>"
    assert strip_output_comments(html) == html


def test_an_unbalanced_comment_in_model_output_cannot_eat_the_page():
    html = ('<details id="m-a"><pre>/* unclosed in A</pre></details>'
            '<details id="m-b"><pre>closing here */</pre></details>')
    out = strip_output_comments(html)
    assert 'id="m-a"' in out
    assert 'id="m-b"' in out, "a later result block was swallowed"


def test_page_css_is_still_stripped_when_a_pre_is_present():
    html = ("<style>/* ours */ .a{}</style>"
            "<pre>/* theirs */</pre>"
            "<script>\n// ours\nvar y=2;\n</script>")
    out = strip_output_comments(html)
    assert "ours" not in out
    assert "/* theirs */" in out
    assert ".a{}" in out and "var y=2;" in out


def test_multiple_pre_blocks_all_survive():
    html = ("<pre>// one</pre><style>/* x */</style>"
            "<pre>// two</pre><pre>/* three */</pre>")
    out = strip_output_comments(html)
    assert "// one" in out and "// two" in out and "/* three */" in out
    assert "/* x */" not in out


def test_pre_with_attributes_is_recognised():
    html = '<pre class="out" data-m="x">// kept</pre>'
    assert "// kept" in strip_output_comments(html)
