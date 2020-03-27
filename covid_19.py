import os
from bs4 import BeautifulSoup
import requests
from tabulate import tabulate
import datetime
import pytz

url = "https://www.worldometers.info/coronavirus/"
source = requests.get(url).text

soup = BeautifulSoup(source, "lxml")
tbody = soup.find("tbody")
country_row = tbody.find_all("tr")

countries_to_watch = ["China", "Italy", "USA", "Canada", "Thailand", "Taiwan"]

# Create table
display_text = []
for country in country_row:
    if country.find("td").get_text() in countries_to_watch:
        data_cols = country.find_all("td")
        name = data_cols[0].get_text()
        cases = data_cols[1].get_text()
        deaths = data_cols[3].get_text()

        new_cases = data_cols[2].get_text()
        new_deaths = data_cols[4].get_text()

        display_text.append([name, cases, new_cases, deaths, new_deaths])
table = tabulate(display_text,
                 headers=["Country", "Cases", "New Cases", "Deaths", "New Deaths"],
                 colalign=("left", "right", "left", "right", "left"),
                 tablefmt="fancy_grid")

# format display in terminal
title_text = "Coronavirus (COVID-19) Tracker for Specific Countries"
curr_time = datetime.datetime.now()
date_text = curr_time.strftime("%b %d, %Y")
time_text = curr_time.strftime("%A %I:%M %p")

curr_utc = curr_time.astimezone(pytz.utc)
curr_gmt = curr_utc.astimezone(pytz.timezone("GMT"))
gmt_text = "[" + curr_gmt.strftime("%m-%d-%Y %I:%M %p %Z%z") + "]\n"

table_rows = table.split("\n")
table_width = len(table_rows[0])
try:
    terminal_width = os.get_terminal_size().columns
    pad_left = int(terminal_width/2 - table_width/2)


except OSError:
    pad_left = 0
    terminal_width = 0

left_ws = " "*pad_left
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
    print(left_ws + row)

print()

print(left_ws + "Note:")
for line in note_text:
    print(left_ws + line)

print()



