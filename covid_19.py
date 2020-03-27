import os
import datetime

from bs4 import BeautifulSoup
import pytz
import requests
from tabulate import tabulate


def extract_and_tabulate(target_countries_list):
    url = "https://www.worldometers.info/coronavirus/"
    source = requests.get(url).text

    soup = BeautifulSoup(source, "lxml")
    tbody = soup.find("tbody")
    country_row = tbody.find_all("tr")

    # Extract wanted data
    display_text = []
    for country in country_row:
        if country.find("td").get_text() in target_countries_list:
            data_cols = country.find_all("td")

            name = data_cols[0].get_text()
            cases = data_cols[1].get_text()
            deaths = data_cols[3].get_text()

            new_cases = data_cols[2].get_text()
            new_deaths = data_cols[4].get_text()

            display_text.append([name, cases, new_cases, deaths, new_deaths])

    display_text = sorted(display_text, key=lambda row: int(row[1].replace(",", "")), reverse=True)
    table = tabulate(display_text,
                     headers=["Country", "Cases", "New Cases", "Deaths", "New Deaths"],
                     colalign=("left", "right", "left", "right", "left"),
                     tablefmt="fancy_grid")
    return table


def format_and_display(data_table, center_headers=True):
    title_text = "Coronavirus (COVID-19) Tracker for Countries of Interest"

    now_local = datetime.datetime.now()
    date_text = now_local.strftime("%b %d, %Y")
    time_text = now_local.strftime("%A %I:%M %p")

    now_utc = now_local.astimezone(pytz.utc)
    now_gmt = now_utc.astimezone(pytz.timezone("GMT"))
    gmt_text = "[" + now_gmt.strftime("%m-%d-%Y %I:%M %p %Z%z") + "]\n"

    table_rows = data_table.split("\n")
    table_width = len(table_rows[0])

    # format only headers to be centered, regardless of column alignment (not supported in tabulate)
    if center_headers:
        split_header = table_rows[1].split("│")
        for i, header_str in enumerate(split_header):
            width = len(header_str)
            stripped_header = header_str.strip()
            split_header[i] = stripped_header.center(width)
        table_rows[1] = "│".join(split_header)

    try:
        terminal_width = os.get_terminal_size().columns
        pad_left = int(terminal_width / 2 - table_width / 2)
    except OSError:
        pad_left = 0
        terminal_width = 0

    left_whitespace_offset = " " * pad_left
    note_text = ["  --> 'New' displays the live changes for the current day",
                 "      (reset after midnight GMT +0)",
                 "  --> Data acquired from www.worldometers.info/coronavirus/"]

    # Display data
    print()

    print(title_text.center(terminal_width) + "\n")
    print(date_text.center(terminal_width))
    print(time_text.center(terminal_width))
    print(gmt_text.center(terminal_width))

    for row in table_rows:
        print(left_whitespace_offset + row)

    print()
    print(left_whitespace_offset + "Note:")
    for line in note_text:
        print(left_whitespace_offset + line)

    print()


countries_of_interest = ["USA", "China", "Italy", "Canada", "Thailand", "Taiwan"]
covid19_table = extract_and_tabulate(countries_of_interest)
format_and_display(covid19_table)



