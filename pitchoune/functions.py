from typing import Iterable, Union
import mysql.connector
from mysql.connector import errorcode
from chocolatine import SqlType


def translate_schema(schema: Iterable[Union[str, int, float, bool] | SqlType]):
    """"""
    res = []
    for t in schema:
        match t.__name__:
            case "int":
                t = SqlType.Integer
            case "float":
                t = SqlType.Float
            case "str":
                t = SqlType.String
        res.append(t)
    return res


def load_csv(source: str):
    """"""
    import csv
    with open(source, newline="", encoding="utf8") as file:
        return tuple(tuple(row) for row in csv.reader(file, delimiter=";", quotechar='"'))


def load_file(source: str):
    """"""
    match source.split(".")[-1]:
        case "csv":
            return load_csv(source)
        

def persist(dataset):
    """"""
    print(f"{dataset} saved")


def connect_to_db(user: str, password: str, host: str, db: str):
    try:
        con = mysql.connector.connect(user=user, password=password, host=host, database=db)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return con


def exec_sql(query: str) -> str:
    """"""
    pass