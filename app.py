from flask import Flask, request, render_template, jsonify
from Lexer import Lexer
from SyntaxAnalyzer import SLRTable

app = Flask(__name__)
lex = Lexer()
slr = SLRTable(lexer=lex)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/lexer/code", methods=["POST"])
def post_lexer_code():
    code = request.json.get("code")
    with open('code.cache', 'w', encoding='utf-8') as fh:
        fh.write(code)
    with open('code.cache', encoding='utf-8') as fh:
        response = lex.parse(fh)
    return jsonify(response)


@app.route("/api/syntax/analyzer/code", methods=["POST"])
def post_syntax_analyzer_code():
    code = request.json.get("code")
    with open('code.cache', 'w', encoding='utf-8') as fh:
        fh.write(code)
    with open('code.cache', encoding='utf-8') as fh:
        res = slr.analyze(fh)
    response = {"output": ""}
    response["output"] += "栈顶     输入     操作     匹配状态\n"
    for i in range(len(res['stack'])):
        response["output"] += ("%-8s %-8s %-8s " % (
            res['stack'][i], res['input'][i], res['operations'][i])) + ' '.join(res['matched'][i + 1]) + '\n'
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
