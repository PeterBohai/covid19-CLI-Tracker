import os
from datetime import datetime

import colorama
import pytz
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


class Style:
    RESET = "\033[0m"
    RED = "\033[31m"
    BLUE_D = "\033[34m"
    BLUE_L = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[33m"
    UNDERLINE = "\033[4m"
    BOLD = "\033[1m"


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
    country_rows = tbody.find_all("tr", {"style": ""})

    # Extract wanted data
    data_matrix = []
    for row in country_rows:
        name_td = row.find("td", {"style": "font-weight: bold; font-size:15px; text-align:left;"})
        name = ""
        if name_td:
            name_anchor = name_td.find("a")
            name = name_anchor.get_text() if name_anchor else name_td.find("span").get_text()

        if name in target_countries_list:
            data_cols = row.find_all("td")

            total_cases = Style.RED + data_cols[2].get_text().strip() + Style.RESET
            active_cases = Style.YELLOW + data_cols[8].get_text().strip() + Style.RESET
            total_deaths = Style.BLUE_D + data_cols[4].get_text().strip() + Style.RESET

            new_cases = data_cols[3].get_text().strip()
            new_deaths = data_cols[5].get_text().strip()

            data_matrix.append([name, total_cases, active_cases, new_cases, total_deaths, new_deaths])

    def strip_ansi(row):
        new_str = row[1].replace(",", "")
        num_start = -1
        num_end = -1

        for i, char in enumerate(new_str):
            if num_start != -1:
                if not char.isdigit():
                    num_end = i
                    break
            if char == "m":
                num_start = i + 1
        return int(new_str[num_start:num_end])

    data_matrix = sorted(data_matrix, key=strip_ansi, reverse=True)

    return data_matrix


def force_align(table_rows, row_index, colalign="center"):

    for row_num in row_index:
        split = table_rows[row_num].split("│")

        for i, header_str in enumerate(split):
            col_width = len(header_str)
            stripped_header = header_str.strip()

            if colalign == "left":
                split[i] = stripped_header.ljust(col_width)
            elif colalign == "right":
                split[i] = stripped_header.rjust(col_width)
            else:
                split[i] = stripped_header.center(col_width)

        table_rows[row_num] = "│".join(split)


def format_and_display_cli(data_table, center_headers=True):
    title_text = Style.UNDERLINE + "Coronavirus (COVID-19) Tracker for Countries of Interest" + Style.RESET

    now_utc = datetime.now(pytz.timezone("UTC"))
    now_local = datetime.now()
    date_text = Style.BOLD + now_local.strftime("%b %d, %Y") + Style.RESET
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
                             headers=["\nCountry", "Total\nCases", "Active\nCases", "New\nCases", "Total\nDeaths", "New\nDeaths"],
                             colalign=("left", "right", "right", "left", "right", "left"),
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
        force_align(table_rows, (1, 2))

    # Display data
    print()
    print()

    print(title_text.center(terminal_width + 6) + "\n")
    print(date_text.center(terminal_width + 6))
    print(time_text.center(terminal_width))
    print(gmt_text.center(terminal_width))

    for row in table_rows:
        print(left_whitespace_offset + row)

    print()
    print("Note".center(terminal_width))
    for line in note_text:
        print(left_whitespace_offset + line)

    print()


def make_valid(str_entry):
    varying_names = {"united states": "USA", "usa": "USA", "us": "USA", "america": "USA", "states": "USA",
                     "united kingdom": "UK", "u.k.": "UK", "uk": "UK", "britain": "UK", "great britain": "UK",
                     "south korea": "S. Korea",
                     "hk": "Hong Kong", "hong kong": "Hong Kong",
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
    # use Colorama to make colored font work on Windows
    colorama.init()

    default_countries = ["USA", "China", "Canada", "Thailand", "Taiwan", "Hong Kong"]
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
