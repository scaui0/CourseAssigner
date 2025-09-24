# CourseAssigner

This program assigns students with 3 preferences each to courses.

## Motivation

We recently had out *Project Days* at our school, and there were many students that weren't fine with the courses they
were assigned to. Each student had three preferences and our student council assigned us to the courses with their (
limited) possibilities. They counted the votes manually which leaded to an unperfect result.

Since I program for quite a long time, I asked myself if I were able to make a program that optimizes this assignment.
After I worked one and a half hours, I got a prototype which worked very good. In a test with 250 random generated
students, it assigned 170 students to their first preference, and only 4 persons weren't assigned to any of their
preferences.

And after I worked 2 or 3 hours more, I got a program with a near perfect result, which I suggested our student council
for the next Project Days. And they accepted!

## Install

You need:

* [Python](https://python.org)
* [uv](https://docs.astral.sh/uv/) or pip, Pythons built-in package manager.

### Using `pip`

Run the following command after you activated your Python Environment (leave as it if you don't know what this is):
`pip install git+https://github.com/scaui0/CourseAssigner.git`

### Using `uv`

Run the following command:
`uv pip install "git+https://github.com/scaui0/CourseAssigner.git"`

## Usage

To run the program, use the `courseassigner` command from your terminal. CourseAssigner will look for courses and
preferences in the `input` folder. You can specify them manually by using the `-c` and `-p` option.

### Examples

`courseassigner` will output an optimized assignment for all students in `input/preferences.csv` and all courses of
`input/courses.csv`.

## Testing the Program

If you are not sure about this program, you can test it by generating random student preferences. I included a script
`generate_random_presets.py` in the `scripts` folder to do so. To run it, either using the terminal command
`python scripts/generate_random_presets.py` or by double-clicking the file.

The script will generate two files `courses.json` and `preferences.json` inside the `input` folder.

## The Input File Formats

The program accepts both `csv` and `json` files. For detailed examples see the `formats` folder.
