import re
import logging
from fuzzywuzzy import fuzz


class excel():
    def __init__(self):
        import xlwt
        self.pointer = 0
        self.book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.sheet = []
        self.style = xlwt.XFStyle()
        self.style.alignment.wrap = 1

    def add_a_sheet(self, name):
        self.sheet.append(self.book.add_sheet(name, cell_overwrite_ok=True))
        self.pointer = 0

    def add_a_row(self, data):
        for e, i in enumerate(data):
            self.sheet[-1].write(self.pointer, e, i, self.style)
        self.pointer = self.pointer + 1

    def save(self, fp):
        self.book.save(fp)


class course_data():
    def __init__(self,
                 term_week_number=18,
                 course_data_filename='classes_data',
                 english_filenames=['2018-2019-18.xlsx'],
                 ):
        self.term_week_number = term_week_number
        self.data = self.load_data(course_data_filename)
        self.class_names = [i[10] for i in self.data]
        self.set_of_class_names = list(set(self.class_names))
        self.set_of_class_names_for_search = \
            self.process_class_names_for_search()
        self.course_time = \
            [self.format_course_time((i[1], i[4])) for i in self.data]
        self.art_time = self.create_art_time()
        self.english_data = self.format_english_data(english_filenames)
        self.sids = self.english_data.keys()
        self.art_classes = set([i[-1] for i in self.data if i[-3] == '艺术设计学院'])

    def search(self, kw):
        kw = ' '.join([ii for ii in kw])
        data = [(fuzz.token_set_ratio(i, kw), self.set_of_class_names[e])
                for e, i in enumerate(self.set_of_class_names_for_search)]
        data.sort(reverse=True)
        data = [i for i in data if i[0] >= 85]
        return [i[1] for i in data]

    def process_class_names_for_search(self):
        data = []
        for i in self.set_of_class_names:
            data.append(' '.join([ii for ii in i]))
        return data

    def create_art_time(self):
        data = []
        for i in range(10):
            if i % 2 == 0:
                data.append((list(range(1, self.term_week_number + 1)),
                             int(i / 2 + 1), [1, 2]))
            else:
                data.append((list(range(1, self.term_week_number + 1)),
                             int((i + 1) / 2), [3, 4]))
        return data

    def format_course_time(self, data):
        data, weekday = data
        week = []
        week_range = re.findall('(.*?)\(', data)[0]
        week_range = week_range.split(',')
        index = re.findall('\((.*?)\)', data)[0]
        index = index.split(',')
        index = [int(i) for i in index]
        for i in week_range:
            t = re.findall('(\d+)-(\d+)', i)
            if t == []:
                week.append(int(re.findall('\d+', i)[0]))
            else:
                a, b = t[0]
                if '单' in i or '双' in i:
                    week = week + list(range(int(a), int(b) + 1, 2))
                else:
                    week = week + list(range(int(a), int(b) + 1))
        return week, weekday, index

    def format_english_data(self, filenames):
        english_data = self.get_english_courses_data(filenames)
        english_dict = {}
        week = list(range(1, self.term_week_number + 1))
        weekday_dict = {'周一': 1,
                        '周二': 2,
                        '周三': 3,
                        '周四': 4,
                        '周五': 5,
                        '周六': 6,
                        '周日': 7}

        for sid, data in english_data:
            data = data.split('；')
            english_dict[sid] = []
            for i in data:
                weekday = re.findall('周.', i)
                if len(weekday) != 1:
                    print('---->', i)
                assert len(weekday) == 1
                weekday = weekday_dict[weekday[0]]
                english_index = re.findall('(\d+)-(\d+)', i)
                assert len(english_index[0]) == 2
                english_index = [int(i) for i in english_index[0]]
                english_dict[sid].append((week, weekday, english_index))

        return english_dict

    def possible_class_names(self, class_name):
        possibles = str(self.search(class_name))
        infomation = '您输入的班级"{}"电脑看不懂，您可能找的是 {}。若不是，请在 {} 中寻找规范的班级名称'\
            .format(class_name,
                    possibles,
                    'http://re.fastbreakfast.top/class_list')

        return infomation

    def load_data(self, filename):
        import pickle
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        return data

    def get_input(self, filename):
        import xlrd

        input_data = []
        data = []
        revised = []

        ef = xlrd.open_workbook(filename)
        sheet = ef.sheet_by_index(0)
        for i in range(sheet.nrows - 1):
            i = i + 1
            if sheet.row_values(i)[0] == '':
                i = i + 1
                break
            input_data.append(sheet.row_values(i)[:3])
        if i != sheet.nrows - 1:
            for i in range(i, sheet.nrows):
                revised.append([ii for ii in sheet.row_values(i) if ii != ''])
        for i in input_data:
            try:
                i[1] = int(i[1])
            except Exception as e:
                if i[1] == '':
                    i[1] = '空'
                else:
                    i[1] = '学号请输入数字'
            data.append([str(i[0].upper()).strip(),
                         str(i[1]).strip(),
                         str(i[2]).strip()])
        return (data, revised)

    def get_english_courses_data(self, filenames):
        import xlrd

        english_data = []
        for i in filenames:
            ef = xlrd.open_workbook(i)
            sheet = ef.sheet_by_index(0)
            for i in range(sheet.nrows - 1):
                i = i + 1
                data = sheet.row_values(i)
                data = [data[0], data[-3]]
                english_data.append(data)
        return english_data

    def get_courses_time_from_class_name(self, class_name):
        courses = []
        for e, i in enumerate(self.class_names):
            if i == class_name:
                courses.append(self.course_time[e])
        return courses

    def change_schedule(self, table, time, value=""):
        for i in time:
            for week in i[0]:
                if week <= self.term_week_number:
                    week = week - 1
                    weekday = i[1]
                    weekday = weekday - 1
                    for index in i[2]:
                        index = index - 1
                        table[week][index][weekday] = value
        return table

    def one_no_lesson_schedule(self, data, revised):
        class_name, sid, name = data
        table = [[([name] * 7) for i in range(11)]
                 for ii in range(self.term_week_number)]
        courses_time = self.get_courses_time_from_class_name(class_name)
        english_time = self.english_data.get(sid)
        table = self.change_schedule(table, courses_time)
        if english_time is not None:
            table = self.change_schedule(table, english_time)
        # if class_name in self.art_classes:
        #     table = self.change_schedule(table, self.art_time)
        if class_name in revised.keys():
            table = self.change_schedule(table, revised[class_name][0], name)
            table = self.change_schedule(table, revised[class_name][1])
        return table

    def combine(self, tables):
        table = [[([[], [], [], [], [], [], []]) for i in range(11)]
                 for ii in range(self.term_week_number)]
        for i in tables:  # each one
            for ee, ii in enumerate(i):  # each week
                for eee, iii in enumerate(ii):  # each row
                    for eeee, iiii in enumerate(iii):  # each value
                        if iiii != '':
                            table[ee][eee][eeee].append(iiii)
        return table

    def check_user_data(self, data, revised):
        wrong_data = []
        flag = 0
        for class_name, sid, name in data:
            user = [class_name, sid, name, '---->']
            infomation = []
            if class_name not in self.set_of_class_names:
                infomation.append(self.possible_class_names(class_name))
                flag = 1
            if sid not in self.sids:
                infomation.append('学号错误或没有英语课(如果确认没有英语课，可以忽略)')
            if name == '':
                infomation.append('没有名字')
                flag = 1

            if infomation != []:
                user.append('  并且  '.join(infomation))
                wrong_data.append('  '.join(user))
        
        for i in revised:
            infomation = []
            if i[0] not in self.set_of_class_names:
                infomation.append(self.possible_class_names(i[0]))
                flag = 1
            if len(i) < 2:
                infomation.append('修订参数没有写全')
                flag = 1
                continue
            for ii in i[1:]:
                try:
                    if ii[0] not in "ad":
                        infomation.append('修正参数"' + str(ii) + '"应该以 a 或 d 开头')
                        flag = 1
                        continue
                    self.format_course_time((ii[1:-1], int(ii[-1])))
                except Exception as e:
                    infomation.append('修订参数"' + str(ii) + '"错误')
                    flag = 1
            if infomation != []:
                i.append('---->')
                wrong_data.append(str(i) + '  并且  '.join(infomation))
                        

        return (flag, wrong_data)

    def format_revised_data(self, revised):
        data = {}
        for i in revised:
            data[i[0]]=[[],[]]
        for i in revised:
            for ii in i[1:]:
                if ii[0] == 'a':
                    data[i[0]][0].append(self.format_course_time((ii[1:-1], int(ii[-1]))))
                elif ii[0] == 'd':
                    data[i[0]][1].append(self.format_course_time((ii[1:-1], int(ii[-1]))))
        print(data)
        return data
    def department_no_lesson_schedule(self, department, revised):
        flag, infomation = self.check_user_data(department, revised)
        if flag == 1:
            return (False, [], infomation)
        else:
            revised = self.format_revised_data(revised)
            schedules = [self.one_no_lesson_schedule(i, revised) for i in department]
            schedule = self.combine(schedules)
            return (True, schedule, infomation)

    def screen_data(self,
                    data,
                    four_class_a_day=True,
                    no_night=True,
                    no_weekend=False,
                    week_range=[1, -1]):
        def combine_odd(data):
            data = [data[i * 2: (i + 1) * 2]
                    for i in range(int(len(data) / 2))]
            data = [list(zip(i[0], i[1])) for i in data]
            data = [list(map(lambda x:'' if x[0] != x[1] else x[1],
                             i))
                    for i in data]
            return data

        assert len(week_range) == 2
        if four_class_a_day:
            no_night = True
        if week_range[-1] == -1:
            week_range[-1] = self.term_week_number

        data = data[week_range[0] - 1:week_range[-1]]

        if no_night:
            data = [i[:-3] for i in data]

        if four_class_a_day:
            data = [combine_odd(i) for i in data]

        if no_weekend:
            data = [list(map(lambda l:l[: -2], i)) for i in data]

        return data

    def storage_data(self, infomation, no_weekend, week_range, data, filename):
        if no_weekend:
            title = ['时间\\星期', '星期一', '星期二', '星期三', '星期四', '星期五']
        else:
            title = ['时间\\星期', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        ex = excel()
        if infomation != []:
            ex.add_a_sheet('提示！')
            ex.add_a_row(['数据来源为学校公开数据，老师没有及时提交的少量数据难以统计，数据仅供参考。'])
            ex.add_a_row(['请确认以下信息，如果无误请删除此sheet。如果有误请修改输入文件，并重新提交：'])
            for i in infomation:
                ex.add_a_row([i])
            ex.add_a_row([''])
            ex.add_a_row([''])
            ex.add_a_row([''])
        for e, i in enumerate(data):
            ex.add_a_sheet('第' + str(e + week_range[0]) + '周')
            ex.add_a_row(title)
            for ee, ii in enumerate(i):
                ii = ['\n'.join(iii) for iii in ii]
                ex.add_a_row(['第' + str(ee + 1) + '节'] + ii)
            ex.add_a_row([''])
            ex.add_a_row([''])
            ex.add_a_row([''])
        ex.save(filename)
