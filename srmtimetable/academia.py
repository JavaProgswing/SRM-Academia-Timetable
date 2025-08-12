import requests
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup
import html

BASE_URL = "https://academia.srmist.edu.in"


def parse_cookie_header(header: str) -> dict:
    """
    Parse Set-Cookie header parts into a dictionary.
    """
    cookies = {}
    for part in header.split(","):
        # Each part might contain several `;` segments, take first segment (the cookie)
        key_value = part.split(";")[0].strip()
        if "=" in key_value:
            key, value = key_value.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def login(username, password):
    """
    Logs in to Academia using given username and password.
    Returns an authenticated requests.Session object.
    """
    s = requests.Session()
    url_lookup = f"{BASE_URL}/accounts/p/40-10002227248/signin/v2/lookup/{username}@srmist.edu.in"

    lookup_payload = {
        "mode": "primary",
        "cli_time": int(time.time()),
        "servicename": "ZohoCreator",
        "service_language": "en",
        "serviceurl": f"{BASE_URL}/portal/academia-academic-services/redirectFromLogin",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-zcsrf-token": "iamcsrcoo=3c59613cb190a67effa5b17eaba832ef1eddaabeb7610c8c6a518b753bc73848b483b007a63f24d94d67d14dda0eca9f0c69e027c0ebd1bb395e51b2c6291d63",
        "cookie": "npfwg=1; npf_r=; npf_l=www.srmist.edu.in; npf_u=https://www.srmist.edu.in/faculty/dr-g-y-rajaa-vikhram/; zalb_74c3a1eecc=44130d4069ebce16724b1740d9128cae; ZCNEWUIPUBLICPORTAL=true; zalb_f0e8db9d3d=93b1234ae1d3e88e54aa74d5fbaba677; stk=efbb3889860a8a5d4a9ad34903359b4e; zccpn=3c59613cb190a67effa5b17eaba832ef1eddaabeb7610c8c6a518b753bc73848b483b007a63f24d94d67d14dda0eca9f0c69e027c0ebd1bb395e51b2c6291d63; zalb_3309580ed5=2f3ce51134775cd955d0a3f00a177578; CT_CSRF_TOKEN=9d0ab1e6-9f71-40fd-826e-7229d199b64d; iamcsr=3c59613cb190a67effa5b17eaba832ef1eddaabeb7610c8c6a518b753bc73848b483b007a63f24d94d67d14dda0eca9f0c69e027c0ebd1bb395e51b2c6291d63; _zcsr_tmp=3c59613cb190a67effa5b17eaba832ef1eddaabeb7610c8c6a518b753bc73848b483b007a63f24d94d67d14dda0eca9f0c69e027c0ebd1bb395e51b2c6291d63; npf_fx=1; _ga_QNCRQG0GFE=GS1.1.1737645192.5.0.1737645194.58.0.0; TS014f04d9=0190f757c98d895868ec35d391f7090a39080dd8e7be840ed996d7e2827e600c5b646207bb76666e56e22bfaf8d2c06ec3c913fe80; cli_rgn=IN; JSESSIONID=E78E4C7013F0D931BD251EBA136D57AE; _ga=GA1.3.1900970259.1737341486; _gid=GA1.3.1348593805.1737687406; _gat=1; _ga_HQWPLLNMKY=GS1.3.1737687405.1.0.1737687405.0.0.0",
    }

    # Step 1: Lookup user
    resp = s.post(url_lookup, data=lookup_payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data and len(data["errors"]) > 0:
        lookup_msg = data["errors"][0].get("message", "Unknown error")
        status_code = int(data.get("status_code", 0))

        if status_code == 400 and "HIP" in data.get("message", ""):
            raise Exception("Captcha required; automation not supported")
        raise Exception(f"Lookup failed: {lookup_msg}")

    if "User exists" not in data.get("message", ""):
        message = (
            data.get("localized_message")
            if "HIP" in data.get("message", "")
            else data.get("message", "")
        )
        raise Exception(f"User does not exist: {message}")

    lookup = data.get("lookup", {})
    identifier = lookup.get("identifier")
    digest = lookup.get("digest")

    if not identifier or not digest:
        raise Exception("Invalid lookup response, missing identifier or digest")

    # Step 2: Password authentication
    body = f'{{"passwordauth":{{"password":"{password}"}}}}'
    login_url = (
        f"{BASE_URL}/accounts/p/40-10002227248/signin/v2/primary/{identifier}/password"
        f"?digest={digest}&cli_time={int(time.time())}&servicename=ZohoCreator&service_language=en"
        f"&serviceurl={BASE_URL}/portal/academia-academic-services/redirectFromLogin"
    )

    resp = s.post(login_url, data=body, headers=headers)
    resp.raise_for_status()

    # The session cookie is maintained automatically by requests.Session
    # You can check for successful login by inspecting resp content if needed
    return s


def fetch_timetable_page(session: requests.Session):
    now = datetime.now()
    year = now.year

    # month = now.month
    # if 8 <= month <= 12:
    #     start_year = year - 1
    #     end_year = year
    # else:
    #     start_year = year - 2
    #     end_year = year - 1
    start_year = year - 2
    end_year = year - 1

    timetable_url = f"{BASE_URL}/srm_university/academia-academic-services/page/My_Time_Table_{start_year}_{str(end_year)[-2:]}"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": BASE_URL,
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "private, max-age=120, must-revalidate",
    }

    response = session.get(timetable_url, headers=headers)
    response.raise_for_status()
    raw_html = response.text

    parts = raw_html.split(".sanitize('")
    if len(parts) < 2:
        raise Exception("Invalid timetable page format, .sanitize string not found")

    hex_encoded = parts[1].split("')")[0]

    decoded_html = bytes(hex_encoded, "utf-8").decode("unicode_escape")

    return decoded_html


