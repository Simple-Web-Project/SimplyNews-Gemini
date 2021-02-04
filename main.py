from simplynews_sites.links import sites
from build_page import build_page
from jetforce import GeminiServer, JetforceApplication, Response, Status
import os
import json
import datetime
import config


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
        "# This is SimplyNews",
        "SimplyNews is a gemini hole to read articles from article-based websites. Without JavaScript, ads and completely text-based. (duh!)",
        "",
        "## List of supported sites",
    ]
    for site in actual_sites:
        lines.append("=> " + site["link"] + " " + site["name"])

    lines += [
        "",
        "SimplyNews is part of the Simple Web project",
        "Do you have problems? Do you want a site to be added? Message os on our IRC (#simple-web on irc.freenode.net)"
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

    body = "\n".join(lines)
    return Response(Status.SUCCESS, "text/gemini", body)


if __name__ == "__main__":
    server = GeminiServer(app)
    server.run()

