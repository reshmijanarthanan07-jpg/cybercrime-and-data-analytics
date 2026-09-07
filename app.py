from flask import Flask, render_template, request, redirect
from database import get_db_connection
import pandas as pd

app = Flask(__name__)


# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Add New Data
@app.route("/add", methods=["GET", "POST"])
def add_data():
    connection = get_db_connection()

    if request.method == "POST":
        crime_type = request.form["crime_type"]
        location = request.form["location"]
        year = request.form["year"]
        cases = request.form["cases"]

        cursor = connection.cursor()

        query = """
            INSERT INTO cybercrime
            (crime_type, location, year, cases)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (crime_type, location, year, cases)
        )

        connection.commit()
        cursor.close()
        connection.close()

        return redirect("/dashboard")

    connection.close()
    return render_template("add_data.html")


# Delete Data
@app.route("/delete/<int:id>")
def delete_data(id):
    connection = get_db_connection()

    cursor = connection.cursor()

    query = "DELETE FROM cybercrime WHERE id = %s"

    cursor.execute(query, (id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/dashboard")


# Edit Data
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_data(id):
    connection = get_db_connection()

    if request.method == "POST":
        crime_type = request.form["crime_type"]
        location = request.form["location"]
        year = request.form["year"]
        cases = request.form["cases"]

        cursor = connection.cursor()

        query = """
            UPDATE cybercrime
            SET crime_type = %s,
                location = %s,
                year = %s,
                cases = %s
            WHERE id = %s
        """

        cursor.execute(
            query,
            (crime_type, location, year, cases, id)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/dashboard")

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, crime_type, location, year, cases
        FROM cybercrime
        WHERE id = %s
        """,
        (id,)
    )

    record = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_data.html",
        record=record
    )


# Dashboard
@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    query = """
        SELECT crime_type, location, year, cases
        FROM cybercrime
    """

    df = pd.read_sql(query, connection)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, crime_type, location, year, cases
        FROM cybercrime
        """
    )

    records = cursor.fetchall()

    cursor.close()
    connection.close()


    # Summary
    total_cases = int(df["cases"].sum())

    total_crime_types = df["crime_type"].nunique()

    total_locations = df["location"].nunique()

    total_years = df["year"].nunique()


    # Crime Type Analysis
    crime_summary = (
        df.groupby("crime_type")["cases"]
        .sum()
        .sort_values(ascending=False)
    )


    # Location Analysis
    location_summary = (
        df.groupby("location")["cases"]
        .sum()
        .sort_values(ascending=False)
    )


    # Year Analysis
    year_summary = (
        df.groupby("year")["cases"]
        .sum()
        .sort_index()
    )


    # Analytics
    most_reported_crime = crime_summary.index[0]

    most_reported_crime_cases = int(
        crime_summary.iloc[0]
    )

    most_affected_location = location_summary.index[0]

    most_affected_location_cases = int(
        location_summary.iloc[0]
    )

    highest_crime_year = year_summary.idxmax()

    highest_crime_year_cases = int(
        year_summary.max()
    )


    return render_template(
        "dashboard.html",

        total_cases=total_cases,

        total_crime_types=total_crime_types,

        total_locations=total_locations,

        total_years=total_years,

        crime_labels=crime_summary.index.tolist(),

        crime_values=crime_summary.values.tolist(),

        location_labels=location_summary.index.tolist(),

        location_values=location_summary.values.tolist(),

        year_labels=year_summary.index.tolist(),

        year_values=year_summary.values.tolist(),

        records=records,

        most_reported_crime=most_reported_crime,

        most_reported_crime_cases=most_reported_crime_cases,

        most_affected_location=most_affected_location,

        most_affected_location_cases=most_affected_location_cases,

        highest_crime_year=highest_crime_year,

        highest_crime_year_cases=highest_crime_year_cases
    )


if __name__ == "__main__":
    app.run(debug=True)