# iupred3-wrapper

This repository contains simple wrapper script for iupred3 web interface.

One needs to supply it with a csrf token and sessionid values from cookie file generated when visiting (iupred3)[https://iupred3.elte.hu/]. Those values can be found by using Developer Tools in Browser.

## Firefox

In Firefox to use Developer Tools, press `F12`. Then go to `Storage Tab` (you may need to press `>>` icon) and select `Cookies`. The relevant value should be there. Example values are provided in `cookies` file in this repo.
