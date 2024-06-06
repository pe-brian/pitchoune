# Pitchoune

![Image](logo.jpg)

Pitchoune is data transformation Python library


# Functionnalities

* Create table from CSV :
    ```python
    table = Table.load_from_csv(
            path="data/titanic.csv",
            value_types=[
                Integer(),
                Integer(),
                Integer(),
                String(),
                String(),
                Integer(),
                Integer(),
                Integer(),
                String(),
                Float(),
                String(),
                String()
            ]
        )
    ```

* Get table schema :

    ```python
    schema = table.schema
    ```


* Select columns :

    ```python
    table = table.select("Pclass", "Name", "Sex", "Age")
    ```

* Filter rows :

    ```python
    table = table.filter(lambda x: x["Survived"] == 0 and x["Sex"] == "male" and x["Age"] is not None)
    ```

* Displaying table :

    
    ```python
    print(table)
    ```

* Create custom table :

    ```python
    indexes = [1, 2, 3, 4, 5]
    names = ["jean", "pierre", "georges", "franck", "isabelle"]
    ages = [19, 24, 18, 23, 20]

    table = Table(Column("Id", Integer(), indexes), Column("Name", String(), names), Column("Age", Integer(), ages)])
    ```

* Add column :

    ```python
    sex = ["M", "M", "M", "M", "F"]
    table.addColumn(Column("sex", String, sex))
    ```
    or :
    ```python
    table.createColumn("sex", String, sex)
    ```
    conditionally :
    ```python
    table.createColumn("US_legalAge", Boolean, lambda row: row["Age"] >= 21)
    ```
* Drop column :

    ```python
    ```

* Rename column :

    ```python
    ```

* Perform a union between two tables :

    ```python
    other_table = Table(
        Column("Index", Integer(), [45, 25, 65]),
        Column("Name", String(), ["marie", "céline", "antoine"]),
        Column("Age", String(), [18, 25, 42]),
        Column("US_legalAge", Boolean(), lambda row: row["Age"] >= 21)
    )

    table = table.union(other_table)
    ```

* Perform an aggregation :

    ```python
   count_table = table.groupBy("Sex", "US_legalAge").count()
   unique_count_table = table.groupBy("Sex", "US_legalAge").unique_count()
   mean_table = table.groupBy("Sex", "US_legalAge").mean()
    ```

* Get more control over aggregation :

    ```python
   count_table = table.groupBy("Sex", "US_legalAge").aggregate(Aggregation("Name", "collect"))
    ```

* Join two tables :

    ```python
   result_table = table.join(other_table, "left", lambda a, b: a["Index"] == b["Index"])
    ```
