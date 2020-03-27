# Coronavirus (COVID-19) CLI Tracker

## Overview
This CLI tracker of the Coronavirus (COVID-19) for specific countries of interest.
Information for each country include: total cases, total deaths, new cases, new deaths.
All the COVID-19 data displayed are extracted from [Worldometers](https://www.worldometers.info/coronavirus/)

The CLI is a Python script utilizing the following external libraries:

* beautifulsoup4
* requests
* tabulate
* pytz

**Note** on Beautiful Soup and using the best parser:

* lxml's HTML parser ("lxml")
	- need to install parser using pip or other setup commands
	- very fast
* Python's html.parser ("html.parser")
	- do not need to install any dependencies
	- not as fast

To change the parser, simply change the second string argument in the initialization of the BeautifulSoup object. For more details concerning installation of parsers (as well as their differences), please refer to the [official reference](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser).

### Screenshots
<p align="center">
	<img src="screenshots/screenshot-1.png" width=400>
</p>