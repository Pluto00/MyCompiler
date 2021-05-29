from flask import Flask, request, render_template, jsonify
from Lexer.Lexer import Lexer

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/lexer/code", methods=["POST"])
def post_lexer_code():
    code = request.json.get("code")
    with open('code.cache', 'w', encoding='utf-8') as fh:
        fh.write(code)
    with open('code.cache', encoding='utf-8') as fh:
        response = Lexer(fh).parse()
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
