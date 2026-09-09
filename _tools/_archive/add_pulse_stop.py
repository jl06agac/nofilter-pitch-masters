import os
dst = os.path.expanduser("~/Desktop/Pitches Master/Schools/UWCSEA/NoFilter-UWCSEA-PartTwo.html")
d = open(dst, encoding="utf-8").read()
if "pulse-done-timer" in d:
    print("Already added."); raise SystemExit
js = """<script id="pulse-done-timer">
setTimeout(function(){
  var els=document.querySelectorAll('.deets-interview');
  for(var i=0;i<els.length;i++){els[i].classList.add('pulse-done');}
}, 30000);
</script>
"""
d = d.replace("</body>", js + "</body>", 1)
open(dst, "w", encoding="utf-8").write(d)
print("30s auto-stop JS added before </body>.")
