from pitchoune.dataset import Dataset
from chocolatine import SqlType


def test_dataset():
    ds = Dataset(
        name="people",
        data=(
            ("first_name", "last_name", "gender", "age", "city"),
            ("jean", "dupond", "male", "22", "paris"),
            ("jeanne", "bertrand", "female", "25", "bordeaux")
        ),
        schema=(
            SqlType.String,
            SqlType.String,
            SqlType.String,
            SqlType.Integer,
            SqlType.String,
        )
    )