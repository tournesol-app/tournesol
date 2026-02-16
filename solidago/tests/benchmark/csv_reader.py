import csv

from solidago.primitives.timer import time


def load_csv():
    rows = list()
    with time("Load csv"):
        with open("tests/comparisons.csv") as csvfile:
            reader = csv.reader(csvfile)
            column_names = next(reader)
            for row in reader:
                rows.append(row)
    return column_names, rows

def load_no_csv():
    rows = list()
    with time("Load csv"):
        with open("tests/comparisons.csv") as csvfile:
            line = csvfile.readline()
            column_names = line.split(",")
            line = csvfile.readline()
            while line is not None:
                rows.append(line)
                line = csvfile.readline()
    return column_names, rows

def load_csv_dict():
    rows = list()
    with time("Load csv"):
        with open("tests/comparisons.csv") as csvfile:
            d = csv.DictReader(csvfile)
    return d

def load_pandas():
    import pandas as pd
    with time("Load csv"):
        return pd.read_csv("tests/comparisons.csv")
    

if __name__ == "__main__":
    load_csv()
    load_csv_dict()
    load_no_csv()