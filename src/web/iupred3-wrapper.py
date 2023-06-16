#!/usr/bin/env python

import argparse
import os
import pathlib
import random
import re
import sys
import sqlite3
import shutil
import textwrap

import Bio.SeqIO.FastaIO
import grequests
import requests

# Keep script name in global constant
SCRIPT_NAME = pathlib.Path(__file__).name

BASE_URL: str = "https://iupred3.elte.hu"
FiREFOX_PROFILE_DIRS = [
    "~/snap/firefox/common/.mozilla/firefox/",
    "~/.mozilla/firefox/",
]
# User agent list for get_random_agent function.
USER_AGENT_LIST = [
    # Firefox
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0",
]


class CookiesUnavailibleError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    """Returns a namespace with parsed command-line arguments."""
    description = """A simple wrapper for iupred3 web interface. To use it csrf
                     tokan and sessionid are required. Those can be aquired from
                     cookie files saved by the browser after visiting the 
                     iupred3 website. Default values for those are supplied 
                     within the script but there is no gurantee of them working.
                     To use the script you should find the values of your own
                     keys."""
    parser = argparse.ArgumentParser(description=textwrap.dedent(description))
    parser.add_argument(
        "file", type=str, help="input file with protein sequence in fasta format"
    )
    parser.add_argument(
        "--token",
        type=str,
        default="C3rTEMDtjNTenW68kmmmea0WFv3mLrcCKmQKftdy8hRFF7sHZGPiEvAgx2zaaoB9",
        help="csrf token from cookie iupred3 cookie file. Needed to make requests.",
    )
    parser.add_argument(
        "--sessionid",
        type=str,
        default="x7w0cxzvzueyvhtu1ma9yt2nph81wt9y",
        help="sessionid from cookie iupred3 cookie file. Needed to make requests.",
    )
    parser.add_argument(
        "--firefox-cookies-path",
        type=str,
        help="a path to firefox cookies sqlite databse file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true", 
        help="print verbose output"
    )
    return parser.parse_args()


def get_random_agent() -> str:
    """Returns a random user agnet string from USER_AGENT_LIST constant."""
    return random.choice(USER_AGENT_LIST)


# raises FileNotFoundError
def get_db_file(firefox_profile_dirs: list[str]) -> pathlib.Path:
    for dir in firefox_profile_dirs:
        path = pathlib.Path(dir).expanduser()
        if path.exists():
            return next(path.expanduser().glob("*.default/cookies.sqlite"))
    raise FileNotFoundError(
        f"{SCRIPT_NAME}: error: Couldn't find the cookies database file."
    )


# raises FileNotFoundError.
def find_cookies_db(args: argparse.Namespace) -> pathlib.Path:
    """Tries to return a path to the sqlite cookies database."""
    if not args.firefox_cookies_path:
        return get_db_file(FiREFOX_PROFILE_DIRS)
    else:
        cookies_db = pathlib.Path(args.firefox_cookies_path)
        if not cookies_db.expanduser().exists():
            raise FileNotFoundError(
                f"{SCRIPT_NAME}: error: [Errno 2] No such file or directory {cookies_db}"
            )
        return cookies_db


# raises CookiesUnavailibleError
def get_values_from_cookies(db_file: pathlib.Path) -> dict[str, str]:
    TMP_DB_NAME = "cookies_tmp.sqlite"
    QUERY = "select name, value from moz_cookies where host = 'iupred3.elte.hu'"
    tmp_path = pathlib.Path(f"./{TMP_DB_NAME}")
    try:
        shutil.copy(db_file, tmp_path)
        connection = sqlite3.connect(tmp_path)
        cursor = connection.cursor()
        rows = cursor.execute(QUERY).fetchall()
        return {rows[0][0]: rows[0][1], rows[1][0]: rows[1][1]}
    except Exception as e:
        raise CookiesUnavailibleError from e
    finally:
        print("Cleaning up...")
        os.remove(tmp_path)


def main(args) -> int:
    file = pathlib.Path(args.file)

    # Check if input file exists and return with non-zero exit stats if not.
    if not file.exists():
        print(f"{SCRIPT_NAME}: error: [Errno 2]: No such file or directory {file}")
        return 1

    if not args.sessionid and not args.token:
        try:
            cookies_db = find_cookies_db(args)
        except FileNotFoundError as e:
            print(e)
            return 1

        try:
            cookies = get_values_from_cookies(cookies_db)
        except CookiesUnavailibleError as e:
            print(f"{SCRIPT_NAME}: error: Unable to read or parse cookies")
            if args.debug:
                print(e)
    else:
        # Set value for cookies fields. csrftoken and sessionid are needed for
        # verification of POST requests on iupred3 site to acess /plot endpoint.
        cookies = {"csrftoken": args.token, "sessionid": args.sessionid}

    # Set headers. `Accept:` does not seem to work.
    header = {
        "Accept": "application/json",
        "Connection": "keep-alive",
        "User-Agent": get_random_agent(),
    }

    # Data passed with POST request. I don't know if other fields need to be
    # an empty string, but I'm gonna leave them as such to be safe.
    data = {
        "email": "",
        "accession": "",
        "inp_seq": "",
        "aln_file": "",
        "csrfmiddlewaretoken": args.token,  # This also needs to be here for some reason.
    }

    # requests need to be within the same session to keep them alive. This is
    # necessary to acquire the jsons from the second series of requests.
    with requests.Session() as session:
        # Set header for the session.
        session.headers.update(header)
        rs = []
        # Read sequences from input file and create an asynchronous request for
        # each sequence. This script does not keep track of sequence identifiers.
        with open(file, "r") as f:
            for record in Bio.SeqIO.FastaIO.SimpleFastaParser(f):
                # Overwrite the `inp_seq` in data directory to pass it to request
                data["inp_seq"] = record[1]
                # Construct post request and append it to rs.
                rs.append(
                    grequests.post(
                        f"{BASE_URL}/plot",
                        data=data,
                        cookies=cookies,
                        headers=header,
                        session=session,
                    )
                )

        # Make requests from rs asynchronously and collect response objects.
        responses = grequests.map(rs)

        # Regular expression used to find id of json file, generated for request.
        json_id_re = re.compile(r'raw_json(%[A-Z0-9]+)"')

        rs2 = []
        # For each response create new request that will retrieve json file with
        # the results. This needs to be one because json is not returned normally
        # by iupred3 web service.
        for r in responses:
            # get id for raw_json endpoint.
            line = [line for line in r.text.split("\n") if "raw_json" in line][
                0
            ].strip()
            match = json_id_re.search(line)
            if match is not None:
                # Create get requests and append them to rs2.
                rs2.append(
                    grequests.get(
                        f"{BASE_URL}/raw_json{match[1]}",
                        headers=header,
                        session=session,
                    )
                )

        # Make requests from rs2 asynchronously.
        responses2 = grequests.map(rs2)

    # For each response retrieve the resulting values, and construct the
    # string representing the disordered domains, then print it.
    for r in responses2:
        data = r.json()
        disordered = ""
        for d in data["iupred2"]:
            if d > 0.5:
                disordered += "D"
            else:
                disordered += "-"
        print(data["sequence"])
        print(disordered)

    return 0


# Only run main if this module is executed as a top level module.
if __name__ == "__main__":
    sys.exit(main(parse_args()))
