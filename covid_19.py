import os
import datetime

from bs4 import BeautifulSoup
import pytz
import requests
from tabulate import tabulate


def in_terminal():
    try:
        os.get_terminal_size()
    except OSError:
        return False
    return True


def extract_data(target_countries_list):
    url = "https://www.worldometers.info/coronavirus/"
    source = requests.get(url).text

    soup = BeautifulSoup(source, "lxml")
    tbody = soup.find("tbody")
    country_row = tbody.find_all("tr")

    # Extract wanted data
    data_matrix = []
    for country in country_row:
        if country.find("td").get_text() in target_countries_list:
            data_cols = country.find_all("td")

            name = data_cols[0].get_text()
            cases = data_cols[1].get_text()
            deaths = data_cols[3].get_text()

            new_cases = data_cols[2].get_text()
            new_deaths = data_cols[4].get_text()

            data_matrix.append([name, cases, new_cases, deaths, new_deaths])

    data_matrix = sorted(data_matrix, key=lambda row: int(row[1].replace(",", "")), reverse=True)

    return data_matrix


def format_and_display_cli(data_table, center_headers=True):
    title_text = "Coronavirus (COVID-19) Tracker for Countries of Interest"

    now_utc = datetime.datetime.now(pytz.timezone("UTC"))
    now_local = datetime.datetime.now()
    date_text = now_local.strftime("%b %d, %Y")
    time_text = now_local.strftime("%A %I:%M %p")

    now_gmt = now_utc.astimezone(pytz.timezone("GMT"))
    gmt_text = "[" + now_gmt.strftime("%m-%d-%Y %I:%M %p %Z%z") + "]\n"

    # tabulate data to printable string
    if not data_table:
        term_width = 0
        if in_terminal():
            term_width = os.get_terminal_size().columns
        print("Please enter at least one valid country name.".center(term_width))
        return

    display_table = tabulate(data_table,
                             headers=["Country", "Cases", "New Cases", "Deaths", "New Deaths"],
                             colalign=("left", "right", "left", "right", "left"),
                             tablefmt="fancy_grid")
    table_rows = display_table.split("\n")
    table_width = len(table_rows[0])

    pad_left = 0
    terminal_width = 0

    if in_terminal():
        terminal_width = os.get_terminal_size().columns
        pad_left = int(terminal_width / 2 - table_width / 2)

    left_whitespace_offset = " " * pad_left
    note_text = ["  --> 'New' displays the live changes for the current day",
                 "      (reset after midnight GMT +0)",
                 "  --> Data acquired from www.worldometers.info/coronavirus/"]

    # format only headers to be centered, regardless of column alignment (not supported in tabulate)
    if center_headers:
        split_header = table_rows[1].split("│")

        for i, header_str in enumerate(split_header):
            width = len(header_str)
            stripped_header = header_str.strip()
            split_header[i] = stripped_header.center(width)

        table_rows[1] = "│".join(split_header)

    # Display data
    print()
    print()

    print(title_text.center(terminal_width) + "\n")
    print(date_text.center(terminal_width))
    print(time_text.center(terminal_width))
    print(gmt_text.center(terminal_width))

    for row in table_rows:
        print(row.center(terminal_width))

    print()
    print("Note".center(terminal_width))
    for line in note_text:
        print(left_whitespace_offset + line)

    print()


def make_valid(str_entry):
    varying_names = {"united states": "USA", "usa": "USA", "us": "USA", "america": "USA", "states": "USA",
                     "united kingdom": "UK", "u.k.": "UK", "uk": "UK", "britain": "UK", "great britain": "UK",
                     "south korea": "S. Korea",
                     "hk": "Hong Kong",
                     "uae": "UAE", "united arab emirates": "UAE", "emirates": "UAE",
                     "drc": "DRC", "dr congo": "DRC", "democratic republic of the congo": "DRC",
                     "car": "CAR", "central african republic": "CAR",
                     "guinea bissau": "Guinea-Bissau",
                     "timor leste": "Timor-Leste"}
    clean_str = str_entry.strip().lower()

    if clean_str in varying_names:
        return varying_names[clean_str]

    return clean_str.capitalize()


if __name__ == "__main__":
    default_countries = ["USA", "China", "Italy", "Canada", "Thailand", "Taiwan"]
    countries_of_interest = []

    width = 0
    if in_terminal():
        width = os.get_terminal_size().columns

    print("Display default countries? (yes = ENTER)".center(width))
    print(f"{default_countries}".center(width))
    user_input_default = input(" " * (width // 2))

    if not user_input_default.strip() or user_input_default.strip().lower() == "yes":
        countries_of_interest = default_countries
    else:
        print()
        print("Please specify countries of interest".center(width))
        user_input = input("[separate by commas] [Enter blank for default]\n".center(width))
        countries_of_interest = list(map(make_valid, user_input.split(",")))

        while not countries_of_interest:
            user_input = input("No countries specified, please try again: ")
            countries_of_interest = list(map(make_valid, user_input.split(",")))

    covid19_table = extract_data(countries_of_interest)
    format_and_display_cli(covid19_table)



