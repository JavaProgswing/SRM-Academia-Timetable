import json
from srmtimetable.utils import load_pickle_login, save_to_file
from srmtimetable.academia import (
    get_timetable,
    fetch_timetable_page,
    parse_student_details,
    fetch_calendar_html,
    parse_calendar_events,
)


def main():
    session = load_pickle_login("yk9852_1756393627.pickle")
    timetable_html = fetch_timetable_page(session)
    student_details = parse_student_details(timetable_html)
    save_to_file(f'{{"data": {json.dumps(student_details)}}}', "student_details.json")
    timetable = get_timetable(student_details)
    save_to_file(f'{{"data": {json.dumps(timetable)}}}', "timetable.json")
    calendar_html = fetch_calendar_html(session, semester=student_details["Semester"])
    calendar_events = parse_calendar_events(calendar_html)
    save_to_file(f'{{"data": {json.dumps(calendar_events)}}}', "calendar_events.json")
    # Saves the student details, timetable, and calendar events to JSON files.
    # Make sure to generate the session pickle file first using login_test.py.


if __name__ == "__main__":
    main()
