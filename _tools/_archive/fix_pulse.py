import re, os
dst = os.path.expanduser("~/Desktop/Pitches Master/Schools/UWCSEA/NoFilter-UWCSEA-PartTwo.html")
d = open(dst, encoding="utf-8").read()

bad = [
 '.contact-card .deets-interview .moneyfm-logo{transform-origin:center;animation:nfLogoPulse 1.8s ease-in-out infinite;}',
 '.contact-card .deets-interview .moneyfm-logo{animation:none;}',
 '@keyframes nfLogoPulse{0%,100%{transform:scale(1);opacity:1;}',
 '.contact-card .deets-interview.pulse-done .moneyfm-logo{animation:none;transition:transform .25s ease;}',
 '.contact-card .deets-interview.pulse-done .moneyfm-link:hover .moneyfm-logo{animation:nfLogoPulse 1.8s ease-in-out infinite;}',
]
for b in bad:
    d = d.replace(b + "\n", "")
    d = d.replace(b, "")

# also remove any orphaned keyframe fragment lines
d = re.sub(r'@keyframes nfLogoPulse\{0%,100%\{[^\n]*\n?', '', d)
d = re.sub(r'50%\{transform:scale\(1\.22\);opacity:0\.78;\}\}\n?', '', d)

block = """.contact-card .deets-interview .moneyfm-logo{transform-origin:center;animation:nfLogoPulse 1.8s ease-in-out infinite;}
@keyframes nfLogoPulse{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.22);opacity:0.78;}}
.contact-card .deets-interview.pulse-done .moneyfm-logo{animation:none;transition:transform .25s ease;}
.contact-card .deets-interview.pulse-done .moneyfm-link:hover .moneyfm-logo{animation:nfLogoPulse 1.8s ease-in-out infinite;}
"""
d = d.replace("</style>", "\n/* Money FM pulse (corrected) */\n" + block + "</style>", 1)
open(dst, "w", encoding="utf-8").write(d)
print("Pulse CSS rewritten cleanly.")
