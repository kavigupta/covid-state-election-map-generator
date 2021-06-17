import os

import pandas as pd
import us

target_margin = .5224

def load_general_data():
    pops = pd.read_csv("pops.csv")
    pops["State"] = pops["State"].apply(lambda x: x[1:])
    pops["Population"] = pops["Population"].apply(lambda x: int(x.replace(",","")))
    pops = pops.set_index("State")
    ec = pd.read_csv("ec.csv")
    return ec.set_index("state").join(pops, how="inner")

def load_statistics():
    df = pd.read_csv("us-covid-number-fully-vaccinated.csv")[["Entity", "Day", "people_fully_vaccinated"]]
    df["Entity"] = df["Entity"].apply(lambda x: x if x != "New York State" else "New York")
    return df

def get_data(date):
    df = load_statistics()
    for_day = df[df.Day == date].set_index("Entity").join(load_general_data(), how="right").fillna(0)
    for_day.people_fully_vaccinated /= for_day.Population
    multiplier = (
        target_margin
        * for_day.Population.sum()
        / (for_day.people_fully_vaccinated * for_day.Population).sum()
    )
    for_day["dem_margin"] = 2 * for_day.people_fully_vaccinated * multiplier - 1
    return for_day, multiplier

categories = {
        (-float("inf"), -.05) : "#ff4d4d",
        (-0.05, -0.01) : "#ffb3b3",
        (-0.01, 0) : "#ff8080",
        (0, 0.01) : "#8080ff",
        (0.01, 0.05) :"#b3b3ff",
        (0.05, float("inf")) : "#4d4dff"
    }
def color_for(margin):
    for (start, end), c in categories.items():
        if start < margin <= end:
            return c
    1/0

def dem_ec(for_day):
    return for_day[for_day.dem_margin >= 0].electoral_college.sum()
    
def generate_map(date):
    styles = []
    for_day, multiplier = get_data(date)
    for i, row in for_day.iterrows():
        abbr = us.states.lookup(i).abbr.lower()
        c = color_for(row.dem_margin)
        styles.append(f".{abbr} {{fill:{c}}}")
    with open("map.svg") as f:
        svg = f.read()
    svg = svg.replace("empty space below. */", "empty space below. */\n" + "\n".join(styles))
    svg = svg.replace("$DATE", date)
    svg = svg.replace("$06", f"{dem_ec(for_day):.0f}")
    svg = svg.replace("$32", f"{538 - dem_ec(for_day):.0f}")
    svg = svg.replace("$MULT", f"{multiplier:.2f}")
    
    path = f"outputs/{date}.svg"
    with open(path, "w") as f:
        f.write(svg)
    os.system(f"inkscape --export-type=\"png\" {path}")
    os.remove(path)