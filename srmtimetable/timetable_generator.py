from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from .utils import fig_to_base64
from collections import OrderedDict
from itertools import islice


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


def generate_timetables_base64(dayorder_data):
    result = {"individual": [], "combined": None}

    # -------- Individual timetables --------
    for do, data in dayorder_data.items():
        schedule = data["schedule"]

        fig, ax = plt.subplots(figsize=(5, max(5, len(schedule))))
        draw_schedule_compact(schedule, ax)

        result["individual"].append(
            {
                "do": do,
                "date": data.get("date"),  # optional
                "day": (
                    datetime.strptime(data["date"], "%Y-%m-%d").strftime("%A")
                    if data.get("date")
                    else None
                ),
                "image": fig_to_base64(fig),
            }
        )

        plt.close(fig)

    # -------- Combined timetable (D/O 1–5) --------
    combined_items = list(islice(dayorder_data.items(), 5))

    if combined_items:
        fig, axs = plt.subplots(
            1, len(combined_items), figsize=(4 * len(combined_items), 9)
        )

        if len(combined_items) == 1:
            axs = [axs]

        for ax, (do, data) in zip(axs, combined_items):
            draw_schedule_combined(do, data["schedule"], ax)

        result["combined"] = fig_to_base64(fig)
        plt.close(fig)

    return result


def generate(timetable_data):
    """
    timetable_data: list of entries like
    {
        "DayOrder": 1,
        "Schedule": [...]
    }
    """

    # Filter empty slots and map DayOrder → schedule
    dayorder_map = {
        entry["DayOrder"]: [slot for slot in entry["Schedule"] if slot.get("Course")]
        for entry in timetable_data
        if entry.get("Schedule")
    }

    # Sort DayOrders numerically (1,2,3,4,5...)
    ordered = OrderedDict(
        (do, {"schedule": sched}) for do, sched in sorted(dayorder_map.items())
    )

    return generate_timetables_base64(ordered)
