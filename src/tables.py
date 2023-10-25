import pandas

from data import employers, subjects

class Element:

    def __init__(self, day: str, number: int, even: bool, text: str):
        self.day = day
        self.number = number
        self.even = even
        self.text = text


class Column:

    def __init__(self, name: str):
        self.name = name
        self.elements = list()

    def add_element(self, day, number, even: bool, text: str):
        self.elements.append(Element(day, number, even, text))


class ResultTable:

    def __init__(self):
        self.columns = list()

    def add_column(self, name: str):
        self.columns.append(Column(name))

    def parse_group_schedule(self, table: pandas.DataFrame):

        for row in table.iterrows():
            ...


class StudentGroupSchedule:

    def __init__(self, path: str):

        df = pandas.read_csv(path)

        df.dropna(how='all', axis=1, inplace=True)
        print(df)
