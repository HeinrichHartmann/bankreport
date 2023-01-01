"""
Parse csv files from online banking
"""

import sys
import re
import io
import click
import pandas as pd

from . import templates

COLS = "Account Date Text Value".split()

VERBOSITY = 0


def eprint(*args):
    if VERBOSITY > 0:
        print(*args, file=sys.stderr)


def read_comdirekt_sections(path):
    "Parse comdirekt csv and return section iterator"
    #
    # ComDirekt CSV example:
    # ;
    # "Ums<E4>tze Girokonto";"Zeitraum: 01.01.2020 - 01.01.2021";
    #
    #
    # "Buchungstag";"Wertstellung (Valuta)";"Vorgang";"Buchungstext";"Umsatz in EUR";
    # ... lnes
    #
    #
    #
    # "Ums<E4>tze Depot";"Zeitraum: 01.01.2020 - 01.01.2021";
    #
    # "Buchungstag";"Gesch<E4>ftstag";"St<FC>ck / Nom.";"Bezeichnung";"WKN";"W<E4>hrung";"Ausf<FC>hrungskurs";"Umsatz in EUR";
    # ...
    with open(path, "rb") as fh:
        content = fh.read().decode("iso-8859-1").strip().replace("\r", "")
        # Strip ";\n" from beginning
        content = content.lstrip(";\n")

        # Remove "Kontostand rows"
        content = re.sub(
            "^.*Kontostand[^;]*;[^;]*;.*$", "", content, flags=re.MULTILINE
        )
        # Fix corrupted ? visa lines "12.07.2021";\n"neu";
        content = re.sub(r'("\d+.\d+.\d+");\n"neu"', r"\1", content, flags=re.MULTILINE)
        # Spit into sections based on headline:
        # "Ums<E4>tze Depot";"Zeitraum: 01.01.2020 - 01.01.2021";
        # Matching keywords "Ums.atze" and "Zeitraum" in a single line
        section_pos = [
            m.start() for m in re.finditer(r'^[" ]*Ums.*tze.*Zeitraum', content)
        ]
        section_pos.append(len(content))
        for i in range(len(section_pos) - 1):
            section = content[section_pos[i] : section_pos[i + 1]]
            m = re.match(
                r"\A(?P<head>.*?)\n\n(?P<body>.*)\Z",
                section,
                re.MULTILINE | re.DOTALL,
            )
            if m:
                h = re.match(r".*Ums.tze (?P<title>[a-zA-Z0-9]+).*", m.group("head"))
                if h:
                    title = h.group("title")
                    body = m.group("body")
                    yield (title, body.strip())
                else:
                    eprint(f"No title in section {section}")
            else:
                eprint(f"NO MATCH: {section}\n")


def import_comdirekt_csv(path):
    prefix = path.split("/")[-1].split("_")[0]
    df_out = pd.DataFrame(columns=COLS)
    for head, content in read_comdirekt_sections(path):
        if head == "Girokonto":
            df = pd.read_csv(
                io.StringIO(content),
                delimiter=";",
                index_col=None,
                thousands=".",
                decimal=",",
                usecols=[0, 2, 3, 4],
                names="Date Vorgang Buchungstext Value".split(),
                skiprows=1,
                dtype={"Date": str},
            )
            df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
            df["Text"] = df["Vorgang"] + " -" + df["Buchungstext"]
            df["Account"] = prefix + "/giro"
            df_out = df_out.append(df[COLS])
        elif head == "Tagesgeld":
            df = pd.read_csv(
                io.StringIO(content),
                delimiter=";",
                index_col=None,
                thousands=".",
                decimal=",",
                usecols=[0, 2, 3, 4],
                names="Date Vorgang Buchungstext Value".split(),
                skiprows=1,
                dtype={"Date": str},
            )
            df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
            df["Text"] = df["Vorgang"] + " -" + df["Buchungstext"]
            df["Account"] = prefix + "/tg"
            df_out = df_out.append(df[COLS])
        elif head.startswith("Visa"):
            df = pd.read_csv(
                io.StringIO(content),
                delimiter=";",
                index_col=None,
                thousands=".",
                decimal=",",
                usecols=[1, 2, 4, 5],
                names="Date Vorgang Buchungstext Value".split(),
                skiprows=1,
                dtype={"Date": str},
            )
            df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
            df["Text"] = df["Vorgang"] + " -" + df["Buchungstext"]
            df["Account"] = prefix + "/visa"
            df_out = df_out.append(df[COLS])
        elif head == "Depot":
            eprint("Skipping Depot data")
            pass
        else:
            eprint(f"Skipped section {head}\n\n{content}\n")
    return df_out.iloc[::-1]


