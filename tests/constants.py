HTML = """<html>
            <body>
                <h1>
                    HTML
                </h1>
            </body>
        </html>"""

JS = """<script>
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    </script>"""

JS_WITH_TYPE = """<script type="application/javascript">
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    </script>"""

LESS = """<style>
        @a: red;
        body {
            color: @a;
        }
    </style>"""

FALSE_LESS = """<style>
        body {
            color: red;;
        }
    </style>"""

FALSE_JS = """<script>
        let body = (
            color: 'red';;
        }
    </script>"""

JS_RAW = """
console.warn(         [
    'testing',

    ' suite'    ]
  );
"""

LESS_RAW = """
@a:     red;

body    {
    color:       @a;
}
"""

JS_TEMPLATE_LITERALS = """
const a = 'something';
const b = ` more  than    ${a}  `;
"""

CSS_EDGE_CASES = """
:root {
  --main-bg-color: brown;
}

.some-class {
    color: rgba(202, 242, 255, 1);
    background-color: var(--main-bg-color);
}

#some-id {
    grid-area: 1 / 2 / 2 / 3;
}
"""

HTML_EMBEDDED_TAGS = "\n".join(
    [
        "<html>",
        JS,
        '<script type="text/script" src="testing/88.js"></script>',
        f"<style>{CSS_EDGE_CASES}</style>",
        '<script type="application/script" src="testing/1.js"></script>',
        JS,
        '<script src="testing/nested/2.js"></script>',
        "</html>",
    ]
)

HTML_CONDITIONAL_COMMENTS = """
<html>
    <header>
        <!--[if IE]>
            IE comment!
        <![endif]-->
    </header>
</html>
"""

MINIFIED_HTML_CONDITIONAL_COMMENTS = (
    b"<html><header><!--[if IE]>IE comment!<![endif]--></header></html>"
)

MINIFIED_HTML = b"<html><body><h1> HTML </h1></body></html>"
MINIFIED_HTML_GO = b"<html><body><h1>HTML</h1></body></html>"


MINIFIED_JS = b'<script>["J","S"].reduce(function(a,r){return a+r})</script>'

MINIFIED_JS_WITH_TYPE = (
    b'<script type="application/javascript">["J","S"].'
    b"reduce(function(a,r){return a+r})</script>"
)

MINIFIED_LESS = b"<style>body{color:red;}</style>"

MINIFIED_JS_RAW = b"console.warn(['testing',' suite']);"
MINIFIED_JS_RAW_GO = b'console.warn(["testing"," suite"])'


MINIFIED_LESS_RAW = b"body{color:red;}"

MINIFIED_JS_TEMPLATE_LITERALS = "const a='something';const b=` more  than    ${a}  `;"

MINIFIED_CSS_EDGE_CASES = (
    ":root{--main-bg-color:brown}.some-class{color:rgba(202,242,255,1);"
    "background-color:var(--main-bg-color)}#some-id{grid-area:1 / 2 / 2 / 3}"
)

MINIFIED_CSS_EDGE_CASES_GO = ":root{--main-bg-color:brown}.some-class{color:#caf2ff;background-color:var(--main-bg-color)}#some-id{grid-area:1/2/2/3}"

MINIFIED_HTML_EMBEDDED_TAGS = bytes(
    "".join(
        [
            "<html>",
            MINIFIED_JS.decode("utf-8"),
            '<script type="text/script" src="testing/88.js"></script>',
            f"<style>{MINIFIED_CSS_EDGE_CASES}</style>",
            '<script type="application/script" src="testing/1.js"></script>',
            MINIFIED_JS.decode("utf-8"),
            '<script src="testing/nested/2.js"></script></html>',
        ]
    ).encode("utf-8")
)
MINIFIED_HTML_EMBEDDED_TAGS_GO = bytes(
    "".join(
        [
            "<html>",
            MINIFIED_JS.decode("utf-8"),
            '<script type="text/script" src="testing/88.js"></script>',
            f"<style>{MINIFIED_CSS_EDGE_CASES_GO}</style>",
            '<script type="application/script" src="testing/1.js"></script>',
            MINIFIED_JS.decode("utf-8"),
            '<script src="testing/nested/2.js"></script></html>',
        ]
    ).encode("utf-8")
)

COMPILED_LESS_RAW = "body {\n color: red;\n}"
