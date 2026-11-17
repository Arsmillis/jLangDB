"""Download the latest English JMdict from jmdict-simplified, for tools/check.py --jmdict.

    python tools/fetch_jmdict.py [path]           (default: jmdict-eng.json.zip)

If GITHUB_TOKEN is set (as in GitHub Actions), it is sent to the GitHub API only, which raises its rate limit."""
import json
import os
import sys
import urllib.request

RELEASE_API = "https://api.github.com/repos/scriptin/jmdict-simplified/releases/latest"


def fetch(url):
    headers = {"User-Agent": "jlangdb"}
    if url.startswith("https://api.github.com/") and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return r.read()


def main(argv):
    path = argv[0] if argv else "jmdict-eng.json.zip"
    release = json.loads(fetch(RELEASE_API))
    # The full English edition, not jmdict-eng-common (common words only)
    asset = next(a for a in release["assets"] if a["name"].startswith("jmdict-eng-")
                 and not a["name"].startswith("jmdict-eng-common") and a["name"].endswith(".json.zip"))
    with open(path, "wb") as f:
        f.write(fetch(asset["browser_download_url"]))
    print("jmdict-simplified", release["tag_name"], "->", path)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
