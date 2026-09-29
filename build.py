#!/usr/bin/env python3
"""Build index.html + download bundles. Run:  python3 build.py"""
import os, zipfile, datetime, html
from pricing import *

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def money(x):
    if abs(x - round(x)) < 0.005:
        return f"${round(x):,}"
    return f"${x:,.2f}"


def short(x):
    return f"${x/1000:,.1f}K".replace(".0K", "K")


# ── galleries ─────────────────────────────────────────────────────────
CAPTIONS = {
    # casa joy
    "cleared-01-parlor-staircase": "Art-deco staircase",
    "cleared-02-living-room-piano": "Living room · Level 2",
    "cleared-03-living-room-fireplace": "Living room fireplace",
    "cleared-04-garden-level-hall": "Garden-level room",
    "cleared-05-kitchen": "Kitchen · garden level",
    "cleared-06-kitchen-stone-wall": "Kitchen stone wall",
    "cleared-07-kitchen-painted-fridge": "Hand-painted kitchen detail",
    "cleared-08-hand-painted-wall": "Hand-painted walls",
    "cleared-09-garden": "English garden",
    "cleared-10-garden-trellis": "Garden trellis",
    "cleared-11-garden-vestibule": "Garden vestibule",
    "today-01-living-room-fireplace": "Living room · today",
    "today-02-living-room-piano": "Living room with piano · today",
    "today-03-dining-room": "Formal dining room · today",
    "today-04-library": "Library · today",
    "today-05-staircase": "Staircase",
    "today-06-library-fireplace": "Library fireplace",
    "today-07-primary-bedroom": "Primary bedroom · Level 3",
    "today-08-primary-bath": "Hammam-style bath · Level 3",
    "today-09-top-floor-studio-boh": "Top-floor studio · back-of-house",
    "activation-01-balloon-ceiling": "Brand activation · balloon ceiling",
    "activation-02-product-launch-racks": "Product launch · rails + styling",
    # casa mas
    "f1-01-entrance-hall": "Entrance hall · Floor 1",
    "f1-02-grand-staircase": "Grand staircase · Floor 1",
    "f1-03-parlor": "Parlor · Floor 1",
    "f1-04-dining-room": "Dining room · Floor 1",
    "f1-05-library": "Library · Floor 1",
    "f1-06-courtyard": "Indoor courtyard · Floor 1",
    "f1-08-kitchen": "Kitchen · Floor 1",
    "f2-01-black-white-room": "Black & White room · Floor 2",
    "f2-02-blue-room": "Front sitting room · Floor 2",
    "f2-03-hallway": "Hallway · Floor 2",
    "f3-01-jungle-room": "Jungle room · Floor 3 (add-on)",
    "f3-02-mosaic-room": "Mosaic room · Floor 3 (add-on)",
    "f4-01-ballroom": "Ballroom · Floor 4 (on request)",
}


def gallery(folder, prefix, feature_first=True):
    files = sorted(f for f in os.listdir(f"img/{folder}") if f.startswith(prefix))
    out = []
    for i, f in enumerate(files):
        key = f.rsplit(".", 1)[0]
        cap = CAPTIONS.get(key, key)
        cls = "photo feature" if (i == 0 and feature_first and len(files) > 4) else "photo"
        out.append(f'    <figure class="{cls}" style="margin:0"><img loading="lazy" src="img/{folder}/{f}" alt="{html.escape(cap)}" /><figcaption>{html.escape(cap)}</figcaption></figure>')
    return "\n".join(out)


# ── pricing panels ────────────────────────────────────────────────────
def calendar(days):
    cells = []
    for dow, date, what, desc, kind in days:
        cells.append(f'<div class="d {kind}"><div class="dow">{dow}</div><div class="date">{date}</div><div class="what">{what}</div><div class="desc">{desc}</div></div>')
    return f'<div class="cal days-{len(days)}">' + "".join(cells) + "</div>"


def table(rows, total_label, total_value, extra_rows="", plus_note=""):
    body = []
    for name, sub, q, r in rows:
        amt = "Included" if r == 0 else money(q * r)
        rate = "—" if r == 0 else money(r)
        body.append(f'<tr><td><strong>{name}</strong><span class="sub">{sub}</span></td><td class="qty">{q if r else "—"}</td><td class="amount">{rate}</td><td class="amount">{amt}</td></tr>')
    plus = f'<span class="plus">{plus_note}</span>' if plus_note else ""
    return f'''<div class="breakdown"><div class="scroll"><table>
<thead><tr><th>Line item</th><th class="qty">Qty</th><th class="amount">Rate</th><th class="amount">Amount</th></tr></thead>
<tbody>{"".join(body)}{extra_rows}
<tr class="total"><td><span class="label">{total_label}</span>{plus}</td><td></td><td></td><td class="amount">{total_value}</td></tr>
</tbody></table></div></div>'''


