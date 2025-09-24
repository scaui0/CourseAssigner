import csv
import json
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

import networkx as nx

WEIGHTS = {
    0: -100,
    1: -70,
    2: -30
}


class ValidationError(Exception):
    pass


def print_assignments(assignments):
    for course, students in assignments.items():
        print(f"[{course}]")
        for student in students:
            print(student)

        print()


def write_assignments(assignments, path: Path):
    result = []
    for course, students in assignments.items():
        result.append(f"# {course}")
        for student in students:
            result.append(f"- {student}")

        result.append("")

    path.write_text("\n".join(result), "utf-8")


def calculate_statistic(assignments, student_preferences):
    assignments_reversed = {
        student: [c for c, students in assignments.items() if student in students][0]
        for student in student_preferences}

    wishes_granted = [0, 0, 0, 0]
    for (student, preferences), (_, granted) in zip(student_preferences.items(), assignments_reversed.items()):
        wishes_granted[preferences.index(granted) if granted in preferences else 3] += 1

    return wishes_granted


def print_statistic(stats):
    print(
        ("{} got their first preference\n{} got their second preference\n{} got their third preference\n{} people"
         " did not get any of their preferences").format(*stats)
    )


def validate(courses, student_preferences):
    general_capacity = sum(courses.values())
    if general_capacity < len(student_preferences):
        raise ValidationError(
            f"Students can't fit into courses: {len(student_preferences) - general_capacity} more places needed!")

    for student, preferences in student_preferences.items():
        for pref in preferences:
            if pref not in courses:
                raise ValidationError(f"Invalid course {pref!r}! [Occurred in student {student!r}]")


def assign_to_courses(courses: dict[str, int], student_preferences: dict[str, list[str]]):
    general_capacity = sum(courses.values())

    # noinspection PyPep8Naming
    G = nx.DiGraph()

    # add courses
    for course, capacity in courses.items():
        G.add_node(course, demand=capacity)

    # Add students
    for student, prefs in student_preferences.items():
        G.add_node(student, demand=-1)

        for i, pref in enumerate(prefs):
            G.add_edge(student, pref, weight=WEIGHTS[i], capacity=1)

        for course in courses:
            if course not in prefs:
                G.add_edge(student, course, weight=0, capacity=1)

    # Add dummy students to fill all courses (required by min_cost_flow)
    for i in range(general_capacity - len(student_preferences)):
        G.add_node(f"dummy_{i}", demand=-1)
        for course in courses:
            G.add_edge(f"dummy_{i}", course, weight=0)

    assignments = defaultdict(lambda: [])

    # assign students to courses
    for student, preference_courses in nx.min_cost_flow(G).items():
        if student in courses:
            continue

        assert sum(preference_courses.values()) == 1
        if not student.startswith("dummy_"):
            assignments[max(preference_courses, key=preference_courses.get)].append(student)

    return assignments


def read_courses_and_preferences(courses_path: Path, preferences_path: Path):
    if courses_path.suffix == ".json":
        courses = json.loads(courses_path.read_text("utf-8"))
    elif courses_path.suffix == ".csv":
        courses_raw = csv.DictReader(courses_path.read_text("utf-8").splitlines(), delimiter=";")

        courses = {course["Name"]: int(course["Capacity"]) for course in courses_raw}
    else:
        raise ValidationError(f"Invalid suffix {courses_path.suffix!r} for courses file!")

    if preferences_path.suffix == ".json":
        preferences = json.loads(preferences_path.read_text("utf-8"))
    elif preferences_path.suffix == ".csv":
        preferences_raw = csv.DictReader(preferences_path.read_text("utf-8").splitlines(), delimiter=";")

        preferences = {
            student["Name"]: [student["Preference1"], student["Preference2"], student["Preference3"]]
            for student in preferences_raw
        }
    else:
        raise ValidationError(f"Invalid suffix {preferences_path.suffix!r} for courses file!")

    return courses, preferences


DEFAULT_COURSES_PATHS = (
    "courses.csv",
    "courses.json"
)

DEFAULT_PREFERENCES_PATH = (
    "preferences.csv",
    "preferences.json"
)


def get_first_existing_path(check_paths, *, error_message="No file found!"):
    for potential_path in check_paths:
        if potential_path.exists():
            return potential_path

    raise ValidationError(error_message)


def get_courses_and_preferences_files(
        input_path: Path, courses_path: Path | None = None, preferences_path: Path | None = None):
    if courses_path is None:
        courses_path = get_first_existing_path((input_path / p for p in DEFAULT_COURSES_PATHS),
                                               error_message="Not course file found!")
        print(f"Using course path: {courses_path}")
    if preferences_path is None:
        preferences_path = get_first_existing_path((input_path / p for p in DEFAULT_PREFERENCES_PATH),
                                                   error_message="No preferences file found!")
        print(f"Using preferences path: {preferences_path}")

    return courses_path, preferences_path


def main():
    parser = ArgumentParser(
        "CourseAssigner",
        description="This program assigns students with 3 preferences each to courses."
    )
    parser.add_argument(
        "-c", "--courses", type=Path,
        help="The file containing the courses. Preferred over files in input folder",
        required=False
    )
    parser.add_argument(
        "-p", "--preferences", type=Path,
        help="The file containing the student's preferences. Preferred over files in input folder",
        required=False
    )
    parser.add_argument("-i", "--input", type=Path, help="The path for the input folder", required=False,
                        default=Path.cwd() / "input")
    parser.add_argument("-o", "--output", type=Path, help="The path for the output file", required=False,
                        default=Path.cwd() / "output.txt")

    args = parser.parse_args()

    courses_path, preferences_path = get_courses_and_preferences_files(args.input, args.courses, args.preferences)

    courses, student_preferences = read_courses_and_preferences(courses_path, preferences_path)

    validate(courses, student_preferences)

    assignments = assign_to_courses(
        courses,
        student_preferences
    )
    print_assignments(assignments)
    write_assignments(assignments, args.output)
    print_statistic(calculate_statistic(assignments, student_preferences))


if __name__ == '__main__':
    main()
