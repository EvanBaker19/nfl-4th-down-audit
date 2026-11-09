# Import the nflreadpy library and give it the short alias "nfl" so we type less
import nflreadpy as nfl
# Import polars with the alias "pl" (the standard convention, like "pd" for pandas)
import polars as pl

# TODO 1: Load play-by-play data for the 2025 season into a variable called pbp
# Hint: nfl.load_pbp() takes a list of seasons
pbp = nfl.load_pbp([2025])
# TODO 2: Print the shape of pbp (rows, columns)
print(pbp.shape)
# Hint: Polars DataFrames have a .shape attribute, same as pandas

# TODO 3: Filter pbp down to only 4th-down plays and save it as fourth
# Hint: pbp.filter(pl.col("column_name") == value)
fourth = pbp.filter(pl.col("down") == 4)
# TODO 4: Print how many 4th-down plays there were
fourth_count = fourth.shape[0]
print(f"Number of 4th-down plays: {fourth_count}")
# TODO 5: Count 4th-down plays by play_type (punt, field_goal, run, pass, etc.)
count_by_play_type = fourth.group_by("play_type").len().sort("len", descending=True)
print(count_by_play_type)
# Hint: .group_by("play_type").len(), then .sort() so it's readable

# TODO 6: Select and print the first 10 rows of just these columns:
# posteam, ydstogo, yardline_100, play_type, wp, wpa
pbp_type = fourth.select(["posteam", "ydstogo", "yardline_100", "play_type", "wp", "wpa"]).head(10)
print(pbp_type)
# Hint: .select([...]) then .head(10)

#find the percentage of 4th downs were the team went for it (play_type == "run" or play_type == "pass") vs. those that punted or kicked a field goal
# Keep only real decisions (go, punt, kick) - drop no_play and qb_kneel
decisions = fourth.filter(pl.col("play_type").is_in(["run", "pass", "punt", "field_goal"]))

# Count how many real decisions there were (number of rows)
decisions_count = decisions.shape[0]

# From the decisions, keep only the go-for-it plays (run or pass) and count them
go_count = decisions.filter(pl.col("play_type").is_in(["run", "pass"])).shape[0]

# Divide go-for-it plays by total decisions and multiply by 100 for a percentage
go_for_it_rate = go_count / decisions_count * 100

# Print the rate rounded to 2 decimal places (:.2f = float with 2 decimals)
print(f"Go-for-it rate on real 4th-down decisions: {go_for_it_rate:.2f}%")