import os
import glob
import pandas as pd

# Australian seasons by month number
SEASON_MAP = {
    12: "Summer", 1: "Summer", 2: "Summer",
    3: "Autumn", 4: "Autumn", 5: "Autumn",
    6: "Winter", 7: "Winter", 8: "Winter",
    9: "Spring", 10: "Spring", 11: "Spring",
}

# Month names -> month numbers (keeps a clear source of truth for column order)
MONTH_ORDER = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

def find_csvs():
    """
    Find all station CSVs. Prefer ./temperatures/stations_group_*.csv,
    otherwise fall back to ./stations_group_*.csv.
    Raises FileNotFoundError if none are found.
    """
    patterns = []
    if os.path.isdir("temperatures"):
        patterns.append(os.path.join("temperatures", "stations_group_*.csv"))
    patterns.append("stations_group_*.csv")  # fallback

    files, seen = [], set()
    for pat in patterns:
        for f in glob.glob(pat):
            if f not in seen:
                files.append(f)
                seen.add(f)

    files.sort()
    if not files:
        raise FileNotFoundError(
            "No CSV files found. Place files in ./temperatures/ or current folder."
        )
    return files


def load_and_combine(files):
    """
    Read each CSV, attach a 'Year' column inferred from the filename suffix
    (e.g., '..._2021.csv' -> Year=2021), and return one combined DataFrame.
    """
    frames = []
    for f in files:
        # Extract the last underscore-separated token before the extension
        # e.g. "stations_group_2021.csv" -> "2021"
        base_no_ext = os.path.splitext(f)[0]
        last_token = base_no_ext.split("_")[-1]
        year = int(last_token) if last_token.isdigit() else None

        df = pd.read_csv(f)
        df["Year"] = year
        frames.append(df)

    # Important: return the concatenated DataFrame
    return pd.concat(frames, ignore_index=True)


def to_long(df):
    """
    Convert the wide monthly columns into a long format with columns:
    STATION_NAME, STN_ID, LAT, LON, Year, Month, Temp, MonthNum, Season.
    Drops rows where Temp is NaN.
    """
    long_df = df.melt(
        id_vars=["STATION_NAME", "STN_ID", "LAT", "LON", "Year"],
        value_vars=list(MONTH_ORDER.keys()),
        var_name="Month",
        value_name="Temp",
    )
    long_df = long_df.dropna(subset=["Temp"])
    long_df["MonthNum"] = long_df["Month"].map(MONTH_ORDER)
    long_df["Season"] = long_df["MonthNum"].map(SEASON_MAP)
    return long_df


def compute_outputs(long_df):
    """
    Compute:
      1) Seasonal averages (mean Temp per Season, 2 d.p., sorted by season name)
      2) Station(s) with largest Temp range (max - min), include ties
      3) Most stable (min std) and most variable (max std) stations (include ties)
    Returns (seasonal_avg, largest_range_df, most_stable_series, most_variable_series).
    """
    # 1) Seasonal averages
    seasonal_avg = long_df.groupby("Season")["Temp"].mean().round(2).sort_index()

    # 2) Largest temperature range per station
    stats = long_df.groupby("STATION_NAME")["Temp"].agg(["min", "max"])
    stats["range"] = stats["max"] - stats["min"]
    max_range = stats["range"].max()
    largest_range = stats[stats["range"] == max_range].sort_index()

    # 3) Stability (std dev) per station
    stds = long_df.groupby("STATION_NAME")["Temp"].std()
    min_std = stds.min()
    max_std = stds.max()
    most_stable = stds[stds == min_std].sort_index()
    most_variable = stds[stds == max_std].sort_index()

    return seasonal_avg, largest_range, most_stable, most_variable


def save_outputs(seasonal_avg, largest_range, most_stable, most_variable, out_dir="."):
    """
    Write three text files:
      - average_temp.txt
      - largest_temp_range_station.txt
      - temperature_stability_stations.txt
    The formats match the original behavior.
    """
    avg_path   = os.path.join(out_dir, "average_temp.txt")
    range_path = os.path.join(out_dir, "largest_temp_range_station.txt")
    stab_path  = os.path.join(out_dir, "temperature_stability_stations.txt")

    # Seasonal averages
    with open(avg_path, "w", encoding="utf-8") as f:
        for season, val in seasonal_avg.items():
            f.write(f"{season}: {val:.2f}°C\n")

    # Largest temp range (include all ties)
    with open(range_path, "w", encoding="utf-8") as f:
        for name, row in largest_range.iterrows():
            f.write(
                f"{name}: Range {row['range']:.2f}°C "
                f"(Max: {row['max']:.2f}°C, Min: {row['min']:.2f}°C)\n"
            )

    # Stability report
    with open(stab_path, "w", encoding="utf-8") as f:
        for name, val in most_stable.items():
            f.write(f"Most Stable: {name}: StdDev {val:.2f}°C\n")
        for name, val in most_variable.items():
            f.write(f"Most Variable: {name}: StdDev {val:.2f}°C\n")


def main():
    files = find_csvs()
    data = load_and_combine(files)
    long_df = to_long(data)
    seasonal_avg, largest_range, most_stable, most_variable = compute_outputs(long_df)
    save_outputs(seasonal_avg, largest_range, most_stable, most_variable, out_dir=".")

    # Console summary (unchanged format)
    print("=== Seasonal Averages ===")
    print(seasonal_avg.to_string())
    print("\n=== Largest Temp Range (ties listed) ===")
    print(largest_range[["min", "max", "range"]].to_string())
    print("\n=== Stability ===")
    for name, val in most_stable.items():
        print(f"Most Stable: {name}: StdDev {val:.2f}°C")
    for name, val in most_variable.items():
        print(f"Most Variable: {name}: StdDev {val:.2f}°C")


if __name__ == "__main__":
    main()
