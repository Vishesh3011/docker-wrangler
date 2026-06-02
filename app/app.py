from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    tasks = []
    return render_template('index.html', tasks = tasks)

@app.route('/add', methods = ['POST'])
def add_task():
    task_name = request.form.get('task')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug = True, host = '0.0.0.0', port = 8000)