def import_fidor_csv(path):
    prefix = path.split("/")[-1].split("_")[0]
    df = pd.read_csv(
        path,
        delimiter=";",
        index_col=None,
        thousands=".",
        decimal=",",
        names="Date,Text1,Text2,Value".split(","),
        skiprows=1,
        dtype={"Date": str},
    )
    df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
    df.fillna("", inplace=True)
    df["Text"] = df["Text1"] + " -" + df["Text2"]
    df["Account"] = prefix
    return df[COLS].iloc[::-1]


@click.command()
@click.argument("src", nargs=-1)
@click.option(
    "-f",
    "--format",
    "fmt",
    default="tsv",
    type=click.Choice(["tsv", "csv", "txt", "pkl", "html"], case_sensitive=False),
)
@click.option(
    "--dedup/--no-dedup", help="Deduplicate entries across csv files", default=True
)
@click.option(
    "--sort",
    help="Comma sepearated list of columns to sort the output by",
    default="Date",
)
@click.option(
    "-x",
    "--exclude",
    help="Exclude records containing the provided string in Text column",
    multiple=True,
)
@click.option(
    "--rules",
    help=r"File containing classification rules. Schema: <regex>\t<category>\n",
    default=None,
)
@click.option("-v", "--verbose", help="Print debug output to stderr", count=True)
def main(src, fmt, dedup, sort, exclude, verbose, rules):
    global VERBOSITY
    VERBOSITY = verbose

    if len(src) == 0:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    df: pd.DataFrame = pd.DataFrame(columns=COLS)
    for path in src:
        eprint("Importing " + path)
        if path.endswith("cd.csv"):
            df = df.append(
                import_comdirekt_csv(path),
            )
        elif path.endswith("ftx.csv"):
            df = df.append(import_fidor_csv(path))
        else:
            eprint("Skipping " + path)

    df = df[COLS].reset_index(drop=True)

    if dedup:
        df2 = df.drop_duplicates(subset="Date Text Value".split())
        eprint("Dedup (dropped {})".format(len(df) - len(df2)))
        eprint(df[~df.isin(df2).all(1)])
        df = df2

    if sort:
        df.sort_values(by=sort.split(","), inplace=True)
        df = df.reset_index(drop=True)

    for s in exclude:
        df = df[~df["Text"].str.contains(s)]

    df["Category"] = ""
    if rules:
        with open(rules, "rb") as fh:
            content = fh.read().decode("utf-8")
            rules = [l.split("\t") for l in content.splitlines() if "\t" in l]
            df["Category"] = ""
            for rx, cat in rules:
                df.loc[df.Text.str.contains(rx, regex=True), "Category"] = cat

    if fmt == "txt":
        print(df.to_string())
    elif fmt == "csv":
        df.to_csv(sys.stdout, index=False)
    elif fmt == "tsv":
        df.to_csv(sys.stdout, index=False, sep="\t")
    elif fmt == "pkl":
        df.to_pickle("/dev/stdout")
    elif fmt == "html":
        with pd.option_context("display.max_colwidth", -1):
            body = df.to_html()
            body = re.sub(
                pattern="<thead>.*</thead>",
                repl=templates.HTML_THEAD,
                string=body,
                flags=re.DOTALL,
            )
            print(templates.HTML_HEAD)
            print(body)
    else:
        raise Exception(f"Unknown format {fmt}")


if __name__ == "__main__":
    main()
