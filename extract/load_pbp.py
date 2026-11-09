# load_pbp.py: pulls nflverse data and loads it into DuckDB's raw layer

from pathlib import Path          # Path handles file paths the same way on Windows and Linux
import duckdb                     # the DuckDB Python client
import nflreadpy as nfl       # the nflverse Python client

# Build the DB path relative to THIS file, so the script works no matter where you run it from
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # extract/load_pbp.py -> extract/ -> project root
DB_PATH = PROJECT_ROOT / "data" / "nfl.duckdb"          # the / operator joins path pieces together

def main():
    con = duckdb.connect(str(DB_PATH))                   # open (or create) the database file
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")       # make sure the raw schema exists

    pbp = nfl.load_pbp([2025])                                   # pull ONE season of play-by-play as a Polars DataFrame
    print(f"Pulled {pbp.height:,} rows x {pbp.width} columns")  # height = rows, width = columns; :, adds comma separators

    con.execute("CREATE OR REPLACE TABLE raw.pbp AS SELECT * FROM pbp")  # copy the DataFrame into a DuckDB table

    row_count = con.execute("SELECT count(*) FROM raw.pbp").fetchone()[0]     # count rows that landed in the table
    print(f"raw.pbp now has {row_count:,} rows")         # should match the pulled row count

    con.close()                                                                          # release the file lock when done

if __name__ == "__main__":        # only run main() when the file is run directly, not when it's imported
    main()