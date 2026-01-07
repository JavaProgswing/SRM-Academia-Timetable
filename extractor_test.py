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
    # Load filename from config.json
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        login_file = config.get("login_file", "session.pkl")
    session = load_pickle_login(login_file)
    timetable_html = fetch_timetable_page(session)
    student_details = parse_student_details(timetable_html)
    save_to_file(f'{{"data": {json.dumps(student_details)}}}', "student_details.json")
    timetable = get_timetable(student_details)
    save_to_file(f'{{"data": {json.dumps(timetable)}}}', "timetable.json")
    # Saves the student details and timetable to JSON files.
    # Make sure to generate the session pickle file first using login_test.py.


if __name__ == "__main__":
    main()
