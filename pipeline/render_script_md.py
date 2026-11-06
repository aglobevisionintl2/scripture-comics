"""Render an issue script JSON as readable markdown. Usage: python3 render_script_md.py script.json out.md"""
import json, sys
sc = json.load(open(sys.argv[1], encoding="utf-8"))
L = [f"# Issue {sc['issue']}: {sc['title']}", f"**{sc['opening_reference']}**", "",
     "Lettering key: CAPTION = narration box · GOD = glowing borderless text, no speaker drawn · SPEECH = speech bubble", ""]
for pg in sc["pages"]:
    L += [f"## Page {pg['page']} ({pg['verses']})", f"_Layout: {pg['layout']}_", ""]
    for pn in pg["panels"]:
        who = ", ".join(pn["characters"]) or "no characters"
        L.append(f"**Panel {pn['panel']}**: {pn['camera']}; {who}. {pn['art']}")
        for t in pn["text"]:
            L.append(f"- {t['type'].upper()} ({sc['book'].title()} {t['ref']}): {t['text']}")
        L.append("")
m = sc["moral"]
L += [f"## {m['heading']} (own page, framed, after the last story page)", "", m["paragraph"], "",
      "## Coloring pages (single-sided, after the Moral page)"] + [f"- {c['subject']}" for c in sc["coloring_pages"]]
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(L) + "\n")
