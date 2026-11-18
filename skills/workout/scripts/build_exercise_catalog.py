# Adapted from https://github.com/yuhonas/free-exercise-db (dist/exercises.json, Unlicense, public domain):
# exercise ids, names, equipment, muscles, level and force are read from that dataset. The filters,
# the equipment mapping, the muscle groups, the ten `own_` bodyweight moves and the run sessions
# below are our own.
"""Build skills/exercise_catalog.json from a local copy of free-exercise-db's exercises.json.

The deployed agent never downloads anything: this runs once, offline, on a file fetched at a pinned
commit, and its reviewed output is committed. Run from hw3/:

  python scripts/build_exercise_catalog.py --source PATH/exercises.json --commit SHA --retrieved YYYY-MM-DD
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

SOURCE_URL = "https://github.com/yuhonas/free-exercise-db"
OUT = Path(__file__).resolve().parents[1] / "skills" / "exercise_catalog.json"

KEEP_LEVELS = {"beginner", "intermediate"}          # no expert lifts: this is not a coach
# The dataset's equipment value -> the tags our venues use. Anything else (machines, balls, EZ bars,
# foam rollers, "other", missing) is dropped because no venue tag can promise it.
EQUIPMENT_TAGS = {
    "body only": (), "dumbbell": ("dumbbells",), "barbell": ("barbell",),
    "cable": ("cable",), "kettlebells": ("kettlebell",), "bands": ("bands",),
}
GROUPS = {
    "quadriceps": "legs", "hamstrings": "legs", "glutes": "legs", "calves": "legs", "adductors": "legs", "abductors": "legs",
    "chest": "chest", "lats": "back", "middle back": "back", "lower back": "back", "traps": "back",
    "shoulders": "shoulders", "biceps": "arms", "triceps": "arms", "forearms": "arms", "abdominals": "core",
}  # "neck" is deliberately absent
APPARATUS = re.compile(
    r"behind[- ]the[- ]neck|\bneck\b|pull-?up|chin-?up|\bdips?\b|hang|muscle-?up|rope|\brings?\b|\bbox\b|\bstep\b|stair|"
    r"climb|handstand|planche|lever|swing|\btire\b|sled|suspend|\btrx\b|stability|\bball\b|bosu|smith|machine|sandbag|"
    r"clean|snatch|jerk|\bjump|\bpower\b|windmill|turkish|jefferson|\bhack\b|sprints?|plate movers",  # ballistic or technical lifts
    re.I,
)
BENCH = re.compile(r"\bbench\b|\bincline\b|\bdecline\b|\blying\b|\bpreacher\b|\bseated\b", re.I)
FLOOR = re.compile(r"crunch|sit-?up|plank|bridge|leg raise|bicycle|superman|dead bug|bird dog|\blying\b|\bfloor\b|v-?up|flutter|scissor", re.I)
SQUAT = re.compile(r"\bsquats?\b", re.I)
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ,()/'.+&-]{0,59}$")
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")

# Our own bodyweight moves. The dataset has few standing leg, back or core moves for a home with no
# equipment, so these fill that gap. Floor moves need a mat, as in convert().
def _own(ident: str, name: str, group: str, equipment: list[str], mode: str = "reps") -> dict:
    return {"id": ident, "name": name, "kind": "strength", "group": group, "equipment": equipment, "mode": mode, "level": "beginner"}


OWN_MOVES = (
    _own("own_reverse_lunge", "Reverse Lunge", "legs", []),
    _own("own_split_squat", "Bodyweight Split Squat", "legs", []),
    _own("own_wall_sit", "Wall Sit", "legs", [], "seconds"),
    _own("own_calf_raise", "Bodyweight Calf Raise", "legs", []),
    _own("own_glute_bridge", "Glute Bridge", "legs", ["mat"]),
    _own("own_wall_pushup", "Wall Push-Up", "chest", []),
    _own("own_wall_angel", "Wall Angel", "back", []),
    _own("own_superman", "Superman", "back", ["mat"]),
    _own("own_bird_dog", "Bird Dog", "core", ["mat"]),
    _own("own_dead_bug", "Dead Bug", "core", ["mat"]),
)

# Our own sessions: the dataset has no running. Timed blocks; sets x seconds with rest between sets.
RUNS = (
    {"id": "run_easy", "name": "Easy run", "kind": "run", "group": "run", "equipment": [], "mode": "seconds", "level": "beginner"},
    {"id": "run_intervals", "name": "Run intervals", "kind": "run", "group": "run", "equipment": [], "mode": "seconds", "level": "intermediate"},
    {"id": "run_long", "name": "Long run", "kind": "run", "group": "run", "equipment": [], "mode": "seconds", "level": "intermediate"},
)


def convert(entry: dict) -> dict | None:
    """One dataset entry to one catalog entry, or None when we do not use it."""
    if entry.get("category") != "strength" or entry.get("level") not in KEEP_LEVELS:
        return None
    base = EQUIPMENT_TAGS.get(entry.get("equipment"))
    muscles = entry.get("primaryMuscles") or []
    name, ident = entry.get("name", ""), entry.get("id", "")
    if base is None or not muscles or muscles[0] not in GROUPS:
        return None
    if not NAME.match(name) or not ID.match(ident) or APPARATUS.search(name):
        return None
    tags = set(base)
    if tags & {"dumbbells", "barbell", "kettlebell"} and BENCH.search(name):
        tags.add("bench")
    if "barbell" in tags and SQUAT.search(name):
        tags.add("squat_rack")
    if not tags and FLOOR.search(name):
        tags.add("mat")
    return {
        "id": ident, "name": name, "kind": "strength", "group": GROUPS[muscles[0]],
        "equipment": sorted(tags), "mode": "seconds" if entry.get("force") == "static" else "reps", "level": entry["level"],
    }


def build(entries: list[dict], commit: str, retrieved: str) -> dict:
    exercises = {}
    for entry in entries:
        item = convert(entry)
        if item:
            exercises[item["id"]] = item
    for own in OWN_MOVES + RUNS:
        exercises[own["id"]] = {**own, "equipment": list(own["equipment"])}
    return {
        "source": {"name": "free-exercise-db", "url": SOURCE_URL, "file": "dist/exercises.json", "commit": commit,
                   "license": "Unlicense (public domain dedication, LICENSE.md in the source repository)", "retrieved": retrieved,
                   "note": "From the dataset only ids, names, equipment, primary muscle, level and force are used; no instructions or images. Entries with ids starting own_ or run_ are our own."},
        "exercises": [exercises[key] for key in sorted(exercises)],
    }


def summary(catalog: dict, samples: int = 10) -> str:
    items = catalog["exercises"]
    lines = [f"{len(items)} exercises", "", "By equipment needed:"]
    for key, count in sorted(Counter("+".join(i["equipment"]) or "none" for i in items).items()):
        lines.append(f"  {key}: {count}")
    lines += ["", "By muscle group:"] + [f"  {k}: {v}" for k, v in sorted(Counter(i["group"] for i in items).items())]
    lines += ["", "By mode:"] + [f"  {k}: {v}" for k, v in sorted(Counter(i["mode"] for i in items).items())]
    step = max(1, len(items) // samples)
    lines += ["", f"{samples} samples (every {step}th by id):"]
    for item in items[::step][:samples]:
        lines.append(f"  {item['id']} | {item['name']} | {item['group']} | {'+'.join(item['equipment']) or 'none'} | {item['mode']} | {item['level']}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, type=Path, help="local copy of dist/exercises.json")
    parser.add_argument("--commit", required=True, help="the commit the file was fetched at")
    parser.add_argument("--retrieved", required=True, help="retrieval date, YYYY-MM-DD")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    catalog = build(json.loads(args.source.read_text(encoding="utf-8")), args.commit, args.retrieved)
    args.out.write_text(json.dumps(catalog, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(summary(catalog))


if __name__ == "__main__":
    main()
