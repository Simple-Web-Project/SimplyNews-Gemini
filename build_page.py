def build_page(data):
    l = []
    l.append("# " + data["title"])
    
    if "subtitle" in data.keys():
        l.append("## " + data["subtitle"])
    l.append("Last updated " + data["last_updated"] + " by " + data["author"])
    l.append("")

    for m in data["article"]:
        if "type" not in m.keys():
            print("Odd.. no type for this module..")
            continue

        t = m["type"]

        if t == "paragraph":
            l.append(m["value"] + "\n")
        elif t == "text":
            l.append(m["value"])
        elif t == "linebreak":
            l.append("")
        elif t == "image":
            if 'alt' in m.keys():
                alt = m['alt']
            else:
                alt = ""
            l.append("=> " + str(m["src"]) + " (Image) " + alt)
        elif t == "video":
            l.append("=> " + str(m["src"]) + " (Video)")
        elif t == "iframe":
            l.append("=> " + str(m["src"]) + " (Embedded Media)")
        elif t == "link":
            l.append("=> " + str(m["href"]) + " " + str(m["value"]))
        elif t == "strong":
            l.append("*" + m["value"] + "*")
        elif t == "em":
            l.append("_" + m["value"] + "_")
        elif t == "blockquote":
            text = m["value"].replace("\n", "\n> ")
            l.append(text)
        elif t == "code":
            l.append("```\n" + m["value"] + "\n```")
        elif t == "unsorted list":
            for entry in m["entries"]:
                l.append("* " + entry["value"])
        elif t == "header":
            prepend = '#' * int((m['size'])[1]) + " "
            l.append(prepend + m['value'])


    return l

