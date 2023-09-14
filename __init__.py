from flask import Flask, render_template, request
from analyze import analyze
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('app.html')


@app.route('/save_code', methods=['GET', 'POST'])
def save_code():
    code = request.form.get('code')
    with open('test_code.py', 'w') as file:
        file.write(code)
    res = analyze()
    print("Content saved to file.")
    return res


if __name__ == '__main__':
    app.run()
