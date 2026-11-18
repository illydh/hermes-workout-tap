---
name: workout
description: "Plan a strength or run session from a reviewed exercise catalog: a venue-aware shortlist, a schema the model must follow, and a code-checked duration. Proposes only; no weights, no medical advice."
version: 0.1.2
author: hw3
platforms: [linux, macos]
metadata:
  hermes:
    tags: [fitness, workout, planning, running, strength]
---

# Workout planner

Builds one workout for an adult from a fixed catalog of exercises, then checks the result in code.
It never schedules anything: placing a session on a calendar is a separate step that needs the
user's approval.

## When to use

The user asks for a workout, a gym or home session, or a run session. Not for diets, injuries,
medical questions or weights to lift: say that is outside this skill.

## Procedure

1. Get four facts, asking only for what is missing: the venue's equipment, the minutes
   available (15 to 120), the session type (`lift` or `run`) and the goal in a few words.
   Equipment tags: `mat`, `dumbbells`, `bench`, `cable`, `barbell`, `squat_rack`, `kettlebell`,
   `bands`. A home with nothing is `none`. Never assume equipment the user did not list.
2. Run `python3 ${HERMES_SKILL_DIR}/scripts/workout_tool.py prompt --equipment <tags> --minutes <n> --type <lift|run> --goal "<goal>"`.
   It prints the instructions, the schema and a shortlist of about 40 exercises the venue
   supports. Use only exercise ids from that shortlist.
3. Write the workout as one JSON object exactly as the prompt describes, then pass it in single quotes to
   `python3 ${HERMES_SKILL_DIR}/scripts/workout_tool.py validate --equipment <tags> --minutes <n> --workout '<json>'`
   (an argument, never piped: agent command scanners block output piped into `python3`).
   If it prints `"valid": false`, fix the named problem once and validate again. If it still
   fails, tell the user you could not produce a valid session.
4. Show the user the title, the exercises with sets and reps or seconds, and the duration the
   tool calculated (never your own estimate).

If a command fails to run, say so and stop. Never write a workout the tool did not validate.

## Limits

- The catalog is 372 filtered entries from free-exercise-db (public domain) plus ten bodyweight
  moves (`own_` ids) and three run sessions of our own. Machines, balls, ballistic lifts and expert moves are left out on purpose.
- Run sessions are timed blocks: sets of seconds with rest between sets.
- No calculators, no nutrition data, no downloads at run time.

## Files

- `scripts/workout_tool.py` - the command-line front used above.
- `scripts/workouts.py` - catalog loading, shortlist, prompt and validator (standard library only).
- `scripts/exercise_catalog.json` - the reviewed catalog with its source commit and license.
- `scripts/build_exercise_catalog.py` - how the catalog was built from the dataset (offline, once).
- `NOTICE.md` - third-party attribution and the dataset's license text.
