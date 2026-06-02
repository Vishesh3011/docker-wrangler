from flask import Flask, render_template, request, redirect
from app.models import add_task, get_tasks, init_db

app = Flask(__name__)


@app.before_request
def setup():
    pass


@app.route('/')
def index():
    tasks = get_tasks()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
    task_name = request.form.get('task')
    if task_name:
        add_task(task_name)
    return redirect('/')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8000)
