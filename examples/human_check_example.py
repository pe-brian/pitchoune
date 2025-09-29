import os
from pitchoune.decorators import input_df, output


with open("not_checked.csv", "w") as file:
    file.write("a;b\n1;2\n3;4\n5;6\n7;8\n9;10\n11;12\n13;14\n15;16\n17;18\n19;20\n21;22\n23;24\n25;26\n27;28\n29;30")


@input_df("not_checked.csv")
@output(".xlsx", human_check=True)
def main(df):
    return df


if __name__ == "__main__":
    main()
    os.remove("not_checked.csv")
 