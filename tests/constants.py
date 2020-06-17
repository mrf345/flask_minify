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
const a = 'something'
const b = ` more  than    ${a}  `
'''

MINIFED_HTML = b'<html> <body> <h1> HTML </h1> </body> </html>'

MINIFIED_JS = b'<script>["J","S"].reduce(function(a,r){return a+r})</script>'

MINIFED_LESS = b'<style>body{color:red;}</style>'

MINIFIED_JS_RAW = b"console.warn(['testing',' suite']);"

MINIFIED_LESS_RAW = b'body{color:red;}'

MINIFIED_JS_TEMPLATE_LITERALS =\
    "const a='something';const b=` more  than    ${a}  `"


def MINIFED_STRIPED(value):
    constant = globals().get(value, '')

    if type(constant) == bytes:
        constant = bytes(constant.decode('utf-8')
                                 .replace('<style>', '')
                                 .replace('</style>', '')
                                 .replace('<script>', '')
                                 .replace('</script>', '')
                                 .encode('utf-8'))
    else:
        constant = str(constant.encode('utf-8')
                               .replace('<style>', '')
                               .replace('</style>', '')
                               .replace('<script>', '')
                               .replace('</script>', '')
                               .decode('utf-8'))

    return constant
