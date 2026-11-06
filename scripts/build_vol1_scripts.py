"""Source of the Issue 2-5 scripts. Run: python3 scripts/build_vol1_scripts.py  (writes the JSON scripts)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LETTERING = {"caption": "Narration box", "divine": "God's words: Cinzel on solid dark band, no speaker drawn",
             "speech": "Speech bubble"}


def C(ref, text):
    return {"type": "caption", "ref": ref, "text": text}


def D(ref, text):
    return {"type": "divine", "ref": ref, "text": text}


def S(ref, text, who):
    return {"type": "speech", "ref": ref, "text": text, "speaker": who}


def P(n, camera, art, text, chars=(), size="landscape_4_3", face=None, sp=None, crowd=False):
    chars = list(chars)
    return {"panel": n, "camera": camera, "characters": chars, "art": art, "text": text, "size": size,
            "face_visible": bool(chars) if face is None else face, "story_point": sp, "allow_crowd": crowd}


def page(n, verses, layout, panels):
    return {"page": n, "verses": verses, "layout": layout, "panels": panels}


E = "eden_before_3_21"
EDEN_RULE = ("Setting rule for Genesis 2-3 (Eden): a lush untouched garden with nothing made by people: "
             "no buildings, walls, tents, roads, paths, fences or tools.")

issue2 = {
    "issue": 2, "title": "The Garden", "book": "GEN", "opening_reference": "Genesis 2:4–25, selected verses",
    "selection_file": "selections/vol1_genesis_1-5.json", "world_rule": EDEN_RULE, "lettering_types": LETTERING,
    "pages": [
        page(1, "Genesis 2:7", "full-page splash with series title, issue title and opening reference", [
            P(1, "close, low angle, warm first light", "A man's head and shoulders rising from red earth, eyes just opening, dust falling away; framed from the collarbone up.",
              [C("2:7", "Yahweh God formed man from the dust of the ground, and breathed into his nostrils the breath of life; and man became a living soul.")],
              ["ADAM"], "portrait_16_9", sp=E)]),
        page(2, "Genesis 2:8–9", "two wide horizontal panels", [
            P(1, "extreme wide, eastward at dawn", "A vast garden of every kind of tree beside rivers, in morning light.",
              [C("2:8", "Yahweh God planted a garden eastward, in Eden, and there he put the man whom he had formed.")], size="landscape_16_9"),
            P(2, "wide, centered", "Two great trees standing together in the middle of the garden, one bright and full of life, the other heavy with fruit; no figures.",
              [C("2:9", "Out of the ground Yahweh God made every tree to grow that is pleasant to the sight, and good for food, including the tree of life in the middle of the garden and the tree of the knowledge of good and evil.")], size="landscape_16_9")]),
        page(3, "Genesis 2:15–17", "large top panel, two bottom panels", [
            P(1, "medium, framed from the chest up behind tall leafy plants", "The man tending the garden, pruning a fruiting vine with his hands.",
              [C("2:15", "Yahweh God took the man, and put him into the garden of Eden to cultivate and keep it.")], ["ADAM"], "landscape_16_9", sp=E),
            P(2, "close on fruit-laden branches in warm light", "Branches heavy with many kinds of fruit.",
              [C("2:16", "Yahweh God commanded the man, saying,"), D("2:16", "You may freely eat of every tree of the garden;")]),
            P(3, "the tree of the knowledge of good and evil, seen from a distance", "The single tree standing apart, its fruit glowing softly; no figures.",
              [D("2:17", "but you shall not eat of the tree of the knowledge of good and evil; for in the day that you eat of it, you will surely die.")])]),
        page(4, "Genesis 2:18–19", "wide top panel, large bottom", [
            P(1, "wide, the man small and alone at evening, seen from behind, waist-down hidden by tall ferns", "The man alone in the vast garden.",
              [C("2:18", "Yahweh God said,"), D("2:18", "It is not good for the man to be alone. I will make him a helper comparable to him.")],
              ["ADAM"], "landscape_16_9", face=False, sp=E),
            P(2, "wide meadow, the man seen from behind, small, shoulders up above tall grass", "Animals of every kind and birds gathering around the man in a meadow: lions, deer, sheep, birds in the air.",
              [C("2:19", "Out of the ground Yahweh God formed every animal of the field, and every bird of the sky, and brought them to the man to see what he would call them.")],
              ["ADAM"], face=False, sp=E)]),
        page(5, "Genesis 2:21–22", "two wide horizontal panels", [
            P(1, "close, the man's sleeping face and shoulders among large ferns", "The man in deep sleep, head resting on moss, ferns covering him below the shoulders.",
              [C("2:21", "Yahweh God caused the man to fall into a deep sleep. As the man slept, he took one of his ribs, and closed up the flesh in its place.")],
              ["ADAM"], "landscape_16_9", sp=E),
            P(2, "medium, the woman framed from the collarbone up, soft morning light, flowering branches in the foreground", "The first woman, newly made, being brought to the man; both framed from the collarbone up.",
              [C("2:22", "Yahweh God made a woman from the rib which he had taken from the man, and brought her to the man.")],
              ["EVE", "ADAM"], "landscape_16_9", sp=E)]),
        page(6, "Genesis 2:23–24", "large top panel, two bottom panels", [
            P(1, "two faces close, cropped below the chin, leaves in the foreground", "The man seeing the woman for the first time, wonder on his face.",
              [C("2:23", "The man said,"), S("2:23", "This is now bone of my bones, and flesh of my flesh. She will be called ‘woman,’ because she was taken out of Man.", "ADAM")],
              ["ADAM", "EVE"], "landscape_16_9", sp=E),
            P(2, "close on two hands joined, nothing else in frame", "The man's and the woman's hands clasped together over green leaves.",
              [C("2:24", "Therefore a man will leave his father and his mother, and will join with his wife,")], ["ADAM", "EVE"], face=False, sp=E),
            P(3, "wide, warm evening, the garden at peace", "The garden at evening light, rivers glinting; no figures.",
              [C("2:24", "and they will be one flesh.")])]),
        page(7, "Genesis 2:25", "one large panel", [
            P(1, "wide, low angle into a bright low sun", "Two figures far away, a man and a woman, seen from behind, rendered as solid black silhouettes against the blazing low sun with no visible detail at all; only their heads and shoulders rise above tall meadow grass; the garden spreads before them.",
              [C("2:25", "The man and his wife were both naked, and they were not ashamed.")], ["ADAM", "EVE"], "landscape_4_3", face=False, sp=E)]),
    ],
    "moral": {
        "heading": "What This Story Teaches",
        "paragraph": "God made the first man with care, forming him from the ground and breathing life into him (Genesis 2:7). He gave him a good home, good work, and one clear command to obey (Genesis 2:15–17). God saw that it was “not good for the man to be alone,” so he made the woman and brought her to him (Genesis 2:18, 22). Jesus pointed back to this very chapter when he taught about marriage: “What therefore God has joined together, don’t let man tear apart” (Matthew 19:6). The story shows that people were made on purpose, for each other, and to live under God’s word. As the psalm says, “I am fearfully and wonderfully made” (Psalm 139:14).",
        "quotes": [{"ref": "GEN 2:18", "text": "not good for the man to be alone"},
                   {"ref": "MAT 19:6", "text": "What therefore God has joined together, don’t let man tear apart"},
                   {"ref": "PSA 139:14", "text": "I am fearfully and wonderfully made"}],
        "cited_without_quote": ["GEN 2:7", "GEN 2:15-17", "GEN 2:22"]},
    "coloring_pages": [
        {"subject": "Adam and Eve, faces (from page 6, panel 1; locked designs)", "characters": ["ADAM", "EVE"], "source_panel": "p06_1.png"},
        {"subject": "The garden: animals and birds gathered in a meadow", "characters": [],
         "prompt": "A lush garden meadow with a river and many fruit trees; a lion, a lamb, deer, a rabbit, a horse and birds gathered together. No people."}],
}

issue3 = {
    "issue": 3, "title": "The Serpent", "book": "GEN", "opening_reference": "Genesis 3:1–24, selected verses",
    "selection_file": "selections/vol1_genesis_1-5.json", "world_rule": EDEN_RULE, "lettering_types": LETTERING,
    "pages": [
        page(1, "Genesis 3:1", "full-page splash with series title, issue title and opening reference", [
            P(1, "close, the serpent coiled on a low branch in the foreground, the woman beyond it framed from the collarbone up, her long hair over her shoulders", "The serpent speaking to the woman in dappled garden light.",
              [C("3:1", "Now the serpent was more subtle than any animal of the field which Yahweh God had made. He said to the woman,"),
               S("3:1", "Has God really said, ‘You shall not eat of any tree of the garden’?", "SERPENT")],
              ["SERPENT", "EVE"], "portrait_16_9", sp=E)]),
        page(2, "Genesis 3:2–3", "two wide horizontal panels", [
            P(1, "medium, the woman framed from the collarbone up, facing the serpent on its branch", "The woman answering the serpent.",
              [C("3:2", "The woman said to the serpent,"), S("3:2", "We may eat fruit from the trees of the garden,", "EVE")],
              ["EVE", "SERPENT"], "landscape_16_9", sp=E),
            P(2, "wide, the tree in the middle of the garden, the woman small in the foreground seen from behind, shoulders up", "The forbidden tree in the middle of the garden.",
              [S("3:3", "but not the fruit of the tree which is in the middle of the garden. God has said, ‘You shall not eat of it. You shall not touch it, lest you die.’", "EVE")],
              ["EVE"], "landscape_16_9", face=False, sp=E)]),
        page(3, "Genesis 3:4–5", "tall left panel, two stacked right", [
            P(1, "close on the serpent's head, low and near", "The serpent's head and amber eyes, coiled in the branches.",
              [C("3:4", "The serpent said to the woman,"), S("3:4", "You won’t really die,", "SERPENT")], ["SERPENT"], "portrait_16_9"),
            P(2, "close on the fruit on the branch", "The fruit of the tree, glowing in the light.",
              [S("3:5", "for God knows that in the day you eat it, your eyes will be opened,", "SERPENT")]),
            P(3, "the woman's face framed from the collarbone up, looking at the fruit", "The woman gazing at the fruit, thinking.",
              [S("3:5", "and you will be like God, knowing good and evil.", "SERPENT")], ["EVE"], sp=E)]),
        page(4, "Genesis 3:6", "two wide horizontal panels", [
            P(1, "close, the woman's hand reaching to the fruit, her face framed from the collarbone up", "The woman taking the fruit.",
              [C("3:6", "When the woman saw that the tree was good for food, and that it was a delight to the eyes, and that the tree was to be desired to make one wise, she took some of its fruit, and ate.")],
              ["EVE"], "landscape_16_9", sp=E),
            P(2, "two faces close, cropped below the chin, the fruit between them", "The woman handing the fruit to the man.",
              [C("3:6", "Then she gave some to her husband with her, and he ate it, too.")], ["ADAM", "EVE"], "landscape_16_9", sp=E)]),
        page(5, "Genesis 3:7–8", "two wide horizontal panels", [
            P(1, "medium, the man and the woman from the chest up, wearing simple coverings sewn from large fig leaves", "Their eyes opened; both holding coverings of sewn fig leaves, troubled faces.",
              [C("3:7", "Their eyes were opened, and they both knew that they were naked. They sewed fig leaves together, and made coverings for themselves.")],
              ["ADAM", "EVE"], "landscape_16_9", sp="fig_leaves"),
            P(2, "wide, evening breeze through the trees, the two faces half-hidden behind trunks and leaves", "The man and woman hiding among the trees in the cool of the day.",
              [C("3:8", "They heard Yahweh God’s voice walking in the garden in the cool of the day, and the man and his wife hid themselves from the presence of Yahweh God among the trees of the garden.")],
              ["ADAM", "EVE"], "landscape_16_9", face=False, sp="fig_leaves")]),
        page(6, "Genesis 3:9–10", "two wide horizontal panels", [
            P(1, "wide, the empty garden in evening light, wind in the leaves", "The garden at evening; no figures visible.",
              [C("3:9", "Yahweh God called to the man, and said to him,"), D("3:9", "Where are you?")], size="landscape_16_9"),
            P(2, "close, the man's face from the chest up, fig-leaf covering, afraid", "The man stepping out from the trees, afraid.",
              [C("3:10", "The man said,"), S("3:10", "I heard your voice in the garden, and I was afraid, because I was naked; so I hid myself.", "ADAM")],
              ["ADAM"], "landscape_16_9", sp="fig_leaves")]),
        page(7, "Genesis 3:11–13", "large top panel, two bottom panels", [
            P(1, "medium, the man and the woman from the chest up in fig-leaf coverings, heads lowered, warm light falling on them", "The two standing in the light, ashamed.",
              [C("3:11", "God said,"), D("3:11", "Who told you that you were naked? Have you eaten from the tree that I commanded you not to eat from?")],
              ["ADAM", "EVE"], "landscape_16_9", sp="fig_leaves"),
            P(2, "medium, both framed from the chest up, the man pointing toward the woman beside him", "The man blaming the woman; both wear full coverings of sewn fig leaves from the shoulders to the knees.",
              [C("3:12", "The man said,"), S("3:12", "The woman whom you gave to be with me, she gave me fruit from the tree, and I ate it.", "ADAM")],
              ["ADAM", "EVE"], sp="fig_leaves"),
            P(3, "close, the woman looking down toward the serpent on the ground", "The woman blaming the serpent.",
              [C("3:13", "Yahweh God said to the woman,"), D("3:13", "What have you done?"), C("3:13", "The woman said,"),
               S("3:13", "The serpent deceived me, and I ate.", "EVE")], ["EVE"], sp="fig_leaves")]),
        page(8, "Genesis 3:14–15", "two wide horizontal panels", [
            P(1, "low, at ground level, the serpent sliding down onto the dust", "The serpent on its belly in the dust.",
              [C("3:14", "Yahweh God said to the serpent,"), D("3:14", "Because you have done this, you are cursed above all livestock, and above every animal of the field. You shall go on your belly and you shall eat dust all the days of your life.")],
              ["SERPENT"], "landscape_16_9"),
            P(2, "close at ground level, a bare human heel near the serpent's head in the dust", "A heel and the serpent's head on the ground.",
              [D("3:15", "I will put hostility between you and the woman, and between your offspring and her offspring. He will bruise your head, and you will bruise his heel.")],
              ["SERPENT"], "landscape_16_9", crowd=True)]),
        page(9, "Genesis 3:16–17, 3:19", "large top panel, two bottom panels", [
            P(1, "close, the woman's face from the chest up, fig-leaf covering, grieving", "The woman hearing her sentence.",
              [C("3:16", "To the woman he said,"), D("3:16", "I will greatly multiply your pain in childbirth. You will bear children in pain. Your desire will be for your husband, and he will rule over you.")],
              ["EVE"], "landscape_16_9", sp="fig_leaves"),
            P(2, "close, the man's face from the chest up, fig-leaf covering, head bowed", "The man hearing his sentence.",
              [C("3:17", "To Adam he said,"), D("3:17", "Because you have listened to your wife’s voice, and have eaten from the tree, about which I commanded you, saying, ‘You shall not eat of it,’ the ground is cursed for your sake.")],
              ["ADAM"], sp="fig_leaves"),
            P(3, "close on dry dust and thorny ground", "Dust running through open fingers over hard ground.",
              [D("3:19", "For you are dust, and you shall return to dust.")])]),
        page(10, "Genesis 3:21, 3:23", "two wide horizontal panels", [
            P(1, "medium, the man and the woman now clothed in garments of animal skins, warm light", "The two in their new skin garments.",
              [C("3:21", "Yahweh God made garments of animal skins for Adam and for his wife, and clothed them.")],
              ["ADAM", "EVE"], "landscape_16_9", sp="after_3_21"),
            P(2, "wide, the two walking away from the garden into a rocky land, seen from behind", "Leaving the garden.",
              [C("3:23", "Therefore Yahweh God sent him out from the garden of Eden, to till the ground from which he was taken.")],
              ["ADAM", "EVE"], "landscape_16_9", face=False, sp="after_3_21")]),
        page(11, "Genesis 3:24", "one large panel", [
            P(1, "wide, the east gate of the garden at dusk", "Two cherubim standing at the east of the garden; between them, apart from them and held by no one, exactly one single flaming sword turning in the air (only one sword in the whole image); the man and woman far away, small, outside.",
              [C("3:24", "So he drove out the man; and he placed cherubim at the east of the garden of Eden, and a flaming sword which turned every way, to guard the way to the tree of life.")],
              ["CHERUB"], "landscape_4_3", face=False, crowd=True)]),
    ],
    "moral": {
        "heading": "What This Story Teaches",
        "paragraph": "The serpent did not force the woman; he questioned what God had said and then denied it: “You won’t really die” (Genesis 3:4). The New Testament warns about the same danger, “as the serpent deceived Eve in his craftiness” (2 Corinthians 11:3). Sin started with wanting what God had forbidden, just as James describes: “each one is tempted when he is drawn away by his own lust and enticed” (James 1:14). Afterward the man and woman hid and blamed others. The Bible later explains that through one man “sin entered into the world” (Romans 5:12). Yet the chapter does not end in silence: God still spoke to them, and he made them garments of skins and clothed them (Genesis 3:21).",
        "quotes": [{"ref": "GEN 3:4", "text": "You won’t really die"},
                   {"ref": "2CO 11:3", "text": "as the serpent deceived Eve in his craftiness"},
                   {"ref": "JAS 1:14", "text": "each one is tempted when he is drawn away by his own lust and enticed"},
                   {"ref": "ROM 5:12", "text": "sin entered into the world"}],
        "cited_without_quote": ["GEN 3:21"]},
    "coloring_pages": [
        {"subject": "The serpent in the tree (locked design)", "characters": ["SERPENT"], "source_panel": "p03_1.png"},
        {"subject": "Adam and Eve in garments of skins (locked designs)", "characters": ["ADAM", "EVE"], "source_panel": "p10_1.png"}],
}

A = "after_3_21"
issue4 = {
    "issue": 4, "title": "Cain and Abel", "book": "GEN", "opening_reference": "Genesis 4:1–26, selected verses",
    "selection_file": "selections/vol1_genesis_1-5.json", "lettering_types": LETTERING,
    "world_rule": "Setting rule for Genesis 4: open land east of Eden; fields, flocks and simple stone or earth works only; no cities, no buildings.",
    "pages": [
        page(1, "Genesis 4:1–2", "two wide horizontal panels", [
            P(1, "medium, warm light, the woman holding a newborn wrapped in hide, the man beside her", "Eve holding her first son, Adam looking on.",
              [C("4:1", "The man knew Eve his wife. She conceived, and gave birth to Cain, and said,"), S("4:1", "I have gotten a man with Yahweh’s help.", "EVE")],
              ["EVE", "ADAM"], "landscape_16_9", sp=A, crowd=True),
            P(2, "wide split composition: a grown farmer breaking soil on the left, a grown shepherd with his flock on the right", "Cain tilling a field; Abel keeping sheep on a hillside.",
              [C("4:2", "Again she gave birth, to Cain’s brother Abel. Abel was a keeper of sheep, but Cain was a tiller of the ground.")],
              ["CAIN", "ABEL"], "landscape_16_9")]),
        page(2, "Genesis 4:3–5", "large top panel, two bottom panels", [
            P(1, "wide, two brothers on an open hill at evening, each presenting an offering", "Cain bringing grain and fruit; Abel bringing a firstborn lamb.",
              [C("4:3", "As time passed, Cain brought an offering to Yahweh from the fruit of the ground."),
               C("4:4", "Abel also brought some of the firstborn of his flock and of its fat.")], ["CAIN", "ABEL"], "landscape_16_9"),
            P(2, "close, warm light falling on the younger brother and his offering", "Abel in warm light.",
              [C("4:4", "Yahweh respected Abel and his offering,")], ["ABEL"]),
            P(3, "close, the older brother's face in shadow, angry, eyes down", "Cain's fallen, angry face.",
              [C("4:5", "but he didn’t respect Cain and his offering. Cain was very angry, and the expression on his face fell.")], ["CAIN"])]),
        page(3, "Genesis 4:6–7", "two wide horizontal panels", [
            P(1, "medium, Cain alone on the hill at dusk, turned away", "Cain alone, brooding.",
              [C("4:6", "Yahweh said to Cain,"), D("4:6", "Why are you angry? Why has the expression of your face fallen?")], ["CAIN"], "landscape_16_9"),
            P(2, "low, a dark doorway of a rough stone shelter with deep shadow at the threshold, Cain small beyond it", "Deep shadow lying across the threshold of the doorway; only darkness, no figure, no creature, no face or shape in the shadow.",
              [D("4:7", "If you do well, won’t it be lifted up? If you don’t do well, sin crouches at the door. Its desire is for you, but you are to rule over it.")],
              ["CAIN"], "landscape_16_9", face=False)]),
        page(4, "Genesis 4:8", "two wide horizontal panels", [
            P(1, "medium, the two brothers side by side, Cain speaking", "Cain speaking to Abel.",
              [C("4:8", "Cain said to Abel, his brother,"), S("4:8", "Let’s go into the field.", "CAIN")], ["CAIN", "ABEL"], "landscape_16_9"),
            P(2, "extreme wide, two tiny distant silhouettes in a field under a darkening red sky, one rising over the other; nothing graphic, no weapon, no blood", "The field at dusk, far away.",
              [C("4:8", "While they were in the field, Cain rose up against Abel, his brother, and killed him.")], ["CAIN", "ABEL"], "landscape_16_9", face=False)]),
        page(5, "Genesis 4:9–10", "two wide horizontal panels", [
            P(1, "medium, Cain alone in the field at dawn, defiant", "Cain answering.",
              [C("4:9", "Yahweh said to Cain,"), D("4:9", "Where is Abel, your brother?"), C("4:9", "He said,"),
               S("4:9", "I don’t know. Am I my brother’s keeper?", "CAIN")], ["CAIN"], "landscape_16_9"),
            P(2, "close on the bare earth of the field, a fallen shepherd's staff in the grass; no blood visible", "The silent ground.",
              [C("4:10", "Yahweh said,"), D("4:10", "What have you done? The voice of your brother’s blood cries to me from the ground.")], size="landscape_16_9")]),
        page(6, "Genesis 4:11–13", "large top panel, two bottom panels", [
            P(1, "wide, cracked dry ground stretching to the horizon, Cain small and kneeling", "Cursed ground.",
              [D("4:11", "Now you are cursed because of the ground, which has opened its mouth to receive your brother’s blood from your hand.")],
              ["CAIN"], "landscape_16_9", face=False),
            P(2, "close, Cain's hands in barren soil", "Withered sprouts in dry soil.",
              [D("4:12", "From now on, when you till the ground, it won’t yield its strength to you. You will be a fugitive and a wanderer on the earth.")]),
            P(3, "close, Cain's face in anguish", "Cain crying out.",
              [C("4:13", "Cain said to Yahweh,"), S("4:13", "My punishment is greater than I can bear.", "CAIN")], ["CAIN"])]),
        page(7, "Genesis 4:15–16", "two wide horizontal panels", [
            P(1, "medium, Cain standing in a beam of light; nothing drawn on his body", "Cain under a shaft of light.",
              [C("4:15", "Yahweh appointed a sign for Cain, so that anyone finding him would not strike him.")], ["CAIN"], "landscape_16_9"),
            P(2, "extreme wide, a lone figure walking east into a barren land, seen from behind", "Cain going away.",
              [C("4:16", "Cain left Yahweh’s presence, and lived in the land of Nod, east of Eden.")], ["CAIN"], "landscape_16_9", face=False)]),
        page(8, "Genesis 4:25–26", "two wide horizontal panels", [
            P(1, "medium, warm light, Eve holding a newborn wrapped in hide, Adam beside her; the baby's face hidden", "Eve with her newborn son Seth.",
              [C("4:25", "Adam knew his wife again. She gave birth to a son, and named him Seth, saying,"),
               S("4:25", "for God has given me another child instead of Abel, for Cain killed him.", "EVE")], ["EVE", "ADAM"], "landscape_16_9", sp=A, crowd=True),
            P(2, "wide, a small gathering of people on a hillside at dawn, hands lifted, among them a grown man holding an infant", "People beginning to call on Yahweh's name.",
              [C("4:26", "A son was also born to Seth, and he named him Enosh. At that time men began to call on Yahweh’s name.")],
              ["SETH"], "landscape_16_9", face=False, crowd=True)]),
    ],
    "moral": {
        "heading": "What This Story Teaches",
        "paragraph": "Two brothers brought offerings, and God respected Abel’s. The Bible later explains why: “By faith Abel offered to God a more excellent sacrifice than Cain” (Hebrews 11:4). God warned Cain before he sinned: “sin crouches at the door. Its desire is for you, but you are to rule over it” (Genesis 4:7). Cain did not listen, and anger became murder. The apostle John uses this story to teach a simple command: “we should love one another” (1 John 3:11), “unlike Cain” (1 John 3:12). Even after this sorrow, God gave Adam and Eve another son, Seth, and people “began to call on Yahweh’s name” (Genesis 4:26).",
        "quotes": [{"ref": "HEB 11:4", "text": "By faith Abel offered to God a more excellent sacrifice than Cain"},
                   {"ref": "GEN 4:7", "text": "sin crouches at the door. Its desire is for you, but you are to rule over it"},
                   {"ref": "1JN 3:11", "text": "we should love one another"},
                   {"ref": "1JN 3:12", "text": "unlike Cain"},
                   {"ref": "GEN 4:26", "text": "began to call on Yahweh’s name"}],
        "cited_without_quote": []},
    "coloring_pages": [
        {"subject": "Cain and Abel with their offerings (locked designs)", "characters": ["CAIN", "ABEL"], "source_panel": "p02_1.png"},
        {"subject": "Abel's flock on the hillside", "characters": [],
         "prompt": "A hillside pasture with a flock of sheep and lambs, a few trees, a stream and hills behind. No people."}],
}

issue5 = {
    "issue": 5, "title": "From Adam to Noah", "book": "GEN", "opening_reference": "Genesis 5:1–32, selected verses",
    "selection_file": "selections/vol1_genesis_1-5.json", "lettering_types": LETTERING,
    "world_rule": "Setting rule for Genesis 5: open lands, simple tents of hide and early stone dwellings only.",
    "pages": [
        page(1, "Genesis 5:1, 5:3", "two wide horizontal panels", [
            P(1, "medium, Adam (mature, grey at the temples) looking over his fields at sunrise", "Adam in later life.",
              [C("5:1", "This is the book of the generations of Adam. In the day that God created man, he made him in God’s likeness.")],
              ["ADAM"], "landscape_16_9", sp="adam_older"),
            P(2, "medium, Adam holding a small child whose face is turned toward him; the child's face is hidden", "Adam with his young son Seth.",
              [C("5:3", "Adam lived one hundred thirty years, and became the father of a son in his own likeness, after his image, and named him Seth.")],
              ["ADAM"], "landscape_16_9", sp="adam_older", crowd=True)]),
        page(2, "Genesis 5:5, 5:22", "two wide horizontal panels", [
            P(1, "medium, Adam very old with long white hair and beard, seated at dusk at the door of a hide tent", "Adam at the end of his long life.",
              [C("5:5", "All the days that Adam lived were nine hundred thirty years, then he died.")], ["ADAM"], "landscape_16_9", sp="adam_old"),
            P(2, "wide, Enoch walking along a hill path at sunrise, children and grandchildren around his tent below", "Enoch walking.",
              [C("5:22", "After Methuselah’s birth, Enoch walked with God for three hundred years, and became the father of more sons and daughters.")],
              ["ENOCH"], "landscape_16_9", crowd=True)]),
        page(3, "Genesis 5:24", "two wide horizontal panels", [
            P(1, "wide, Enoch walking alone along a high hill toward a bright horizon, the low sun off to the side", "Enoch walking toward the light; no glow or halo around him.",
              [C("5:24", "Enoch walked with God,")], ["ENOCH"], "landscape_16_9", face=False),
            P(2, "the same hill and horizon, now empty, light lingering", "The empty hilltop.",
              [C("5:24", "and he was not found, for God took him.")], size="landscape_16_9")]),
        page(4, "Genesis 5:27, 5:29", "two wide horizontal panels", [
            P(1, "close, Methuselah, extremely old, seated, looking out", "Methuselah in great old age.",
              [C("5:27", "All the days of Methuselah were nine hundred sixty-nine years, then he died.")], ["METHUSELAH"], "landscape_16_9"),
            P(2, "medium, Lamech in a field holding his newborn son wrapped in wool; the baby's face hidden", "Lamech naming Noah.",
              [C("5:29", "He named him Noah, saying,"), S("5:29", "This one will comfort us in our work and in the toil of our hands, caused by the ground which Yahweh has cursed.", "LAMECH")],
              ["LAMECH"], "landscape_16_9")]),
        page(5, "Genesis 5:32", "one large panel", [
            P(1, "medium, warm evening light, Noah seated with three small boys around him; the children's faces turned toward him", "Noah with his young sons Shem, Ham and Japheth.",
              [C("5:32", "Noah was five hundred years old, then Noah became the father of Shem, Ham, and Japheth.")],
              ["NOAH"], "landscape_4_3", crowd=True)]),
        page(6, "Genesis 5:1–32", "family tree", []),
    ],
    "family_tree": ["Adam", "Seth", "Enosh", "Kenan", "Mahalalel", "Jared", "Enoch", "Methuselah", "Lamech", "Noah",
                    ["Shem", "Ham", "Japheth"]],
    "moral": {
        "heading": "What This Story Teaches",
        "paragraph": "Genesis 5 reads like a list of names, but it carries a message. Again and again it says “then he died,” showing that what God told Adam came true. Yet the line goes on, and in the middle of it stands Enoch, who “walked with God” (Genesis 5:24). Hebrews explains that before he was taken “he had been well pleasing to God” (Hebrews 11:5), and it says, “Without faith it is impossible to be well pleasing to him” (Hebrews 11:6). The chapter ends with Noah, whose father hoped he would bring comfort (Genesis 5:29). Psalm 90:12 gives a fitting prayer: “teach us to count our days, that we may gain a heart of wisdom.”",
        "quotes": [{"ref": "GEN 5:5", "text": "then he died"},
                   {"ref": "GEN 5:24", "text": "walked with God"},
                   {"ref": "HEB 11:5", "text": "he had been well pleasing to God"},
                   {"ref": "HEB 11:6", "text": "Without faith it is impossible to be well pleasing to him"},
                   {"ref": "PSA 90:12", "text": "teach us to count our days, that we may gain a heart of wisdom"}],
        "cited_without_quote": ["GEN 5:29"]},
    "coloring_pages": [
        {"subject": "Noah (locked design)", "characters": ["NOAH"], "source_panel": "p05_1.png"},
        {"subject": "Enoch walking with God on the hill (locked design)", "characters": ["ENOCH"], "source_panel": "p03_1.png"}],
}

for sc, name in [(issue2, "issue02_the_garden"), (issue3, "issue03_the_serpent"), (issue4, "issue04_cain_and_abel"),
                 (issue5, "issue05_from_adam_to_noah")]:
    sc["status"] = "approved 2026-11-06"
    (HERE / f"{name}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", name)
