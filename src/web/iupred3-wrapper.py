#!/usr/bin/env python

import argparse
import pathlib
import random
import re
import sys

import Bio.SeqIO.FastaIO
import grequests
import requests

# Keep script name in global constant
SCRIPT_NAME = pathlib.Path(__file__).name

BASE_URL: str = "https://iupred3.elte.hu"
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

def parse_args() -> argparse.Namespace:
    """Returns a namespace with parsed command-line arguments."""
    parser = argparse.ArgumentParser()
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
    return parser.parse_args()


def get_random_agent() -> str:
    """Returns a random user agnet string."""
    return random.choice(USER_AGENT_LIST)


def main(args) -> int:
    file = pathlib.Path(args.file)

    # Check if input file exists and return with non-zero exit stats if not.
    if not file.exists():
        print(f"{SCRIPT_NAME}: error: [Errno 2]: No such file or directory {file}")
        return 1

    cookies = {"csrftoken": args.token, "sessionid": args.sessionid}

    header = {"Accept": "application/xml", "Connection": "keep-alive", "User-Agent": get_random_agent()}

    data = {
        "email": "",
        "accession": "",
        "inp_seq": "",
        "aln_file": "",
        "csrfmiddlewaretoken": args.token,
    }

    with requests.Session() as session:
        session.headers.update(header)
        rs = []
        with open(file, "r") as f:
            for record in Bio.SeqIO.FastaIO.SimpleFastaParser(f):
                data["inp_seq"] = record[1]
                rs.append(
                    grequests.post(
                        f"{BASE_URL}/plot",
                        data=data,
                        cookies=cookies,
                        headers=header,
                        session=session,
                    )
                )

        responses = grequests.map(rs)
        json_id_re = re.compile(r'raw_json(%[A-Z0-9]+)"')
        rs2 = []
        for r in responses:
            line = [line for line in r.text.split("\n") if "raw_json" in line][
                0
            ].strip()
            match = json_id_re.search(line)
            if match is not None:
                rs2.append(
                    grequests.get(
                        f"{BASE_URL}/raw_json{match[1]}",
                        headers=header,
                        session=session,
                    )
                )

        responses2 = grequests.map(rs2)

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


if __name__ == "__main__":
    sys.exit(main(parse_args()))
