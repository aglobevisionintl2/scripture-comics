import csv, sqlite3, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.comments import Comment
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
db = sqlite3.connect(sys.argv[2]); meta = dict(db.execute("SELECT key,value FROM source"))
wb = Workbook(); ws = wb.active; ws.title = "Catalog"
F = Font(name="Arial", size=10); B = Font(name="Arial", size=10, bold=True)
ws["A1"] = "Scripture words per comic page"; ws["A1"].font = B
ws["C1"] = 50; ws["C1"].font = Font(name="Arial", size=10, color="0000FF"); ws["C1"].fill = PatternFill("solid", fgColor="FFFF00")
ws["C1"].comment = Comment("Assumption: selected verbatim WEB words per page, art-forward cinematic layout. Edit to re-estimate.", "Claude")
ws["D1"] = "Minimum story pages"; ws["D1"].font = B
ws["G1"] = "Maximum story pages"; ws["G1"].font = B
ws["I1"] = 12; ws["I1"].font = Font(name="Arial", size=10, color="0000FF"); ws["I1"].fill = PatternFill("solid", fgColor="FFFF00")
ws["J1"] = "Share of passage words kept"; ws["J1"].font = B
ws["L1"] = 0.5; ws["L1"].number_format = "0%"; ws["L1"].font = Font(name="Arial", size=10, color="0000FF"); ws["L1"].fill = PatternFill("solid", fgColor="FFFF00")
ws["L1"].comment = Comment("Target share of each passage kept as verbatim key verses. User decision 2026-11-03: limit words to the most important verses.", "Claude")
ws["I1"].comment = Comment("Cap per issue. Long passages are reduced to their most important verses to fit.", "Claude")
ws["F1"] = 6; ws["F1"].font = Font(name="Arial", size=10, color="0000FF"); ws["F1"].fill = PatternFill("solid", fgColor="FFFF00")
hdr = ["Issue","Series","Title","Reference","Verses","Full-passage words","Selected-word budget","Est. story pages","Format","Main characters","Supporting characters","Locations","Popularity","Rating / decision note","Status"]
for i,h in enumerate(hdr,1):
    c = ws.cell(3,i,h); c.font = Font(name="Arial", size=10, bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="5A3E2B")
keys = ["issue","series","title","reference","verses","words","BUDGET",None,"format","main_characters","supporting_characters","locations","popularity","rating_or_decision_note"]
for r,row in enumerate(rows,4):
    for i,k in enumerate(keys,1):
        if k == "BUDGET":
            v = f"=MIN(ROUND(F{r}*$L$1,0),$I$1*$C$1)"
        elif k is None:
            v = f"=MAX($F$1,ROUNDUP(G{r}/$C$1,0))"
        else:
            v = row[k]; v = int(v) if k in ("issue","verses","words") else v
        c = ws.cell(r,i,v); c.font = F; c.alignment = Alignment(vertical="top", wrap_text=i>=9)
    ws.cell(r,15,"Verse selection: not started").font = F
last = 3+len(rows); t = last+1
ws.cell(t,4,"Total").font = B
for col in "EFGH":
    c = ws[f"{col}{t}"]; c.value = f"=SUM({col}4:{col}{last})"; c.font = B
for col,w in zip("ABCDEFGHIJKLMNO",[7,12,38,24,8,10,10,10,13,34,34,30,12,40,24]): ws.column_dimensions[col].width = w
ws.freeze_panes = "D4"; ws.auto_filter.ref = f"A3:O{last}"
s = wb.create_sheet("Source")
for i,(k,v) in enumerate(meta.items(),1):
    s.cell(i,1,k).font = B; s.cell(i,2,v).font = F
s.column_dimensions["A"].width = 18; s.column_dimensions["B"].width = 80
wb.save(sys.argv[3])