def common_rows():
    sec = ('<tr class="pending-row"><td><strong>Security &amp; crowd control · required</strong>'
           '<span class="sub">Licensed guards at the entrance and inside the house on live days · queue and headcount management · quoted once headcount, hours and flow are set</span></td>'
           '<td class="qty">—</td><td class="amount">—</td><td class="amount"><span class="pending">Quote pending</span></td></tr>')
    park = ('<tr class="pending-row"><td><strong>Parking permits · if required</strong>'
            f'<span class="sub">Handled by Cocoon · similar activations run about {money(PARKING_EST)} for the whole booking · final cost set by the Mayor\'s Office once the permitted area is submitted</span></td>'
            f'<td class="qty">—</td><td class="amount">—</td><td class="amount"><span class="pending">Est. {money(PARKING_EST)}</span></td></tr>')
    return sec + park


def joy_panel(opt):
    lines, sub, oti = joy_lines(opt)
    days = JOY_DAYS[opt]
    n_client = sum(1 for d in days if d[4] != "cocoon")
    if oti is None:
        extra = ('<tr class="pending-row"><td><strong>Furniture &amp; art removal, storage and reset</strong>'
                 '<span class="sub">Specialist art handlers · on the Cocoon prep and reset days</span></td>'
                 '<td class="qty">1</td><td class="amount">—</td><td class="amount"><span class="pending">Quote pending</span></td></tr>')
        total_label = f"Option {opt} · Casa Joy · venue total"
        total_value = money(sub)
        plus = "+ furniture &amp; art removal / reset, security &amp; crowd control, parking permits if required"
        dep = f"50% deposit on signing: {money(sub/2)} · refundable security deposit (25%): {money(sub*SECURITY_DEPOSIT)} · both adjust once furniture handling is added"
    else:
        extra = (f'<tr><td><strong>Furniture &amp; art removal, storage and reset</strong><span class="sub">Specialist fine-art handlers · 8 technicians × 3 days to clear + 3 days to reset · packing materials and storage of all removed pieces included</span></td>'
                 f'<td class="qty">1</td><td class="amount">{money(oti)}</td><td class="amount">{money(oti)}</td></tr>')
        total_label = f"Option {opt} · Casa Joy · venue total"
        total_value = money(sub + oti)
        plus = "+ security &amp; crowd control, parking permits if required"
        dep = f"50% deposit on signing: {money((sub+oti)/2)} · refundable security deposit (25%): {money((sub+oti)*SECURITY_DEPOSIT)}"
    intro = (f'<p class="body" style="color:var(--ink-soft); margin: 0 0 6px;"><strong style="color:var(--ink)">Option {opt}</strong> · '
             f'{n_client} client days + {len(days)-n_client} Cocoon-only days = {len(days)} days on the calendar ({days[0][1]} – {days[-1][1]}).</p>')
    return intro + calendar(days) + table(lines, total_label, total_value, extra + common_rows(), plus) + \
        f'<p class="caption" style="margin-top:14px;">{dep} · balance 30 days before load-in · wire/ACH, or card +3.7%</p>'


def mas_panel(opt):
    lines, total = mas_lines(opt)
    days = MAS_DAYS[opt]
    intro = (f'<p class="body" style="color:var(--ink-soft); margin: 0 0 6px;"><strong style="color:var(--ink)">Option {opt}</strong> · '
             f'{len(days)} days on the calendar ({days[0][1]} – {days[-1][1]}) · no prep or reset days needed.</p>')
    return intro + calendar(days) + table(lines, f"Option {opt} · Casa Mas · venue total", money(total), common_rows(), "+ security &amp; crowd control, parking permits if required") + \
        f'<p class="caption" style="margin-top:14px;">50% deposit on signing: {money(total/2)} · refundable security deposit (25%): {money(total*SECURITY_DEPOSIT)} · balance 30 days before load-in · wire/ACH, or card +3.7%</p>'


