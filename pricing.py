"""
Single source of truth for the proposal numbers.
Edit here, then run:  python3 build.py
"""

# ── Pending vendor quote ────────────────────────────────────────────────
# Set to a number (e.g. 38500) once OTI's quote lands. None = shows "Quote in progress".
OTI_REMOVAL_RESET = {
    "A": round(50499.38 * 1.15, 2),  # OTI estimate 9/28: removal 8 techs × $95 × 30 hrs $22,800 + reset $22,800 + packing $4,500 + tax
    "B": round(50499.38 * 1.15, 2),  # +15% Cocoon coordination markup
}

SECURITY_DEPOSIT = 0.25  # refundable, both houses
PARKING_EST = 2500       # if required · whole booking · final cost set by the Mayor's Office

# ── CASA JOY (Cocoon published rates, as quoted to Mia on Sep 8) ────────
JOY = {
    "load_hr": 1800, "live_hr": 2880, "hours": 12,
    "sm_hr": 120, "sm_hours": 14,
    "clean": 400,
    "cocoon_day": 15000,  # flat space rental for Cocoon-only prep/reset days
    "floor_protection": 9800,  # ESTIMATE · 2 rounds · ~$3,500/round cost (Layout Pros unit prices scaled to 4 floors + stairs) +40% (no vendor quote)
}

JOY_DAYS = {
    "A": [
        ("Sun", "Nov 15", "Cocoon prep day 1/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Mon", "Nov 16", "Cocoon prep day 2/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Tue", "Nov 17", "Cocoon prep day 3/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Wed", "Nov 18", "Load-in", "Your production team on site", "load"),
        ("Thu", "Nov 19", "Load-in", "Your production team on site", "load"),
        ("Fri", "Nov 20", "Live", "Content shoot · evening creator preview (30–40)", "live"),
        ("Sat", "Nov 21", "Live", "Open to the public · timed entry", "live"),
        ("Sun", "Nov 22", "Load-out", "Your production team strikes", "load"),
        ("Mon", "Nov 23", "Cocoon reset day 1/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
        ("Tue", "Nov 24", "Cocoon reset day 2/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
        ("Wed", "Nov 25", "Cocoon reset day 3/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
    ],
    "B": [
        ("Sat", "Nov 14", "Cocoon prep day 1/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Sun", "Nov 15", "Cocoon prep day 2/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Mon", "Nov 16", "Cocoon prep day 3/3", "Furniture & art removal by our art handlers · no client access", "cocoon"),
        ("Tue", "Nov 17", "Load-in", "Your production team on site", "load"),
        ("Wed", "Nov 18", "Load-in", "Your production team on site", "load"),
        ("Thu", "Nov 19", "Load-in", "Your production team on site", "load"),
        ("Fri", "Nov 20", "Live", "Content shoot · evening creator preview (30–40)", "live"),
        ("Sat", "Nov 21", "Live", "Open to the public · timed entry", "live"),
        ("Sun", "Nov 22", "Load-out", "Your production team strikes", "load"),
        ("Mon", "Nov 23", "Cocoon reset day 1/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
        ("Tue", "Nov 24", "Cocoon reset day 2/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
        ("Wed", "Nov 25", "Cocoon reset day 3/3", "Furniture & art reset by our art handlers · no client access", "cocoon"),
    ],
}

# ── CASA MAS (Floor 1 + Floor 2, events over 100 guests) ────────────────
MAS = {
    "day": 60750,          # 12-hour day, Floor 1 + Floor 2
    "hours": 12,
    "electrical": 607.50,  # per day, tie-in incl. distro + cable
    "deep_clean_floor": 675,  # per floor, per clean (ownership-approved vendor)
    "floors": 2,
    "garbage_load": 405,   # estimate 1 load/day, trued up post-event
    "floor_protection": 8548.80,
    "floor3_day": 10125,   # add-on per day on top of F1+F2
}

MAS_DAYS = {
    "A": [
        ("Wed", "Nov 18", "Load-in", "Floor protection installed at call time", "load"),
        ("Thu", "Nov 19", "Load-in", "Your production team on site", "load"),
        ("Fri", "Nov 20", "Live", "Content shoot · evening creator preview (30–40)", "live"),
        ("Sat", "Nov 21", "Live", "Open to the public · timed entry", "live"),
        ("Sun", "Nov 22", "Load-out", "Strike · 3 hrs next-morning load-out at no charge", "load"),
    ],
    "B": [
        ("Tue", "Nov 17", "Load-in", "Floor protection installed at call time", "load"),
        ("Wed", "Nov 18", "Load-in", "Your production team on site", "load"),
        ("Thu", "Nov 19", "Load-in", "Your production team on site", "load"),
        ("Fri", "Nov 20", "Live", "Content shoot · evening creator preview (30–40)", "live"),
        ("Sat", "Nov 21", "Live", "Open to the public · timed entry", "live"),
        ("Sun", "Nov 22", "Load-out", "Strike · 3 hrs next-morning load-out at no charge", "load"),
    ],
}


def joy_lines(opt):
    days = JOY_DAYS[opt]
    n_load = sum(1 for d in days if d[4] == "load")
    n_live = sum(1 for d in days if d[4] == "live")
    n_coc = sum(1 for d in days if d[4] == "cocoon")
    n_all = len(days)
    n_clean = 1 + n_load + n_live + 1  # before check-in + after each client day + final after reset
    load_day = JOY["load_hr"] * JOY["hours"]
    live_day = JOY["live_hr"] * JOY["hours"]
    sm_day = JOY["sm_hr"] * JOY["sm_hours"]
    lines = [
        ("Load-in & load-out days", f"12-hour day · ${JOY['load_hr']:,}/hr", n_load, load_day),
        ("Live event days", f"12-hour day · ${JOY['live_hr']:,}/hr", n_live, live_day),
        ("Cocoon prep + reset days", "3 days to clear + 3 days to reset · house held, no client access · reduced flat day rate", n_coc, JOY["cocoon_day"]),
        ("On-site Studio Manager", f"Every day of the run · 14 hrs · ${JOY['sm_hr']}/hr", n_all, sm_day),
        ("Cleaning services", "Before check-in · after every day's check-out · final clean after reset · trash removal included", n_clean, JOY["clean"]),
        ("Floor & wall protection", "Oak floors, entry & stairs on the activation floors · installed and removed by our approved vendor, 2 rounds (estimate)", 1, JOY["floor_protection"]),
    ]
    subtotal = sum(q * r for _, _, q, r in lines)
    oti = OTI_REMOVAL_RESET[opt]
    return lines, subtotal, oti


def mas_lines(opt):
    days = MAS_DAYS[opt]
    n = len(days)
    lines = [
        ("Space rental · Floor 1 + Floor 2", "Exclusive use · 12-hour day · events over 100 guests", n, MAS["day"]),
        ("Electrical tie-in", "1,200A 3-phase camlock · distro box, cable & lunch boxes", n, MAS["electrical"]),
        ("Cleaning services · Floors 1 + 2", "Ownership-approved vendor · before check-in and after every day's check-out", n + 1, MAS["deep_clean_floor"] * MAS["floors"]),
        ("Garbage removal", "Private hauler · est. 1 load/day · trued up after the event", n, MAS["garbage_load"]),
        ("Floor & wall protection", "Marble + wood · installed and removed by the approved vendor, 2 rounds (estimate)", 1, MAS["floor_protection"]),
        ("On-site Cocoon Casa Manager", "Full run", 1, 0),
    ]
    total = sum(q * r for _, _, q, r in lines)
    return lines, total
