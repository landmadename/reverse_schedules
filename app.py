import os
import create_reverse_schedule
from flask import Flask, render_template, flash, redirect
from flask import url_for, request, send_from_directory
import logging


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"    # 日志格式化输出
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"                        # 日期格式
fp = logging.FileHandler('./log/re.log', encoding='utf-8')
fs = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])


app = Flask(__name__)
logging.info("raw path->" + os.getcwd())
if os.getcwd() == '/home/landmadename':
    os.chdir('/home/landmadename/reverse_schedules')
logging.info("now path->" + os.getcwd())
app.secret_key = 'lalalalololo'
app.config.from_pyfile('settings.py')
cd = create_reverse_schedule.course_data(app.config['TERM_WEEK_NUMBER'],
                                         app.config['DATA_FILENAME'],
                                         app.config['ENGLISH_FILENAMES'])

@app.route('/')
def index():
    logging.info("visit index")
    return render_template('index.html')


@app.route('/instructions')
def instructions():
    logging.info("visit instructons")
    return render_template('instructions.html')


@app.route('/class_list')
def class_list():
    logging.info("visit class list")
    return render_template('class_names.html')


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
            logging.info("没有上传文件")
            flag = False
        elif request.files.get('file').filename.split('.')[-1] not in\
                ['xls', 'xlsx']:
            flash('请上传excel表格')
            logging.info("请上传excel表格")
            flag = False
        if not request.form.get('from_week') or\
           not request.form.get('to_week'):
            flash('请填写起始日期')
            logging.info("请填写起始日期")
            flag = False
        if not request.form.get('from_week').isdigit() or\
           not request.form.get('to_week').isdigit():
            flash('起止日期应是数字')
            logging.info("起止日期应是数字")
            flag = False
        if int(request.form.get('from_week')) < 1 or\
           int(request.form.get('to_week')) > app.config['TERM_WEEK_NUMBER']:
            flash('起止日期错误')
            logging.info("起止日期错误")
            flag = False
        return flag

    logging.info("文件->" + str(request.files))
    logging.info("表单->" + str(request.form))    
    if not check_exit():
        return redirect(url_for('index'))

    file = request.files.get('file')
    raw_filename = file.filename
    new_filename = random_filename(raw_filename)
    file.save(os.path.join(app.config['UPLOAD_PATH'], new_filename))
    logging.info("新文件名->" + new_filename)

    department_data, revised = cd.get_input(os.path.join(app.config['UPLOAD_PATH'],
                                                new_filename))
    flag, data, infomation = cd.department_no_lesson_schedule(department_data,
                                                              revised)
    if flag is False:
        for i in infomation:
            flash(i)
            logging.info("输入文件错误-> " + i)
        return redirect(url_for('index'))
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
    cd.storage_data(infomation,
                    no_weekend,
                    week_range,
                    data,
                    os.path.join(app.config['OUTPUT_PATH'], 'output.xls'))
    return send_from_directory(app.config['OUTPUT_PATH'], 'output.xls')