# ── Q&A matrix ────────────────────────────────────────────────────────
jd = JOY["load_hr"] * JOY["hours"]; jl = JOY["live_hr"] * JOY["hours"]
MAS_HR = MAS["day"] / MAS["hours"]; MAS_OT = MAS_HR * 1.5
MATRIX = [
    ("Base rental, what a “day” is, and overtime",
     f"<strong>12-hour day.</strong> Load-in/out {money(JOY['load_hr'])}/hr ({money(jd)}/day); live days {money(JOY['live_hr'])}/hr ({money(jl)}/day). The Cocoon-only prep and reset days, when your team isn't in the house, are charged at a reduced flat {money(JOY['cocoon_day'])}/day. Overtime is 1.5× in 1-hour blocks: {money(JOY['load_hr']*1.5)}/hr on load days, {money(JOY['live_hr']*1.5)}/hr on live days.",
     f"<strong>12-hour day,</strong> Floors 1 + 2 exclusive: {money(MAS['day'])}/day ({money(MAS_HR)}/hr). Overtime is {money(MAS_OT)}/hr in 1-hour blocks. Vehicles on 63rd Street 8 am – 10 pm; the first 3 hours of next-morning load-out are free."),
    ("In-house staffing you're required to buy",
     "<strong>Cocoon Studio Manager,</strong> on site every day and included above. <strong>Security and crowd control are required</strong> at the entrance and inside the house on the live days; we'll quote them once headcount, hours and flow are confirmed. Fire guard, porters, bathroom attendants and coat check aren't required by the venue, and we can supply any of them through Super Concierge.",
     "<strong>Cocoon Casa Manager,</strong> included for the full run. <strong>Security and crowd control are required</strong> at the entrance and inside the house on the live days: licensed guards named on the COI, quoted once headcount, hours and flow are confirmed. Fire guard, porters, attendants and coat check aren't required by the venue."),
    ("Cleaning during and after, trash and garbage",
     "A clean before check-in, after every day's check-out and a final clean after the reset, with trash removal included. All priced above.",
     f"A clean before check-in and after every day's check-out by ownership's approved vendor ({money(MAS['deep_clean_floor'])}/floor per clean, included). Garbage by private hauler at {money(MAS['garbage_load'])}/load, estimated at one a day and trued up after the event. Food waste has to leave the building nightly."),
    ("Removing and storing existing furniture and art",
     "<strong>Required on the activation floors.</strong> A team of 8 fine-art handlers clears the house over 3 Cocoon prep days and resets it over 3 days after your load-out, with all packing materials and secure storage of every removed piece. Their cost and the 6 days the house is held are both priced above.",
     "<strong>Not needed.</strong> The house is unfurnished, so there's no removal, storage or reset cost and no extra days."),
    ("Processing, admin, insurance and tax",
     "No admin fee. Wire/ACH is preferred; card payments carry a 3.7% processing fee. Space rental isn't subject to NY sales tax. COI with waiver of subrogation, naming Cocoon and the owner as additional insured, is due 2 pm two days before load-in. Every vendor on site needs one too.",
     "Same payment and tax terms. COI with waiver of subrogation, naming Cocoon and ownership as additional insured, with a <strong>minimum of $1M per occurrence plus $2M umbrella/excess</strong>. Every vendor on site needs a COI on the same terms."),
    ("Capacity by floor, private vs public",
     "Floor-by-floor numbers are being confirmed with the owner and will be shared before the walkthrough. The 30–40 creator preview fits comfortably. On the public day, timed entry keeps numbers inside the cap.",
     "Fire-code limits: <strong>176 on the ground floor, 205 across Floors 1 + 2</strong>, guests and staff combined. The creator preview fits easily. On the public day we'd plan for <strong>up to ~175 guests at a time</strong>, managed by timed entry."),
    ("ADA access and elevator, by floor",
     "Not ADA-compliant. Street-level entry, plus a small passenger elevator (3′ × 4′, 950 lb) that reaches every level and works for guests with limited mobility.",
     "Ramps at the front entrance and interior steps, plus a small passenger elevator connecting all floors. We'll go through any specific access needs at the scout."),
    ("Signage and façade branding",
     "Discreet, removable signage at the entrance is possible with the owner's approval; nothing can be fixed into the façade. No venue fee; fabrication is on your side.",
     "<strong>No exterior branding, lights or lifts on 63rd Street,</strong> and the façade can't be filmed. Interior branding is fine with removable fixings only. Any exterior exception needs ownership's written approval."),
    ("Power, WiFi and house AV",
     "Standard house power across three panels, with no tie-in; we'd review high-draw lighting at the scout. WiFi runs about 320 Mbps down and 4 Mbps up. For QR shopping and content uploads we recommend a dedicated line, which we can quote. No house speakers, TV or projector. There's a grand piano on site.",
     "1,200A 3-phase camlock tie-in with a 600A distro box, lunch boxes and cable, included per day. WiFi is 300/240 Mbps with partial coverage; a dedicated line up to 10 Gbps is available. No house speakers, TV or projector."),
    ("Deposit schedule and cancellation",
     "50% on signing and 50% 30 days before load-in. A <strong>refundable security deposit of 25%</strong> of the booking total is due on signing and returned within 30 business days after the event. Cancelling within 12 months of the event can forfeit the full payment. Rescheduling carries a 50% fee on the space rental.",
     "50% on signing and 50% 30 days before load-in. A <strong>refundable security deposit of 25%</strong> of the booking total is due on signing and returned within 30 business days after the event. Same cancellation terms."),
]
matrix_html = "\n".join(
    f'<tr><th><span class="n">{i+1:02d}</span>{q}</th><td data-casa="Casa Joy">{a}</td><td data-casa="Casa Mas">{b}</td></tr>'
    for i, (q, a, b) in enumerate(MATRIX))


