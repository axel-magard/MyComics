# MyComics
A viewer for favorite comics from [gocomics.com](https://www.gocomics.com/)

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

A demo version can be seen [here](https://axmagard.eu.pythonanywhere.com/demo) on pythonanywhere.

The "Options" page ( reachable thru button with gear icon ) allows to
* pick favorite comics from comics available
* randomly display a comic from comics available

Favorite comics will be shown in listbox on main page.
Comics to be display can be selected or de-selected from that list of favorites.

The "Use RSS" checkbox allows to chose whether to use [PyPI Comics API](https://pypi.org/project/comics/) or the
RSS feed from [gocomics.com](https://www.gocomics.com/).

RSS feed is much faster but only supports access to entries from last ~100 days.


