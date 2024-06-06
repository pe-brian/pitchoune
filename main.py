# from pitchoune.functions import connect_to_db


# con = connect_to_db('user', 'password', '127.0.0.1', 'db')
# con.close()

from pitchoune.dataset import Dataset
from pitchoune.decorators import load, save


@load("raw_people", source="data/people.csv", schema=(str, str, int, str))
@save("people")
def load_and_clean_people(raw_people: Dataset) -> Dataset:
    print(raw_people, "loaded")
    print(raw_people._creation_query)
    return raw_people


@load("raw_cities", source="data/cities.csv", schema=(str, str, int, str))
@save("cities")
def load_and_clean_cities(raw_cities: Dataset) -> Dataset:
    print(raw_cities, "loaded")
    print(raw_cities._creation_query)
    return raw_cities


@load("people")
@load("cities")
@save("people_cities")
def merge_people_and_cities(people: Dataset, cities: Dataset) -> Dataset:
    print(people, "loaded")
    print(cities, "loaded")
    return people.merge(cities, on="city")


load_and_clean_people()
load_and_clean_cities()
merge_people_and_cities()
