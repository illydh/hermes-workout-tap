# hermes-workout-tap

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill tap with one skill, `workout`. It plans a
strength or run session from a reviewed exercise catalog, checks the result in code (exercise ids, equipment,
duration), and only proposes: it never writes a calendar or gives weights or medical advice.

## Install

```bash
hermes skills tap add illydh/hermes-workout-tap
hermes skills install illydh/hermes-workout-tap/workout
```

Tested with Hermes v0.21.5 (tag `v2026.9.24`). The skill's scripts need only Python 3 and its standard library.

## Use

Ask Hermes for a workout, for example "a 40-minute dumbbell session at home for upper-body strength". The skill
can also be run by hand from its installed folder:

```bash
python3 scripts/workout_tool.py prompt --equipment dumbbells,bench --minutes 40 --type lift --goal "upper-body strength"
python3 scripts/workout_tool.py validate --equipment dumbbells,bench --minutes 40 < workout.json
```

## Versions

Tag `v0.1.0` is the first release (`version: 0.1.0` in `SKILL.md`).

## Data and license

The exercise catalog is filtered from [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db)
(Unlicense, commit `f00c92c`); see `skills/workout/NOTICE.md`. Built for a university course assignment
(USC CSCI 599, Fall 2026).