# ── bundles ───────────────────────────────────────────────────────────
os.makedirs("downloads", exist_ok=True)

def make_zip(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in entries:
            z.write(src, arc)
    return os.path.getsize(path)

joy_files = [(f"img/casa-joy/{f}", f"Casa Joy/{f}") for f in sorted(os.listdir("img/casa-joy"))]
mas_files = [(f"img/casa-mas/{f}", f"Casa Mas/{f}") for f in sorted(os.listdir("img/casa-mas"))]
plan = [("docs/Casa-Mas-Floor-Plans.pdf", "Casa Mas/Casa-Mas-Floor-Plans.pdf")]
sz = lambda b: f"{b/1_048_576:.0f} MB" if b > 1_048_576 else f"{b/1024:.0f} KB"
s_joy = make_zip("downloads/casa-joy-photos.zip", joy_files)
s_mas = make_zip("downloads/casa-mas-photos-and-plans.zip", mas_files + plan)
s_all = make_zip("downloads/cocoon-holiday-activation-all-assets.zip", joy_files + mas_files + plan)


# ── assemble ──────────────────────────────────────────────────────────
css = open("css_base.css").read() + open("css_extra.css").read()
_, joyA, _ = joy_lines("A"); _, joyB, _ = joy_lines("B")
_, masA = mas_lines("A"); _, masB = mas_lines("B")
oti = OTI_REMOVAL_RESET
repl = {
    "@@CSS@@": css,
    "@@TODAY@@": datetime.date.today().strftime("%B %-d, %Y"),
    "@@JOY_A_SHORT@@": short(joyA + (oti["A"] or 0)),
    "@@JOY_B_SHORT@@": short(joyB + (oti["B"] or 0)),
    "@@MAS_A_SHORT@@": short(masA),
    "@@MAS_B_SHORT@@": short(masB),
    "@@MAS_F3@@": money(MAS["floor3_day"]),
    "@@MAS_OT@@": money(MAS_OT),
    "@@GAL_JOY_CLEARED@@": gallery("casa-joy", "cleared"),
    "@@GAL_JOY_TODAY@@": gallery("casa-joy", "today"),
    "@@GAL_JOY_ACT@@": gallery("casa-joy", "activation", feature_first=False),
    "@@GAL_MAS_F1@@": gallery("casa-mas", "f1"),
    "@@GAL_MAS_F2@@": gallery("casa-mas", "f2", feature_first=False),
    "@@GAL_MAS_MORE@@": gallery("casa-mas", "f3", feature_first=False) + "\n" + gallery("casa-mas", "f4", feature_first=False),
    "@@JOY_A@@": joy_panel("A"), "@@JOY_B@@": joy_panel("B"),
    "@@MAS_A@@": mas_panel("A"), "@@MAS_B@@": mas_panel("B"),
    "@@MATRIX@@": matrix_html,
    "@@SZ_ALL@@": sz(s_all), "@@SZ_JOY@@": sz(s_joy), "@@SZ_MAS@@": sz(s_mas),
}
page = open("template.html").read()
for k, v in repl.items():
    page = page.replace(k, v)
assert "@@" not in page, [l for l in page.splitlines() if "@@" in l][:5]
open("index.html", "w").write(page)

print("Casa Joy  A:", money(joyA), "+ OTI" if oti["A"] is None else f"+ {money(oti['A'])} = {money(joyA+oti['A'])}")
print("Casa Joy  B:", money(joyB), "+ OTI" if oti["B"] is None else f"+ {money(oti['B'])} = {money(joyB+oti['B'])}")
print("Casa Mas  A:", money(masA))
print("Casa Mas  B:", money(masB))
print("zips:", sz(s_joy), sz(s_mas), sz(s_all), "| index.html", os.path.getsize("index.html")//1024, "KB")
