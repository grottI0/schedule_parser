import re

import pandas
from numpy import nan

from data import subjects, letters_en_to_ru


class Element:

    def __init__(self, day: str, number: int, even: bool, subject: str, duration: str,
                 auditory: str, teacher: str, t: str, group: str):
        self.day = day
        self.number = number
        self.even = even
        self.subject = subject
        self.duration = duration
        self.auditory = auditory
        self.teacher = teacher
        self.type = t
        self.group = group

    def __eq__(self, other):
        return self.day == other.day and self.number == self.number and self.subject and self.even == other.even


class Column:

    def __init__(self, name: str):
        self.name = name
        self.elements = list()

    def add_element(self, day, number, even: bool, subject, auditory, teacher, t, group, duration):
        self.elements.append(Element(day, number, even, subject, duration, auditory, teacher, t, group))


class ResultTable:

    def __init__(self):
        self.columns = list()

    def add_column(self, name: str):
        self.columns.append(Column(name))

    @staticmethod
    def get_subject(s: str):
        subject = re.search(r'[\w\n\s]{0,56}', s)[0].replace('\n', '')
        return subject

    @staticmethod
    def get_duration(s: str):
        duration = re.search(r'\([\w\s\-.]{0,15}\)', s)[0]
        return duration

    def __contains__(self, item: str):
        for column in self.columns:
            if column.name == item:
                return True
        return False

    def __getitem__(self, item: str):
        res = list()
        for column in self.columns:
            if column.name == item:
                res.append(column)
        return res

    def insert_element(self, e: Element):
        if e.subject in self:
            for i in range(len(self[e.subject])):
                exist = False
                for element in self.columns[i]:
                    if e == element:
                        exist = True
                        break
                if not exist:
                    self[e.subject][i].add_element(e)
                else:
                    self.add_column(e.subject)
                    self[e.subject][-1].add_element(e)

    def parse_group_schedule(self, table: pandas.DataFrame, group):
        _ = None
        for row in table.iterrows():
            r = row[1]
            if r.iloc[0] is not nan:
                _ = r.iloc[0]

            subject = self.get_subject(r.iloc[6])

            if subject in subjects:
                duration = self.get_duration(r.iloc[6])
                e_odd = Element(day=_, number=r.iloc[1],
                                auditory=r.iloc[3], t=r.iloc[4],
                                teacher=r.iloc[5], subject=subject,
                                even=False, duration=duration, group=group)
                self.insert_element(e_odd)

            subject = self.get_subject(r.iloc[7])
            if subject in subjects:
                duration = self.get_duration(r.iloc[7])
                e_even = Element(day=_, number=r.iloc[1],
                                 auditory=r.iloc[10], t=r.iloc[9],
                                 teacher=r.iloc[8], subject=subject,
                                 even=True, duration=duration, group=group)
                self.insert_element(e_even)


class StudentGroupSchedule:

    def __init__(self, csv_path: str):

        group = csv_path.split('/')[-1].split('.')[0]
        self.group = ''

        for i in range(len(group)):
            if group[i] in letters_en_to_ru:
                self.group += letters_en_to_ru[group[i]]
            else:
                self.group += group[i]

        self.df = pandas.read_csv(csv_path)
        self.df.dropna(how='all', axis=0, inplace=True)
