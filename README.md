 # bankreport

## Installation

* Via pip: `pip install bankreport`
* From  local git checkout: `make install`

## Usage

```
Usage: bankreport [OPTIONS] [SRC]...

Options:
  -f, --format [tsv|csv|txt|pkl|html]
  --dedup / --no-dedup            Deduplicate entries
  --sort TEXT                     Comma sepearated list of fields to sort the output by
  -x, --exclude TEXT              Exclude records containing the provided string
  --rules TEXT                    File containing classification rules
                                  Schema: <regex>\t<category>

  -v, --verbose                   Debug output
  --help                          Show this message and exit
```

## Output Columns

1. Account -- E.g. comdirekt/giro; comdiekt/visa
2. Date -- isoformatted date 
3. Text -- "Buchungstext"
4. Value -- Value of transactions (typically in EUR)
5. Category -- Inferred category from rules file 

## Example Usage

1. Download various csv files from ComDirekt online-banking into ./csv
2. Rename ComDirekt CSV files to have extension .cd.csv
3. Run bankreport as:
   - `bankreport ./csv/*` to write a well-defined unified tsv file to stdout
   - `bankreport -f html ./csv/* > out.html & open out.html` to view HTML formatted table
   - `bankreport ./csv/* --rules rules.tsv | q -t -H -O 'select Category, sum(Value) from - group by Category'` to show category totals
     (using [q(1)](http://harelba.github.io/q/)).

## Supported Banking Formats

Banking formats are inferred from the file extension, as to allow mixed files in
a single directory. Unfortunately, the supported banks do not use consistent
file extensions by themselves, so the files have to be manually renamed
to have the correct extension.

| Bank      | Date       | Extension |
|-----------|------------|-----------|
| ComDirekt | 2020-12-22 | .cd.csv   |
| Fidor     | 2019-12    | .fd.csv   |
