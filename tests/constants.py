HTML = '''<html>
            <body>
                <h1>
                    HTML
                </h1>
            </body>
        </html>'''

JS = '''<script>
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    </script>'''

JS_WITH_TYPE = '''<script type="application/javascript">
        ["J", "S"].reduce(
            function (a, r) {
                return a + r
            })
    </script>'''

LESS = '''<style>
        @a: red;
        body {
            color: @a;
        }
    </style>'''

FALSE_LESS = '''<style>
        body {
            color: red;;
        }
    </style>'''

JS_RAW = '''
console.warn(         [
    'testing',

    ' suite'    ]
  );
'''

LESS_RAW = '''
@a:     red;

body    {
    color:       @a;
}
'''

JS_TEMPLATE_LITERALS = '''
const a = 'something';
const b = ` more  than    ${a}  `;
'''

HTML_EMBEDDED_TAGS = '\n'.join([
    '<html>',
    JS,
    '<script type="text/script" src="testing/88.js"></script>',
    LESS,
    '<script type="application/script" src="testing/1.js"></script>',
    JS,
    '<script src="testing/nested/2.js"></script>',
    '</html>'
])

MINIFED_HTML = b'<html> <body> <h1> HTML </h1> </body> </html>'

MINIFIED_JS = b'<script>["J","S"].reduce(function(a,r){return a+r})</script>'

MINIFIED_JS_WITH_TYPE = (b'<script type="application/javascript">["J","S"].'
                         b'reduce(function(a,r){return a+r})</script>')

MINIFED_LESS = b'<style>body{color:red;}</style>'

MINIFIED_JS_RAW = b"console.warn(['testing',' suite']);"

MINIFIED_LESS_RAW = b'body{color:red;}'

MINIFIED_JS_TEMPLATE_LITERALS =\
    "const a='something';const b=` more  than    ${a}  `;"


MINIFED_HTML_EMBEDDED_TAGS = bytes(''.join([
    '<html> ',
    MINIFIED_JS.decode('utf-8'),
    ' <script type="text/script" src="testing/88.js"></script> ',
    MINIFED_LESS.decode('utf-8'),
    ' <script type="application/script" src="testing/1.js"></script> ',
    MINIFIED_JS.decode('utf-8'),
    ' <script src="testing/nested/2.js"></script> </html>']).encode('utf-8'))
