from pitchoune.functions import load_csv, load


def test_load_csv():
    assert load_csv("data/people.csv") == (
        ("first_name", "last_name", "gender", "age", "city"),
        ("jean", "dupond", "male", "22", "paris"),
        ("jeanne", "bertrand", "female", "25", "bordeaux")
    )


def test_load():
    assert load("data/people.csv") == (
        ("first_name", "last_name", "gender", "age", "city"),
        ("jean", "dupond", "male", "22", "paris"),
        ("jeanne", "bertrand", "female", "25", "bordeaux")
    )
