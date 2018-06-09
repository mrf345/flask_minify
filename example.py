from flask import Flask, render_template
from flask_minify import minify
from atexit import register
from os import remove

app = Flask(__name__, template_folder='.')
minify(app=app, js=True, cache=True)

def cleanUp():
    try:
        remove('index.html')
    except Exception:
        pass

register(cleanUp)

@app.route('/')
def root():
    with open('index.html', 'w+') as file:
        file.write("<html>\n<head>\n")
        file.write('\n<script></script><style rel="dsff" link="dsdsf"> </style>\n')
        file.write('<script>\nif (true) {\n\tconsole.log("working !")\n}\n</script>')
        file.write('<style>\n body {\n background-color: black; \n} h1 {\n color: white;\n}\n</style>')
        file.write("\n</head>\n<body>\n<h1>Flask-Less Example !</h1>\n</body>\n</html>\n")
    return render_template('index.html')


app.run(debug=True, port=4000)