"""Winter Arc reminder sender.

Picks the right message for the current slot (morning / evening / night),
rotates the wording by day, and pushes it to ntfy.sh. Standard library only.
"""

import json
import os
import sys
import urllib.request
from datetime import date, datetime, time, timedelta, timezone

# Morocco runs on UTC+1 all year except Ramadan, which falls after the
# deadline (Feb 2027), so a fixed offset is exact and avoids stale tzdata.
TZ = timezone(timedelta(hours=1), "Casablanca")
START = datetime.combine(date(2026, 10, 30), time(0, 0), TZ)
END = datetime.combine(date(2027, 1, 30), time(23, 59, 59), TZ)
TOTAL_DAYS = (END.date() - START.date()).days + 1  # 93

# The topic lives in the NTFY_TOPIC repo secret so it never appears in a public repo.
TOPIC = os.environ.get("NTFY_TOPIC", "")
PAGE_URL = os.environ.get("PAGE_URL", "https://claude.ai/artifact/SFb7AenMS47rDyjGLBjjH6")

GOALS = (
    "BODY: 72kg -> 83kg\n"
    "MONEY: agency income covers every living cost\n"
    "TRADING: 200k funded capital + 3-4% return"
)
WHY = "WHY: your family. Every rep, every client, every trade is for them."

MORNING = [
    "Nobody is coming to do this for you. Write today's plan before you touch your phone again.",
    "Eat like it's your job. Work like rent is due. Trade like the account is your family's.",
    "Comfort is the enemy. Pick the three things that move the goals and do them first.",
    "Yesterday is gone, good or bad. Today gets judged on its own. Make it count.",
    "Motivation is gone by noon. Discipline is what's left. Plan the day now.",
    "Every meal is a step toward 83kg. Every call is a step toward a paying agency. Start walking.",
    "You said you'd do this. Prove it before breakfast: write the plan, then execute it.",
    "Your family doesn't need your excuses. They need you to finish. Plan the day.",
    "No zero days. One workout, one client move, one disciplined trading session. Minimum.",
    "The deadline doesn't move. Your effort is the only thing you control. Plan it.",
    "Soft days make a hard life. Hard days make an easy one. Choose now.",
    "Wake up, eat big, work hard, trade clean. Write down exactly how.",
]

EVENING = [
    "Check-in. Did you eat enough today? If not, fix it before you sleep.",
    "Half the day is gone. Did you do the hard thing yet, or are you still dodging it?",
    "Check-in. One client action today: done or not? If not, do it in the next hour.",
    "Be honest. Would your family be proud of how you spent today so far?",
    "Trading check: did you follow your rules, or did you gamble? No lies.",
    "Still time to save the day. Pick the one task you've been avoiding and finish it.",
    "Have you trained today? If not, the gym is still open. Go.",
    "Check-in. Scrolling is stealing your goals. Put the phone down and work.",
    "The day isn't over. Eat a real meal and finish one more thing for the agency.",
    "You don't need to feel like it. You need to do it. What's left on today's plan?",
]

NIGHT = [
    "Night review. What did you win today? What did you dodge? Write both down.",
    "Lights out soon. Muscle grows in sleep. Eat your last meal and go to bed.",
    "Review: food, work, trading. Score each one honestly out of 10.",
    "Did today get you closer to the goals, or did you just stay busy? Answer it.",
    "No screen marathons tonight. Plan tomorrow's first move, then sleep.",
    "If today was weak, don't hide from it. Name the reason and fix it tomorrow.",
    "Your family is the reason. Did today's version of you earn that? Review and rest.",
    "Night review. One thing to keep doing, one thing to cut. Then sleep.",
    "The work you did today compounds. So does the work you skipped. Review it.",
    "Close the day like a professional. Review, plan tomorrow, sleep 8 hours.",
]


def progress(now):
    day_n = (now.date() - START.date()).days + 1
    days_left = (END.date() - now.date()).days + 1
    pct = (now - START).total_seconds() / (END - START).total_seconds() * 100
    return day_n, days_left, max(0.0, min(100.0, pct))


def slot_from_hour(now):
    if now.hour < 13:
        return "morning"
    if now.hour < 20:
        return "evening"
    return "night"


def build(slot, now):
    day_n, days_left, pct = progress(now)
    status = f"Day {day_n}/{TOTAL_DAYS} · {days_left} days left · {pct:.0f}% of the time gone"
    i = day_n - 1
    if slot == "morning":
        title = f"WINTER ARC · {days_left} DAYS LEFT"
        body = f"{MORNING[i % len(MORNING)]}\n\n{GOALS}\n\n{WHY}\n\n{status}"
        return title, body, 4, ["snowflake", "dart"]
    if slot == "evening":
        title = "18:00 CHECK-IN"
        body = f"{EVENING[i % len(EVENING)]}\n\n{status}"
        return title, body, 4, ["hourglass_flowing_sand"]
    title = "NIGHT REVIEW"
    body = f"{NIGHT[i % len(NIGHT)]}\n\n{status}"
    return title, body, 3, ["crescent_moon"]


def main():
    now = datetime.now(TZ)
    if now > END or now.date() < START.date():
        print("Outside the Winter Arc window; nothing sent.")
        return
    if not TOPIC and "--dry-run" not in sys.argv:
        sys.exit("NTFY_TOPIC is not set. Add it as a repository secret.")
    slot = os.environ.get("SLOT") or slot_from_hour(now)
    if slot not in ("morning", "evening", "night"):
        slot = slot_from_hour(now)
    title, body, priority, tags = build(slot, now)
    payload = {"topic": TOPIC, "title": title, "message": body,
               "priority": priority, "tags": tags}
    if PAGE_URL:
        payload["click"] = PAGE_URL
    if "--dry-run" in sys.argv:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    req = urllib.request.Request(
        "https://ntfy.sh/", data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"Sent {slot} reminder: HTTP {resp.status}")


if __name__ == "__main__":
    main()
