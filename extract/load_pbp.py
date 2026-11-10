# load_pbp.py: pulls nflverse data and loads it into DuckDB's raw layer

from pathlib import Path          # Path handles file paths the same way on Windows and Linux
import duckdb                     # the DuckDB Python client
import nflreadpy as nfl       # the nflverse Python client
import sys                        # lets the script read what you type in the terminal

# Build the DB path relative to THIS file, so the script works no matter where you run it from
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # extract/load_pbp.py -> extract/ -> project root
DB_PATH = PROJECT_ROOT / "data" / "nfl.duckdb"          # the / operator joins path pieces together

SEASONS = list(range(2018, 2027))     # every season to load; range's end number is EXCLUDED

def load_season(con, season):
    """Download one season and replace that seasons rows it to raw.pbp."""
    pbp = nfl.load_pbp([season])                         # pull one season as a Polars DataFrame
    con.execute("CREATE TABLE IF NOT EXISTS raw.pbp AS SELECT * FROM pbp LIMIT 0")  # first time only: copy the columns, zero rows
    con.execute("DELETE FROM raw.pbp WHERE season = ?", [season])                #wipes 2026 data for the refresh, since the data is updated throughout the season
    con.execute("INSERT INTO raw.pbp BY NAME SELECT * FROM pbp")                    # append this season's rows, matching columns by name
    print(f"{season}: loaded {pbp.height:,} rows")       # progress message per season

def main():
    con = duckdb.connect(str(DB_PATH))                   # open the database
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")       # make sure raw exists
    seasons = [int(s) for s in sys.argv[1:]] or SEASONS   # seasons typed after the script name; if none, load all
    for season in seasons:                                 # loop over whichever seasons were chosen
        load_season(con, season)                           # delete + reload that one season

    counts = con.execute("SELECT season, COUNT(*) FROM raw.pbp GROUP BY season ORDER BY season").fetchall()               # rows per season, in season order
    for season, n in counts:                             # each row is a (season, count) tuple, so unpack both
        print(f"  {season}: {n:,}")                      # print each season's count

    con.close()                                          # release the file lock                                                                    
if __name__ == "__main__":        # only run main() when the file is run directly, not when it's imported
    main()