def calculate_year_from_reg(reg_num):
    if not reg_num or len(reg_num) < 4:
        return None
    year_str = reg_num[2:4]
    try:
        academic_year_last2 = int(year_str)
    except:
        return None

    now = datetime.now()
    current_year_last2 = now.year % 100
    academic_year = current_year_last2 + (1 if now.month >= 7 else 0)

    student_year = academic_year - academic_year_last2
    if academic_year_last2 > current_year_last2:
        student_year -= 1
    return student_year


def parse_student_details(html_content):
    """
    Parse the decoded timetable HTML to extract student info and course listings.
    Returns a dict with student details and list of course dicts.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # --- Student Information ---
    reg_number = None
    name = None
    batch = None
    mobile = None
    department = None
    semester = None

    # Locate the first table with student details
    info_table = soup.find("table", attrs={"border": "0", "align": "left"})
    if info_table:
        tds = info_table.find_all("td")
        for i in range(len(tds)):
            label = tds[i].get_text(strip=True)
            if label == "Registration Number:":
                reg_number = tds[i + 1].get_text(strip=True)
            elif label == "Name:":
                name = tds[i + 1].get_text(strip=True)
            elif label == "Batch:":
                batch = tds[i + 1].get_text(strip=True)
            elif label == "Mobile:":
                mobile = tds[i + 1].get_text(strip=True)
            elif label == "Department:":
                department = tds[i + 1].get_text(strip=True)
            elif label == "Semester:":
                semester = tds[i + 1].get_text(strip=True)

    # --- Course Table ---
    table = soup.find("table", class_="course_tbl")
    if not table:
        raise Exception("Course table not found in timetable HTML")

    courses = []

    all_td = table.find_all("td")
    columns_per_course = 11
    for i in range(columns_per_course, len(all_td), columns_per_course):
        if i + columns_per_course > len(all_td):
            break
        tds = all_td[i : i + columns_per_course]
        course = {
            "S.No": tds[0].text.strip(),
            "Course Code": tds[1].text.strip(),
            "Course Title": tds[2].text.strip(),
            "Credit": tds[3].text.strip(),
            "Regn. Type": tds[4].text.strip(),
            "Category": tds[5].text.strip(),
            "Course Type": tds[6].text.strip(),
            "Faculty Name": tds[7].text.strip(),
            "Slot": tds[8].text.strip(),
            "Room No.": tds[9].text.strip(),
            "Academic Year": tds[10].text.strip(),
        }

        courses.append(course)

    return {
        "RegNumber": reg_number,
        "Name": name,
        "Batch": int(batch),
        "Mobile": mobile,
        "Department": department,
        "Semester": int(semester),
        "Courses": courses,
    }


def cleanup(cookie):
    """
    Deletes active session for the user by calling cleanup endpoint.
    cookie: cookie string to be sent in header.
    """
    s = requests.Session()
    url = f"{BASE_URL}/accounts/p/40-10002227248/webclient/v1/account/self/user/self/activesessions"

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "x-zcsrf-token": "iamcsrcoo=8cbe86b2191479b497d8195837181ee152bcfd3d607f5a15764130d8fd8ebef9d8a22c03fd4e418d9b4f27a9822f9454bb0bf5694967872771e1db1b5fbd4585",
        "Referer": f"{BASE_URL}/accounts/p/40-10002227248/announcement/sessions-reminder?servicename=ZohoCreator&serviceurl={BASE_URL}/portal/academia-academic-services/redirectFromLogin&service_language=en",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cookie": cookie,
    }
    resp = s.delete(url, headers=headers)
    print(f"Cleanup response: {resp.status_code}: {resp.text}")


def logout(cookie):
    """
    Logs out the user by calling logout endpoint.
    cookie: cookie string to be sent in header.
    """
    s = requests.Session()
    logout_url = f"{BASE_URL}/accounts/p/40-10002227248/logout?servicename=ZohoCreator&serviceurl={BASE_URL}"
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "DNT": "1",
        "Referer": BASE_URL,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": cookie,
    }
    resp = s.get(logout_url, headers=headers)
    print(f"Logout response: {resp.status_code}: {resp.text}")


batch1 = {
    "Batch": "1",
    "Slots": [
        {
            "DayOrder": 1,
            "Slots": ["A", "A", "F", "F", "G", "P6", "P7", "P8", "P9", "P10"],
        },
        {
            "DayOrder": 2,
            "Slots": ["P11", "P12", "P13", "P14", "P15", "B", "B", "G", "G", "A"],
        },
        {
            "DayOrder": 3,
            "Slots": ["C", "C", "A", "D", "B", "P26", "P27", "P28", "P29", "P30"],
        },
        {
            "DayOrder": 4,
            "Slots": ["P31", "P32", "P33", "P34", "P35", "D", "D", "B", "E", "C"],
        },
        {
            "DayOrder": 5,
            "Slots": ["E", "E", "C", "F", "D", "P46", "P47", "P48", "P49", "P50"],
        },
    ],
}

batch2 = {
    "Batch": "2",
    "Slots": [
        {
            "DayOrder": 1,
            "Slots": ["P1", "P2", "P3", "P4", "P5", "A", "A", "F", "F", "G"],
        },
        {
            "DayOrder": 2,
            "Slots": ["B", "B", "G", "G", "A", "P16", "P17", "P18", "P19", "P20"],
        },
        {
            "DayOrder": 3,
            "Slots": ["P21", "P22", "P23", "P24", "P25", "C", "C", "A", "D", "B"],
        },
        {
            "DayOrder": 4,
            "Slots": ["D", "D", "B", "E", "C", "P36", "P37", "P38", "P39", "P40"],
        },
        {
            "DayOrder": 5,
            "Slots": ["P41", "P42", "P43", "P44", "P45", "E", "E", "C", "F", "D"],
        },
    ],
}


def get_timetable(student_data):
    """
    Builds a structured timetable with course details and timing.

    Args:
        course_data (dict): Parsed timetable data.
        batch (dict): Batch slot mapping.

    Returns:
        list: Structured timetable list for each day with start and end times.
    """

    course_data, batch = student_data["Courses"], (
        batch1 if student_data["Batch"] == 1 else batch2
    )
    # Slot index → (StartTime, EndTime)
    slot_times = [
        ("08:00", "08:50"),
        ("08:50", "09:40"),
        ("09:45", "10:35"),
        ("10:40", "11:30"),
        ("11:35", "12:25"),
        ("12:30", "01:20"),
        ("01:25", "02:15"),
        ("02:20", "03:10"),
        ("03:10", "04:00"),
        ("04:00", "04:50"),
    ]

    # Build slot → course mapping
    slot_to_course = {}
    for course in course_data:
        slots = [s for s in course["Slot"].split("-") if s]
        for slot in slots:
            slot_to_course[slot] = {
                "Course Code": course["Course Code"],
                "Course Type": course["Course Type"],
                "Title": course["Course Title"],
                "Faculty": course["Faculty Name"],
                "Room": course["Room No."],
            }

    timetable = []

    for day_info in batch["Slots"]:
        schedule = []

        for i, slot in enumerate(day_info["Slots"]):
            course_info = slot_to_course.get(slot)
            schedule.append(
                {
                    "Slot": slot,
                    "StartTime": slot_times[i][0],
                    "EndTime": slot_times[i][1],
                    "Course": course_info,  # None if no class in this slot
                }
            )

        timetable.append(
            {
                "DayOrder": day_info["DayOrder"],
                "Schedule": schedule,
            }
        )

    return timetable


def fetch_calendar_html(session: requests.Session, semester: int) -> str:
    now = datetime.now()
    year = now.year

    # Assume:
    # - Odd semester in August–December
    # - Even semester in January–May
    is_odd = semester % 2 == 1
    term = "ODD" if is_odd else "EVEN"

    url = f"{BASE_URL}/srm_university/academia-academic-services/page/Academic_Planner_{year}_{str(year + 1)[-2:]}_{term}"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": f"{BASE_URL}/",
        "Cache-Control": "public, max-age=3600, stale-while-revalidate=7200",
    }

    resp = session.get(url, headers=headers)
    resp.raise_for_status()

    return html.unescape(resp.text)


def extract_month_map(soup):
    """
    Extracts a map from column group index to month number based on <th> headers.
    Matches headers like "Jul '25", "Aug '25", etc.
    """
    current_year_suffix = str(datetime.now().year % 100)
    headers = soup.find_all("th")
    month_map = {}
    seen = set()

    pattern = re.compile(r"([A-Za-z]{3})\s*'?" + re.escape(current_year_suffix))

    month_abbr_to_num = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    for i, th in enumerate(headers):
        text = th.get_text(strip=True)
        match = pattern.search(text)
        if match:
            abbr = match.group(1).title()
            if abbr in month_abbr_to_num and abbr not in seen:
                month_index = i // 5
                month_map[month_index] = month_abbr_to_num[abbr]
                seen.add(abbr)

    return month_map


def parse_calendar_events(html: str) -> dict:
    """
    Parses calendar HTML and extracts working days grouped by month number.
    Does NOT hardcode month names. Handles unwrapped <td> rows (like for 31st).
    """
    soup = BeautifulSoup(html, "html.parser")
    month_map = extract_month_map(soup)
    columns_per_month = 5
    working_days_by_month = {num: [] for num in month_map.values()}

    table = soup.find("table")
    if not table:
        raise ValueError("No <table> found in calendar HTML")

    all_tds = table.find_all("td", recursive=True)

    if len(all_tds) % columns_per_month != 0:
        print("⚠️ Warning: td count not divisible by columns_per_month x months")

    row_chunks = [
        all_tds[i : i + columns_per_month * len(month_map)]
        for i in range(0, len(all_tds), columns_per_month * len(month_map))
    ]

    for row in row_chunks:
        for m_index, month_num in month_map.items():
            base = m_index * columns_per_month
            if base + 3 >= len(row):
                continue

            try:
                date = row[base].get_text(strip=True)
                day = row[base + 1].get_text(strip=True)
                event = row[base + 2].get_text(strip=True)
                do = row[base + 3].get_text(strip=True)
            except IndexError:
                continue  # Not enough cells in this row

            if do == "-" or not date or not do.isdigit():
                continue

            try:
                date_int = int(date)
                do_int = int(do)
            except ValueError:
                continue

            working_days_by_month[month_num].append(
                {
                    "date": f"{datetime.now().year}-{month_num:02d}-{date_int:02d}",
                    "day": day,
                    "event": event,
                    "do": do_int,
                }
            )

    return working_days_by_month
