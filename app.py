import os
import create_reverse_schedule
from flask import Flask, render_template, flash, redirect
from flask import url_for, request, send_from_directory


app = Flask(__name__)
app.secret_key = 'lalalalololo'
app.config.from_pyfile('settings.py')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/instrustions')
def instructions():
    return render_template('instructions.html')


@app.route('/process_form', methods=['POST'])
def process_file():
    def random_filename(filename):
        import uuid
        ext = filename.split('.')[-1]
        return uuid.uuid4().hex + '.' + ext

    def check_exit():
        flag = True
        if not request.files.get('file'):
            flash('没有上传文件')
            flag = False
        elif request.files.get('file').filename.split('.')[-1] not in\
                ['xls', 'xlsx']:
            flash('请上传excel表格')
            flag = False
        if not request.form.get('from_week') or\
           not request.form.get('to_week'):
            flash('请填写起始日期')
            flag = False
        if not request.form.get('from_week').isdigit() or\
           not request.form.get('to_week').isdigit():
            flash('起止日期应是数字')
            flag = False
        if int(request.form.get('from_week')) < 1 or\
           int(request.form.get('to_week')) > app.config['TERM_WEEK_NUMBER']:
            flash('起止日期错误')
            flag = False
        return flag

    print(request.files)
    print(request.form)
    print(request.form.get('from_week').isdigit())
    if not check_exit():
        return redirect(url_for('index'))

    file = request.files.get('file')
    row_filename = file.filename
    new_filename = random_filename(row_filename)
    file.save(os.path.join(app.config['UPLOAD_PATH'], new_filename))

    cd = create_reverse_schedule.course_data(app.config['TERM_WEEK_NUMBER'],
                                             app.config['DATA_FILENAME'],
                                             app.config['ENGLISH_FILENAMES'])
    department = cd.get_input(os.path.join(app.config['UPLOAD_PATH'],
                                           new_filename))
    data = cd.department_no_lesson_schedule(department)
    four_class_a_day = 'four_class_a_day' in request.form.getlist('options')
    no_night = 'no_night' in request.form.getlist('options')
    no_weekend = 'no_weekend' in request.form.getlist('options')
    week_range = [int(request.form.get('from_week')),
                  int(request.form.get('to_week'))]
    data = cd.screen_data(data,
                          four_class_a_day=four_class_a_day,
                          no_night=no_night,
                          no_weekend=no_weekend,
                          week_range=week_range)
    cd.storage_data(data, os.path.join(app.config['OUTPUT_PATH'],
                                       'output.xls'))
    return send_from_directory(app.config['OUTPUT_PATH'], 'output.xls')
