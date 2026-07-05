"""Populate the database with demo notices and events (some with posters).

Re-runnable: it wipes existing rows first. Usage:
    PYTHONPATH=. uv run python scripts/seed_demo.py
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import text

from app.db.session import AsyncSessionLocal, engine
from app.models.event import EventCategory, TargetYear
from app.models.notice import NoticeCategory
from app.models.user import UserRole
from app.services import event as event_service
from app.services import notice as notice_service
from app.services import user as user_service

C = NoticeCategory
E = EventCategory
Y = TargetYear


def poster(seed: str) -> str:
    return f"https://picsum.photos/seed/{seed}/800/500"


# (title, content, category, image)
NOTICES = [
    ("Central library closed on Aug 15", "The central library will be closed on Aug 15 for annual maintenance. Hall reading rooms remain open 24x7.", C.general, None),
    ("Mid-sem exam schedule released", "The mid-semester examination schedule for Autumn 2026 is now available on the ERP. Check your slots and report 30 minutes early.", C.examination, poster("exam")),
    ("Hostel water supply cut - RK Hall", "Water supply in RK Hall will be interrupted on Jul 6 from 10am to 2pm for tank cleaning.", C.hostel, None),
    ("MCM scholarship applications open", "Merit-cum-Means scholarship applications for this semester are open until Jul 31 on the ERP portal.", C.scholarship, poster("scholar")),
    ("New PhD coursework guidelines", "Revised PhD coursework and credit guidelines are effective this semester. Read the full circular attached.", C.academic, None),
]

# (title, desc, category, venue, organizer, start, end, image, registration_url, target_year)
EVENTS = [
    ("Robotics Workshop - build a line follower", "Hands-on session where teams assemble and program a line-following robot from scratch. Components provided; bring a laptop.", E.workshop, "Nalanda C3", "Robotics Club", (2026, 8, 5, 10), (2026, 8, 5, 13), poster("robot"), "https://forms.gle/robotics-workshop", Y.y1),
    ("TCS Placement Talk", "Pre-placement talk covering roles, CTC bands and the interview process for the 2027 batch.", E.placement, "NR Auditorium", "Career Development Centre", (2026, 7, 10, 15), (2026, 7, 10, 17), None, "https://forms.gle/tcs-ppt", Y.y4),
    ("Kshitij Fest Kickoff", "Opening ceremony of Asia's largest techno-management fest with keynote speakers and a light show.", E.fest, "Gymkhana Grounds", "Kshitij Team", (2026, 8, 1, 18), (2026, 8, 1, 21), poster("kshitij"), None, Y.all),
    ("Guest Lecture: Frontiers in AI", "Distinguished lecture on large models and their societal impact, followed by an open Q&A.", E.talk, "Kalidas Auditorium", "Dept. of CSE", (2026, 7, 18, 16), (2026, 7, 18, 18), poster("ai"), "https://forms.gle/ai-lecture", Y.all),
    ("Inter-hall Football Final", "The championship decider between LBS and RK halls. Come cheer for your hall!", E.sports, "Tata Sports Complex", "Sports Board", (2026, 7, 25, 17), (2026, 7, 25, 19), None, None, Y.all),
]


def dt(y: int, mo: int, d: int, h: int) -> datetime:
    return datetime(y, mo, d, h, tzinfo=timezone.utc)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE users, notices, events CASCADE"))
        await session.commit()

        admin = await user_service.create_user(
            session, name="Asha Rao", email="asha@kgp.ac.in",
            password="adminpass123", role=UserRole.admin,
        )
        await user_service.create_user(
            session, name="Rahul Verma", email="rahul@kgp.ac.in",
            password="adminpass123", role=UserRole.admin,
        )

        for title, content, category, image in NOTICES:
            await notice_service.create_notice(
                session, title=title, content=content, category=category,
                poster=admin, image_url=image,
            )

        for title, desc, cat, venue, org, start, end, image, reg, year in EVENTS:
            await event_service.create_event(
                session, title=title, description=desc, category=cat,
                venue=venue, organizer=org, image_url=image,
                registration_url=reg, target_year=year,
                start_time=dt(*start), end_time=dt(*end),
            )

    await engine.dispose()
    print(f"Seeded {len(NOTICES)} notices and {len(EVENTS)} events.")
    print("Admin logins (password 'adminpass123'):")
    print("  - asha@kgp.ac.in")
    print("  - rahul@kgp.ac.in")


if __name__ == "__main__":
    asyncio.run(main())
