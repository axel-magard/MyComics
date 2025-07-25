# MyComics
A viewer for favorite comics from gocomics.com

## Features
Initially displays all comics for current day. Allow to navigate back day by day or select a date from a date picker.

## How to install
1. Install Python ( if not installed already )
2. Run install.cmd ( on Windows ) or manually install necessary python modules:
```
pip install bs4
pip install requests
pip install comics
pip install flask==3.1.0
```

3. Clone code from git: 
`git clone git@github.com:axel-magard/MyComics.git`

4. Edit file comics.lst and specify your favortite comics from gocomics.com

## How to Run
Use run_f.cmd to start, or type
`flask --app MyComics_f.py run --debug`

A demo version can be seen [here](https://axmagard.eu.pythonanywhere.com/) on pythonanywhere.


