# iupred3-wrapper

This repository contains simple wrapper script for iupred3 web interface.

One no longer needs to supply it with a `csrftoken` and `sessionid` values from cookie file generated when visiting [iupred3](https://iupred3.elte.hu/). Script now manages to get those values from Firefox cookies database file. To do so, default locations of firefox's `profile directory` are checked for `databse.sqlite` file. If those do not work, user can supply custom cookies file location via `--firefox-cookies-path` argument.

Locations checked for `database.sqlite` file:
 - `$HOME/snap/firefox/common/.mozilla/firefox/*.default`,
 - `$HOME/.mozilla/firefox/*.default`,

Only cookies saved by the Firefox browser can be used. Other browsers are not supported.

## Firefox

`csrftoken` and `sessionid` can still be supplied manually. Those values can be found by using Developer Tools in Browser.
In Firefox to use Developer Tools, press `F12`. Then go to `Storage` Tab (you may need to press `>>` icon) and select `Cookies`. The relevant value should be there. Example values are provided in `cookie` file in this repo.
