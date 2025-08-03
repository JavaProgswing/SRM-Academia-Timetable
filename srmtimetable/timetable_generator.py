from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from itertools import islice
from .utils import fig_to_base64


# Individual D/O (compact) schedule
def draw_schedule_compact(schedule, ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(schedule))
    ax.axis("off")

    for idx, slot in enumerate(reversed(schedule)):
        y = idx
        course = slot["Course"]
        label = f'{slot["StartTime"]} - {slot["EndTime"]}'
        title = course["Title"][:50] + ("..." if len(course["Title"]) > 50 else "")
        room = course["Room"]
        ctype = course.get("Course Type", "")
        content = f"{label}\n{title}\n({room})"
        # color = "#90ee90" if ctype == "Lab Based Theory" else "#fce570"
        color = "#A2D2FF" if ctype == "Lab Based Theory" else "#FFC8DD"

        ax.add_patch(
            Rectangle(
                (0.05, y), 0.9, 0.9, facecolor=color, edgecolor="black", lw=1, alpha=0.9
            )
        )
        ax.text(
            0.5, y + 0.45, content, ha="center", va="center", fontsize=7.5, wrap=True
        )


# Time slots for combined view
time_slots = [
    "08:00",
    "08:50",
    "09:45",
    "10:40",
    "11:35",
    "12:30",
    "01:25",
    "02:20",
    "03:10",
    "04:00",
]


def draw_schedule_combined(do, schedule, ax):
    ax.set_title(f"D/O {do}", fontsize=10, pad=10)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(time_slots))
    ax.axis("off")

    # Map start times to schedule entries
    slot_map = {slot["StartTime"]: slot for slot in schedule}

    for idx, time in enumerate(reversed(time_slots)):  # Bottom to top
        y = idx
        slot = slot_map.get(time)

        if slot:
            course = slot["Course"]
            label = f'{slot["StartTime"]} - {slot["EndTime"]}'
            title = course["Title"][:30] + ("..." if len(course["Title"]) > 30 else "")
            room = course["Room"]
            ctype = course.get("Course Type", "")
            content = f"{label}\n{title}\n({room})"
            color = "#A2D2FF" if ctype == "Lab Based Theory" else "#FFC8DD"
            alpha = 0.9
        else:
            content = ""  # Transparent empty box
            color = "#FFFFFF"
            alpha = 0.05

        ax.add_patch(
            Rectangle(
                (0.05, y),
                0.9,
                0.9,
                facecolor=color,
                edgecolor="black",
                lw=1,
                alpha=alpha,
            )
        )
        if content:
            ax.text(
                0.5,
                y + 0.45,
                content,
                ha="center",
                va="center",
                fontsize=7.5,
                wrap=True,
            )


# Main method to return base64 timetables as JSON
def generate_timetables_base64(date_to_schedule, date_to_do):
    result = {"individual": [], "combined": None}

    # Generate individual images per D/O
    done_dos = set()
    for date, schedule in date_to_schedule.items():
        do = date_to_do[date]
        if do in done_dos:
            continue
        done_dos.add(do)
        fig, ax = plt.subplots(figsize=(5, max(5, len(schedule))))
        draw_schedule_compact(schedule, ax)
        img_b64 = fig_to_base64(fig)
        plt.close(fig)

        result["individual"].append(
            {
                "do": do,
                "date": date,
                "day": datetime.strptime(date, "%Y-%m-%d").strftime("%A"),
                "image": img_b64,
            }
        )

    # Generate combined view for first 5 D/Os in order
    combined_days = list(islice(date_to_schedule.items(), 5))
    if combined_days:
        if len(combined_days) == 1:
            fig, axs = plt.subplots(1, 1, figsize=(4, 9))
            axs = [axs]
        else:
            fig, axs = plt.subplots(
                1, len(combined_days), figsize=(4 * len(combined_days), 9)
            )

        for ax, (date, schedule) in zip(axs, combined_days):
            do = date_to_do[date]
            draw_schedule_combined(do, schedule, ax)

        result["combined"] = fig_to_base64(fig)
        plt.close(fig)

    return result


def generate(timetable_data, calendar_data):
    # Map DayOrder to schedule
    dayorder_map = {entry["DayOrder"]: entry["Schedule"] for entry in timetable_data}

    # Map each date to its corresponding DayOrder using calendar data
    date_to_schedule = {}
    date_to_do = {}
    do_to_date = {}
    for month in calendar_data.values():
        for day in month:
            date = day["date"]
            do = day["do"]
            if do in dayorder_map:
                slots = [slot for slot in dayorder_map[do] if slot["Course"]]
                if slots:
                    date_to_schedule[date] = slots
                    date_to_do[date] = do
                    do_to_date[do] = date

    return generate_timetables_base64(date_to_schedule, date_to_do)
