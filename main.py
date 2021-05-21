from simplynews_sites.links import sites
from build_page import build_page
from jetforce import GeminiServer, JetforceApplication, Response, Status
import os
import json
import datetime
import config


page_header = """```
.d8888. d888888b .88b  d88. d8888b. db      db    db      d8b   db d88888b db   d8b   db .d8888. 
88'  YP   `88'   88'YbdP`88 88  `8D 88      `8b  d8'      888o  88 88'     88   I8I   88 88'  YP 
`8bo.      88    88  88  88 88oodD' 88       `8bd8'       88V8o 88 88ooooo 88   I8I   88 `8bo.   
  `Y8b.    88    88  88  88 88~~~   88         88         88 V8o88 88~~~~~ Y8   I8I   88   `Y8b. 
db   8D   .88.   88  88  88 88      88booo.    88         88  V888 88.     `8b d8'8b d8' db   8D 
`8888Y' Y888888P YP  YP  YP 88      Y88888P    YP         VP   V8P Y88888P  `8b8' `8d8'  `8888Y' 
```
"""


actual_sites = {}
for link in sites.keys():
    site = sites[link]
    if site.identifier in actual_sites:
        continue
    actual_sites[site.identifier] = {"link": link, "name": site.site_title}

_actual_sites = []
for key in sorted(actual_sites.keys()):
    _actual_sites.append(actual_sites[key])
actual_sites = _actual_sites

# Configuration
cfg = config.parse_config()

os.makedirs(
    os.path.expanduser(cfg["settings"]["cachePath"]),
    exist_ok=True,
)


app = JetforceApplication()

@app.route("", strict_trailing_slash=False)
def index(request):
    lines = [
        page_header,
        "# This is SimplyNews",
        "SimplyNews is a gemini capsule to read articles from article-based websites. Without JavaScript, ads and completely text-based. (duh!)",
        "NOTE: SimplyNews is in a very early stage of development, please be aware that almost certainly you are going to encounter bugs.",
        "",
        "## List of supported sites",
    ]
    for site in actual_sites:
        lines.append("=> " + site["link"] + " " + site["name"])

    lines += [
        "",
        "SimplyNews is part of the Simple Web project",
        "Do you have problems? Do you want a site to be added? Message os on our IRC (#simple-web on irc.libera.chat)"
        "",
        "=> https://git.sr.ht/~metalune/simplynews_gemini Source Code for this Website"
    ]
    
    body = "\n".join(lines)
    return Response(Status.SUCCESS, "text/gemini", body)


@app.route("/(?P<p>.*)", strict_trailing_slash=False)
def site(request, p):
    split_path = p.split("/")

    site = split_path[0]
    path = p[len(split_path[0]) + 1:]

    if site not in sites:
        return Response(Status.NOT_FOUND, f"SimplyNews doesn't seem to support sites with the url {site}")

    if len(path) > 0:
        return handle_page_url(site, path)
    return site_main(site)


def site_main(site):
    site_o = sites[site]

    lines = [
        "# Recent articles from " + site_o.site_title
    ]


    ident = site_o.identifier
    cache_file_path = os.path.join(
        os.path.expanduser(cfg["settings"]["cachePath"]),
        f"{ident}.json",
    )
    recent_articles = None

    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, "r") as cache_file:
                recent_articles_cached = json.loads(cache_file.read())

            last_updated = recent_articles_cached["last_updated"]
            date_time = datetime.datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
            if (datetime.datetime.now() - date_time) > sites[
                site
            ].cache_refresh_time_delta:
                recent_articles = None
            else:
                recent_articles = recent_articles_cached["recent_articles"]

        except Exception as e:
            print(f"Error loading cache for '{ident}':")
            print(str(e))

    if recent_articles is None:
        recent_articles = site_o.get_recent_articles()
        cache_content = {
            "last_updated": str(datetime.datetime.now()),
            "recent_articles": recent_articles,
        }
        with open(cache_file_path, "w") as cache_file:
            cache_file.write(json.dumps(cache_content))

    for article in recent_articles:
        link = "/" + site + "/" + article["link"]
        lines.append("=> " + link + " " + article["title"])

    body = "\n".join(lines)
    return Response(Status.SUCCESS, "text/gemini", body)


def handle_page_url(site, path):

    try:
        lines = build_page(sites[site].get_page(path))
    except Exception as e:
        return Response(Status.CGI_ERROR, str(e))

    lines.append("")
    lines.append("=> /" + site + " Back to " + site) 
    lines.append(f"=> https://{site}/{path} See original post on " + sites[site].site_title)

    body = "\n".join(lines)
    return Response(Status.SUCCESS, "text/gemini", body)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Gemini frontend for SimplyNews')
    parser.add_argument('hostname', default='localhost', metavar='HOSTNAME', type=str)
    parser.add_argument('port', default=1956, metavar='PORT', type=int)

    args = parser.parse_args()
    server = GeminiServer(app, port=args.port, hostname=args.hostname)
    server.run()

