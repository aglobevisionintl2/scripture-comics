"""Genesis-Exodus issue catalog, checked against the WEB verse database.

Usage: python3 -I catalog_gen_exo.py data/web.sqlite data/catalog_gen_exo.csv
Fails loudly if ranges leave a gap, overlap, or point to verses that do not exist.
"""
import csv
import math
import sqlite3
import sys

WORDS_PER_PAGE = 75  # verbatim Scripture per comic page in cinematic realism (lettering-limited)

# (series, title, book, start, end, main characters, supporting, locations, popularity, rating note)
I = [
    ("Beginnings", "In the Beginning", "GEN", "1:1", "2:3", "God (non-figural)", "", "The deep; the heavens and the earth", "well-known", ""),
    ("Beginnings", "The Garden", "GEN", "2:4", "2:25", "Adam; Eve", "God (non-figural)", "Eden; the four rivers", "well-known", "Gen 2:25 nakedness: framing rule needed"),
    ("Beginnings", "The Serpent", "GEN", "3:1", "3:24", "Adam; Eve; the serpent", "God (non-figural); cherubim", "Eden", "well-known", "Gen 2:25 framing until 3:21"),
    ("Beginnings", "Cain and Abel", "GEN", "4:1", "4:26", "Cain; Abel", "Adam; Eve; Lamech; Adah; Zillah; Seth; Enosh", "Field; land of Nod; city of Enoch", "well-known", "Murder (4:8): restrained framing"),
    ("Beginnings", "From Adam to Noah", "GEN", "5:1", "5:32", "Adam; Seth; Enoch; Methuselah; Lamech; Noah", "Genealogy line", "", "lesser-known", "Genealogy: format decision"),
    ("Noah", "Noah 1: The Ark", "GEN", "6:1", "7:24", "Noah", "Noah's wife; Shem; Ham; Japheth; sons' wives; Nephilim", "Pre-flood earth; the ark", "well-known", "Mass death in flood: restrained"),
    ("Noah", "Noah 2: The Covenant of the Rainbow", "GEN", "8:1", "9:17", "Noah", "Family; raven; dove", "Mountains of Ararat", "well-known", ""),
    ("Noah", "Noah 3: Noah's Sons", "GEN", "9:18", "9:29", "Noah; Ham; Shem; Japheth", "Canaan", "Vineyard; tent", "lesser-known", "Drunkenness/nakedness 9:21-23: restrained"),
    ("Beginnings", "The Nations and Babel", "GEN", "10:1", "11:9", "Nimrod; builders of Babel", "Table of nations", "Shinar; Babel", "well-known", "Genealogy 10:1-32"),
    ("Beginnings", "From Shem to Abram", "GEN", "11:10", "11:32", "Terah; Abram; Sarai; Lot", "Shem line; Nahor; Haran; Milcah", "Ur of the Chaldees; Haran", "lesser-known", "Genealogy"),
    ("Abraham", "Abraham 1: The Call", "GEN", "12:1", "13:18", "Abram; Sarai; Lot", "Pharaoh; herdsmen", "Haran; Shechem; Bethel; Egypt; Negev; Mamre", "well-known", ""),
    ("Abraham", "Abraham 2: The War of the Kings", "GEN", "14:1", "14:24", "Abram; Lot; Melchizedek", "Chedorlaomer; king of Sodom; Aner; Eshcol; Mamre", "Valley of Siddim; Dan; Salem", "lesser-known", "Battle: restrained"),
    ("Abraham", "Abraham 3: Count the Stars", "GEN", "15:1", "15:21", "Abram", "God (non-figural); Eliezer", "Abram's tent at night", "lesser-known", ""),
    ("Abraham", "Abraham 4: Hagar", "GEN", "16:1", "16:16", "Hagar; Sarai; Abram", "Angel of Yahweh", "Spring on the way to Shur", "lesser-known", ""),
    ("Abraham", "Abraham 5: A New Name", "GEN", "17:1", "17:27", "Abraham; Sarah", "Ishmael", "Abraham's household", "lesser-known", "Circumcision: describe via text only"),
    ("Abraham", "Abraham 6: Three Visitors", "GEN", "18:1", "18:33", "Abraham; Sarah; three men", "", "Oaks of Mamre", "lesser-known", "Angel depiction decision"),
    ("Abraham", "Abraham 7: Sodom and Gomorrah", "GEN", "19:1", "19:38", "Lot; two angels", "Lot's wife; daughters; men of Sodom", "Sodom; Zoar; cave", "well-known", "19:5-8 and 19:30-38: rating decision"),
    ("Abraham", "Abraham 8: Abimelech", "GEN", "20:1", "20:18", "Abraham; Sarah; Abimelech", "", "Gerar", "lesser-known", ""),
    ("Abraham", "Abraham 9: Isaac Is Born", "GEN", "21:1", "21:34", "Abraham; Sarah; Isaac; Hagar; Ishmael", "Abimelech; Phicol; angel of God", "Wilderness of Beersheba", "well-known", ""),
    ("Abraham", "Abraham 10: On the Mountain", "GEN", "22:1", "22:24", "Abraham; Isaac", "Angel of Yahweh; servants", "Land of Moriah", "well-known", ""),
    ("Abraham", "Abraham 11: The Cave of Machpelah", "GEN", "23:1", "23:20", "Abraham; Ephron", "Children of Heth", "Hebron; Machpelah", "lesser-known", ""),
    ("Abraham", "Abraham 12: A Bride for Isaac", "GEN", "24:1", "24:67", "Abraham's servant; Rebekah; Isaac", "Laban; Bethuel", "City of Nahor; the well", "lesser-known", ""),
    ("Abraham", "Abraham 13: Esau and Jacob", "GEN", "25:1", "25:34", "Abraham; Esau; Jacob; Isaac; Rebekah", "Keturah's sons; Ishmael line", "Beer Lahai Roi", "well-known", "Esau red and hairy (25:25)"),
    ("Jacob", "Jacob 1: Isaac in Gerar", "GEN", "26:1", "26:35", "Isaac; Rebekah; Abimelech", "Herdsmen of Gerar", "Gerar; Beersheba", "lesser-known", ""),
    ("Jacob", "Jacob 2: The Stolen Blessing", "GEN", "27:1", "27:46", "Jacob; Esau; Isaac; Rebekah", "", "Isaac's tent", "well-known", ""),
    ("Jacob", "Jacob 3: The Ladder", "GEN", "28:1", "28:22", "Jacob", "Angels; Esau; Mahalath", "Bethel", "well-known", ""),
    ("Jacob", "Jacob 4: Rachel and Leah", "GEN", "29:1", "30:24", "Jacob; Rachel; Leah; Laban", "Bilhah; Zilpah; sons", "Haran; the well", "lesser-known", ""),
    ("Jacob", "Jacob 5: Jacob and Laban", "GEN", "30:25", "31:55", "Jacob; Laban; Rachel; Leah", "", "Haran; Gilead; Mizpah", "lesser-known", ""),
    ("Jacob", "Jacob 6: Wrestling at the Jabbok", "GEN", "32:1", "32:32", "Jacob; the man who wrestled", "Messengers; angels", "Mahanaim; Peniel", "well-known", "Who the wrestler is: show text only"),
    ("Jacob", "Jacob 7: Esau Runs to Meet Him", "GEN", "33:1", "33:20", "Jacob; Esau", "Wives; children", "Succoth; Shechem", "lesser-known", ""),
    ("Jacob", "Jacob 8: Dinah", "GEN", "34:1", "34:31", "Dinah; Shechem; Simeon; Levi; Jacob", "Hamor", "Shechem", "lesser-known", "34:2 assault, 34:25 slaughter: rating decision"),
    ("Jacob", "Jacob 9: Return to Bethel", "GEN", "35:1", "35:29", "Jacob; Rachel; Benjamin", "Deborah (Rebekah's nurse); Reuben; Isaac", "Bethel; Ephrath; Mamre", "lesser-known", "35:22: restrained"),
    ("Jacob", "The Generations of Esau", "GEN", "36:1", "36:43", "Esau", "Edomite chiefs and kings", "Seir; Edom", "lesser-known", "Genealogy"),
    ("Joseph", "Joseph 1: The Dreamer", "GEN", "37:1", "37:36", "Joseph; Jacob; Reuben; Judah", "Brothers; Midianites", "Hebron; Shechem; Dothan", "well-known", ""),
    ("Joseph", "Joseph 2: Judah and Tamar", "GEN", "38:1", "38:30", "Judah; Tamar", "Er; Onan; Shelah; Hirah", "Adullam; Timnah; Enaim", "lesser-known", "38:9, 38:15-18: rating decision"),
    ("Joseph", "Joseph 3: Potiphar's House", "GEN", "39:1", "39:23", "Joseph; Potiphar; Potiphar's wife", "Keeper of the prison", "Egypt", "well-known", "39:7-12: restrained"),
    ("Joseph", "Joseph 4: Two Dreams in Prison", "GEN", "40:1", "40:23", "Joseph; cupbearer; baker", "", "Egyptian prison", "lesser-known", ""),
    ("Joseph", "Joseph 5: Pharaoh's Dreams", "GEN", "41:1", "41:57", "Joseph; Pharaoh", "Cupbearer; Asenath; Manasseh; Ephraim", "Pharaoh's court", "well-known", ""),
    ("Joseph", "Joseph 6: The Brothers Bow", "GEN", "42:1", "42:38", "Joseph; brothers; Jacob", "Simeon; Benjamin", "Egypt; Canaan", "well-known", ""),
    ("Joseph", "Joseph 7: Benjamin Comes", "GEN", "43:1", "43:34", "Joseph; Judah; Benjamin", "Steward", "Joseph's house", "lesser-known", ""),
    ("Joseph", "Joseph 8: The Silver Cup", "GEN", "44:1", "44:34", "Joseph; Judah; Benjamin", "Steward", "Road from the city; Joseph's house", "lesser-known", ""),
    ("Joseph", "Joseph 9: I Am Joseph", "GEN", "45:1", "45:28", "Joseph; brothers; Jacob", "Pharaoh", "Joseph's house", "well-known", ""),
    ("Joseph", "Joseph 10: Israel Goes Down to Egypt", "GEN", "46:1", "47:31", "Jacob; Joseph; Pharaoh", "Family of seventy", "Beersheba; Goshen", "lesser-known", "Genealogy 46:8-27"),
    ("Joseph", "Joseph 11: Ephraim and Manasseh", "GEN", "48:1", "48:22", "Jacob; Joseph; Ephraim; Manasseh", "", "Jacob's bedside", "lesser-known", ""),
    ("Joseph", "Joseph 12: Jacob's Last Words", "GEN", "49:1", "49:33", "Jacob; twelve sons", "", "Jacob's bedside", "lesser-known", "Mostly poetry"),
    ("Joseph", "Joseph 13: The Bones of Joseph", "GEN", "50:1", "50:26", "Joseph; brothers", "Egyptians; physicians", "Egypt; Atad; Machpelah", "lesser-known", ""),
    ("Exodus", "Exodus 1: The Baby in the Basket", "EXO", "1:1", "2:25", "Moses; Shiphrah; Puah; Pharaoh's daughter; Miriam", "Pharaoh; Jochebed; Reuel; Zipporah", "Egypt; the Nile; Midian", "well-known", "1:16, 1:22 infanticide: restrained"),
    ("Exodus", "Exodus 2: The Burning Bush", "EXO", "3:1", "4:31", "Moses; Aaron", "Angel of Yahweh; Zipporah; Gershom", "Horeb; Midian; Egypt", "well-known", "4:24-26: show text only"),
    ("Exodus", "Exodus 3: Bricks Without Straw", "EXO", "5:1", "6:30", "Moses; Aaron; Pharaoh", "Taskmasters; officers", "Pharaoh's court; brickfields", "lesser-known", "Genealogy 6:14-27"),
    ("Exodus", "Exodus 4: Blood, Frogs, Lice, Flies", "EXO", "7:1", "8:32", "Moses; Aaron; Pharaoh", "Magicians", "The Nile; Egypt", "well-known", ""),
    ("Exodus", "Exodus 5: Livestock, Boils, Hail, Locusts, Darkness", "EXO", "9:1", "10:29", "Moses; Aaron; Pharaoh", "Servants of Pharaoh", "Egypt; Goshen", "well-known", ""),
    ("Exodus", "Exodus 6: The Passover", "EXO", "11:1", "12:51", "Moses; Aaron; Pharaoh", "Israelites", "Egypt; Rameses", "well-known", "12:29 death of firstborn: restrained"),
    ("Exodus", "Exodus 7: The Sea", "EXO", "13:1", "14:31", "Moses; Pharaoh", "Angel of God; pillar of cloud and fire", "Succoth; Etham; the Red Sea", "well-known", "14:28-30: restrained"),
    ("Exodus", "Exodus 8: The Song of the Sea", "EXO", "15:1", "15:27", "Moses; Miriam", "Israelites", "Shore of the Red Sea; Marah; Elim", "lesser-known", "Mostly poetry"),
    ("Wilderness", "Wilderness 1: Manna", "EXO", "16:1", "16:36", "Moses; Aaron", "Israelites", "Wilderness of Sin", "well-known", ""),
    ("Wilderness", "Wilderness 2: Water and Amalek", "EXO", "17:1", "17:16", "Moses; Joshua; Aaron; Hur", "Amalek", "Rephidim; Massah and Meribah", "lesser-known", "Battle: restrained"),
    ("Wilderness", "Wilderness 3: Jethro's Advice", "EXO", "18:1", "18:27", "Moses; Jethro", "Zipporah; Gershom; Eliezer", "Mountain of God", "lesser-known", ""),
    ("Sinai", "Sinai 1: The Ten Commandments", "EXO", "19:1", "20:26", "Moses; Aaron", "Israelites", "Mount Sinai", "well-known", ""),
    ("Sinai", "Sinai 2: The Book of the Covenant", "EXO", "21:1", "23:33", "Moses", "Israelites", "Mount Sinai", "lesser-known", "Law: main commandments only, verbatim"),
    ("Sinai", "Sinai 3: The Covenant Meal", "EXO", "24:1", "24:18", "Moses; Aaron; Nadab; Abihu; seventy elders", "Joshua", "Mount Sinai", "lesser-known", "24:10 'they saw the God of Israel': depiction rule"),
    ("Tabernacle", "Tabernacle 1: The Pattern", "EXO", "25:1", "31:18", "Moses; Aaron; Bezalel; Oholiab", "Aaron's sons", "Mount Sinai", "lesser-known", "Instructions: key verses only"),
    ("Sinai", "Sinai 4: The Golden Calf", "EXO", "32:1", "32:35", "Moses; Aaron; Joshua", "Sons of Levi", "Camp below Sinai", "well-known", "32:27-28: restrained"),
    ("Sinai", "Sinai 5: Show Me Your Glory", "EXO", "33:1", "33:23", "Moses; Joshua", "", "Tent of meeting; cleft of the rock", "lesser-known", "33:20-23: depiction rule"),
    ("Sinai", "Sinai 6: The Shining Face", "EXO", "34:1", "34:35", "Moses", "Aaron; Israelites", "Mount Sinai", "lesser-known", ""),
    ("Tabernacle", "Tabernacle 2: The Glory Fills the Tabernacle", "EXO", "35:1", "40:38", "Moses; Bezalel; Oholiab", "Israelites; Aaron and sons", "The camp; the tabernacle", "lesser-known", "Construction: key verses only"),
]


