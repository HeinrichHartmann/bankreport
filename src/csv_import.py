"""
Read csv files from online banking
"""

import sys
import re
import io
import click
import pandas as pd

COLS = "Account Date Text Value".split()

SILENT = False


HTML_HEAD = """
<script src="https://code.jquery.com/jquery-1.7.1.min.js"></script>

<script>
$(document).ready(function(){
  var $rows = $('table tbody tr');
  $('#filter').keyup(function() {
    var val = $.trim($(this).val()).replace(/ +/g, ' ').toLowerCase();
    $rows.show().filter(function() {
      var text = $(this).text().replace(/\s+/g, ' ').toLowerCase();
      return !~text.indexOf(val);
    }).hide();
  });
});
</script>

<style>
  table {
      width: 100%;
      text-align: left;
      border-collapse: collapse;
  }
  table td, table th {
      border: 1px solid #000000;
      padding: 5px 4px;
  }
  table tbody td {
      font-size: 13px;
  }
  table thead {
      background: #CFCFCF;
      background: -moz-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      background: -webkit-linear-gradient(top, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      background: linear-gradient(to bottom, #dbdbdb 0%, #d3d3d3 66%, #CFCFCF 100%);
      border-bottom: 2px solid #000000;
  }
  table thead th {
      font-size: 15px;
      font-weight: bold;
      color: #000000;
      text-align: left;
  }

  #filter {
  width: 100%;
  }

</style>
<input type="search" id="filter" placeholder="Filter" autofocus="autofocus">
"""

HTML_THEAD = """
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th style="width:60px">Account</th>
      <th style="width:80px">Date</th>
      <th>Text</th>
      <th style="width:100px">Value</th>
    </tr>
  </thead>
"""


def eprint(*args):
    if not SILENT:
        print(*args, file=sys.stderr)


def rstrip(s, suffix):
    if s.endswith(suffix):
        return s[: -len(suffix)]


def read_comdirekt_sections(path):
    "Parse comdirekt csv and return section iterator"
    with open(path, "rb") as fh:
        RE_SECTION = re.compile(br"\r\n\r\n[\r\n]*")
        fbytes = fh.read()
        fbytes = fbytes.lstrip(b";\r\n")
        sections = RE_SECTION.split(fbytes)
        print(sections[0])
        print(sections[2])
        i = 0
        while i < len(sections):
            section = sections[i]
            m_head = re.match(br".*Ums\xE4tze ([^ ;]*)", section)
            if m_head:
                head = m_head.group(1)
                content = sections[i + 1]
                yield (head.decode("iso-8859-1"), content.decode("iso-8859-1"))
                i += 2
            else:
                i += 1


def import_comdirekt_csv(path):
    prefix = path.split("/")[-1].split("_")[0]
    df_out = pd.DataFrame(columns=COLS)
    for head, content in read_comdirekt_sections(path):
        eprint(f"HEAD '{head}'\n")
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
        elif head == "Visa-Karte":
            df = pd.read_csv(
                io.StringIO(content),
                delimiter=";",
                index_col=None,
                thousands=".",
                decimal=",",
                usecols=[0, 2, 4, 5],
                names="Date Vorgang Buchungstext Value".split(),
                skiprows=1,
                dtype={"Date": str},
            )
            df["Date"] = pd.to_datetime(df["Date"], format="%d.%m.%Y")
            df["Text"] = df["Vorgang"] + " -" + df["Buchungstext"]
            df["Account"] = prefix + "/visa"
            df_out = df_out.append(df[COLS])
        elif head == "Depot":
            # Not importing Depot data, yet
            pass
        else:
            eprint("Skipped", head, content)
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
@click.option("-f", "--format", "fmt", default="txt")
@click.option("--dedup/--no-dedup", default=False)
@click.option("--sort/--no-sort", default=False)
@click.option("-x", "--exclude", multiple=True)
@click.option("--silent/--no-silent", default=False)
def main(src, fmt, dedup, sort, exclude, silent):
    global SILENT
    SILENT = silent
    df = pd.DataFrame(columns=COLS)
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
        cols = "Date Text Value".split()
        eprint("dedup")
        df2 = df.drop_duplicates(subset=cols)
        eprint("Dedup (dropped {})".format(len(df) - len(df2)))
        eprint(df[~df.isin(df2).all(1)])
        df = df2
    if sort:
        df.sort_values(by=sort.split(","), inplace=True)
        df = df.reset_index(drop=True)

    for s in exclude:
        df = df[~df["Text"].str.contains(s)]

    if fmt == "txt":
        print(df.to_string())
    elif fmt == "csv":
        df.to_csv(sys.stdout, index=False)
    elif fmt == "pkl":
        df.to_pickle("/dev/stdout")
    elif fmt == "html":
        with pd.option_context("display.max_colwidth", -1):
            body = df.to_html()
            body = re.sub("<thead>.*</thead>", HTML_THEAD, body, flags=re.DOTALL)
            print(HTML_HEAD)
            print(body)
    else:
        raise Exception(f"Unknown format {fmt}")


if __name__ == "__main__":
    main()
