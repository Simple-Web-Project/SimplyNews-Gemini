def build_page(data):
    l = []
    l.append("# {}".format(data["title"]))
    
    if "subtitle" in data.keys():
        l.append("## {}".format(data["subtitle"]))
    l.append("Last updated {} by {}".format(data["last_updated"], data["author"]))
    l.append("")

    for m in data["article"]:
        if "type" not in m.keys():
            print("Odd.. no type for this module..")
            continue

        t = m["type"]

        if t == "paragraph":
            l.append("{}\n".format(m["value"]))
        elif t == "text":
            l.append(m["value"])
        elif t == "linebreak":
            l.append("")
        elif t == "image":
            alt = ""
            if 'alt' in m.keys():
                alt = m['alt']
            l.append("=> {} (Image) {}".format(m["src"], alt))
        elif t == "video":
            l.append("=> {} (Video)".format(m["src"]))
        elif t == "iframe":
            l.append("=> {} (Embedded Media)".format(m["src"]))
        elif t == "link":
            l.append("=> {} {}".format(m["href"], m["value"]))
        elif t == "strong":
            l.append("*{}*".format(m["value"]))
        elif t == "em":
            l.append("_{}_".format(m["value"]))
        elif t == "blockquote":
            text = m["value"].replace("\n", "\n> ")
            l.append(text)
        elif t == "code":
            l.append("```\n{}\n```".format(m["value"]))
        elif t == "unsorted list":
            for entry in m["entries"]:
                l.append("* {}".format(entry["value"]))
        elif t == "header":
            prepend = '#' * int((m['size'])[1]) + " "
            l.append(prepend + m['value'])


    return l

