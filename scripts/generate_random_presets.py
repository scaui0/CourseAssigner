import json
import random
from itertools import islice
from pathlib import Path

RANDOM_PRESETS = json.loads((Path(__file__).parent / "random_presets.json").read_text("utf-8"))

NAMES = RANDOM_PRESETS["names"]

COURSES_WITH_WEIGHT_AND_CAPACITY = {name: (p["weight"], p["capacity"]) for name, p in RANDOM_PRESETS["courses"].items()}
COURSES = list(COURSES_WITH_WEIGHT_AND_CAPACITY)
COURSE_WEIGHTS = [w for w, c in COURSES_WITH_WEIGHT_AND_CAPACITY.values()]
COURSES_WITH_CAPACITY = {c: cap for c, (w, cap) in COURSES_WITH_WEIGHT_AND_CAPACITY.items()}

assignments = {}


def infinite_course_generator():
    while True:
        yield random.choices(COURSES, COURSE_WEIGHTS)[0]


course_generator = iter(infinite_course_generator())


def generate_courses():
    generated = []

    for i in range(3):
        while (course := next(course_generator)) in generated:
            pass
        generated.append(course)

    return generated


num_students = input(f"How many random students would you like to generate?\nPress enter to use default (300) ")
num_students = int(num_students or 300)

print(f"Generating random preferences for {num_students} students.")

for name in islice(NAMES, num_students):
    assignments[name] = generate_courses()

(Path(__file__).parent.parent / "input/preferences.json").write_text(json.dumps(assignments), encoding="utf-8")
(Path(__file__).parent.parent / "input/courses.json").write_text(json.dumps(COURSES_WITH_CAPACITY), encoding="utf-8")
print("Done.")
