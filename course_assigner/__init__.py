import json
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

WEIGHTS = {
    0: -100,
    1: -70,
    2: -30
}


class ValidationError(Exception):
    pass


def draw_graph(assignments):
    graph = nx.DiGraph(assignments)
    nx.draw(graph, with_labels=True)
    plt.show()


def print_assignments(assignments):
    for course, students in assignments.items():
        print(f"[{course}]")
        for student in students:
            print(student)

        print()


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


def main():
    parser = ArgumentParser("CourseAssigner",
                            description="This program assigns students with 3 preferences each to courses.")
    parser.add_argument("-c", "--courses", type=Path, help="The file containing the courses", required=True)
    parser.add_argument("-p", "--preferences", type=Path, help="The file containing the student's preferences",
                        required=True)
    parser.add_argument("-g", "--graph", action="store_true",
                        help="Whether to open a new windows that shows a graph with all students and courses. "
                             "(Might be unreadable when using many students)",
                        required=False)

    args = parser.parse_args()

    courses = json.loads(args.courses.read_text("utf-8"))
    student_preferences = json.loads(args.preferences.read_text("utf-8"))

    validate(courses, student_preferences)

    assignments = assign_to_courses(
        courses,
        student_preferences
    )
    print_assignments(assignments)
    print_statistic(calculate_statistic(assignments, student_preferences))
    if args.graph:
        draw_graph(assignments)


if __name__ == '__main__':
    main()
