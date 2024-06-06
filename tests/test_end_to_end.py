# Load titanic.csv and create a temporary table for it

from pitchoune.dataset import Dataset
from pitchoune.decorators import inject_params, load, save


@load("people", source="data/people.csv", schema=(str, str, int, str))
@load("cities", source="data/cities.csv", schema=(str, str))
# @save("people_cities")
@inject_params
def merge_people_and_cities(people: Dataset, cities: Dataset) -> Dataset:
    return None
    # return people.merge(cities, on="city")
