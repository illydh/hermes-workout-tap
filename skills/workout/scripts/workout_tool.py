"""Command-line front for the workout skill (standard library only).

  python3 scripts/workout_tool.py prompt --equipment mat,dumbbells --minutes 45 --goal "..."
  python3 scripts/workout_tool.py candidates --equipment none --type run
  python3 scripts/workout_tool.py validate --equipment mat --minutes 45 --workout '{...workout json...}'

Equipment is a comma-separated list of: mat, dumbbells, bench, cable, barbell, squat_rack,
kettlebell, bands. Use "none" for a venue with no equipment (home). The workout is an argument, not
standard input: agent command scanners (Hermes's among them) block output piped into an interpreter.
"""

import argparse
import json
import sys

import workouts


def equipment_arg(text: str) -> frozenset[str]:
    tags = frozenset(part.strip() for part in text.split(",") if part.strip() and part.strip() != "none")
    unknown = tags - workouts.EQUIPMENT_TAGS
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown equipment: {sorted(unknown)}")
    return tags


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prompt", "candidates", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--equipment", type=equipment_arg, default=frozenset(), help="comma-separated tags, or none")
        command.add_argument("--type", choices=("lift", "run"), default="lift", dest="session_type")
        if name != "candidates":
            command.add_argument("--minutes", type=int, required=True, help="time available, 15 to 120")
        if name == "prompt":
            command.add_argument("--goal", required=True)
        if name == "validate":
            command.add_argument("--workout", required=True, help="the workout as one JSON object")
    args = parser.parse_args(argv)
    try:
        if args.command == "candidates":
            shortlist = workouts.candidates(args.equipment, args.session_type)
            print(json.dumps({key: {"name": ex.name, "mode": ex.mode, "group": ex.group} for key, ex in shortlist.items()}, indent=1))
        elif args.command == "prompt":
            print(workouts.generation_prompt(args.goal, args.equipment, args.minutes, [], args.session_type))
        else:
            workout = workouts.validate_workout(json.loads(args.workout), args.equipment, args.minutes)
            print(json.dumps({"valid": True, "duration_minutes": workout.duration_minutes, "workout": workout.as_dict()}, indent=1))
    except (ValueError, TypeError) as error:
        print(json.dumps({"valid": False, "error": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