def ref(s):
    c, v = s.split(":")
    return int(c), int(v)


def main(db_path, out_csv):
    db = sqlite3.connect(db_path)
    order = {b: [(c, v) for c, v in db.execute(
        "SELECT chapter, verse FROM verses WHERE book=? ORDER BY chapter, verse", (b,))] for b in ("GEN", "EXO")}
    rows, problems = [], []
    expected = {"GEN": (1, 1), "EXO": (1, 1)}
    for n, (series, title, book, s, e, mains, supp, locs, pop, note) in enumerate(I, 1):
        seq = order[book]
        si, ei = seq.index(ref(s)), seq.index(ref(e))
        if seq[si] != expected[book]:
            problems.append(f"#{n} {title}: starts {s}, expected {expected[book][0]}:{expected[book][1]}")
        expected[book] = seq[ei + 1] if ei + 1 < len(seq) else None
        span = seq[si:ei + 1]
        words = sum(len(db.execute("SELECT text FROM verses WHERE book=? AND chapter=? AND verse=?",
                                   (book, c, v)).fetchone()[0].split()) for c, v in span)
        pages = max(6, math.ceil(words / WORDS_PER_PAGE))
        name = {"GEN": "Genesis", "EXO": "Exodus"}[book]
        rows.append({"issue": n, "series": series, "title": title,
                     "reference": f"{name} {s}–{e}", "verses": len(span), "words": words,
                     "est_story_pages": pages, "format": "series issue" if series not in ("Beginnings",) else "standalone",
                     "main_characters": mains, "supporting_characters": supp, "locations": locs,
                     "popularity": pop, "rating_or_decision_note": note})
    for b, exp in expected.items():
        if exp is not None:
            problems.append(f"{b}: coverage stops before {exp}")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    total_v = sum(r["verses"] for r in rows)
    print(f"issues={len(rows)} verses_covered={total_v} (GEN+EXO=2746) pages={sum(r['est_story_pages'] for r in rows)}")
    print("problems:", problems or "none")
    for r in rows:
        if r["est_story_pages"] > 40:
            print("LONG", r["issue"], r["title"], r["est_story_pages"])


if __name__ == "__main__":
    main(*sys.argv[1:3])
