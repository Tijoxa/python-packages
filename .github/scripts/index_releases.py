"""Index public GitHub Release assets on the static Simple API pages."""

import json
import re
import subprocess
import sys
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

RELEASE_PROJECTS = {
    "Tijoxa/snowpark-rs": ("snowpark-rs", "snowpark-rs-session"),
    "Tijoxa/denki-client": ("denki-client",),
}
SHA256 = re.compile(r"sha256:([a-f0-9]{64})")


class WheelLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: dict[str, tuple[str, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        href = attributes.get("href") or ""
        filename = urlsplit(href).path.rsplit("/", 1)[-1]
        if filename.endswith(".whl"):
            self.links[filename] = (href, attributes.get("data-requires-python") or "")


def public_releases(repository: str) -> list[dict]:
    response = subprocess.check_output(
        ["gh", "api", "--paginate", "--slurp", f"repos/{repository}/releases?per_page=100"],
        encoding="utf-8",
    )
    return [release for page in json.loads(response) for release in page if not release["draft"]]


def release_wheels(release: dict, projects: tuple[str, ...]) -> tuple[str, dict[str, tuple[str, str]]] | None:
    assets = {asset["name"]: asset for asset in release["assets"] if asset["state"] == "uploaded"}
    manifest = assets.get("wheel-index.json")
    if manifest is None:
        return None

    with urlopen(manifest["browser_download_url"], timeout=30) as response:
        info = json.load(response)

    name, version = info["name"], info["version"]
    if name not in projects or release["tag_name"] != f"{name}-v{version}":
        raise ValueError(f"Unexpected wheel manifest in {release['tag_name']}")

    prefix = f"{name.replace('-', '_')}-{version}-"
    links = {}
    for filename in info["wheels"]:
        asset = assets[filename]
        digest = SHA256.fullmatch(asset.get("digest") or "")
        if not filename.startswith(prefix) or not filename.endswith(".whl") or digest is None:
            raise ValueError(f"Invalid wheel asset {filename} in {release['tag_name']}")
        links[filename] = (
            f"{asset['browser_download_url']}#sha256={digest[1]}",
            info["requires-python"],
        )
    return name, links


def format_page(name: str, links: dict[str, tuple[str, str]]) -> str:
    anchors = "\n".join(
        f'    <a href="{escape(href)}" data-requires-python="{escape(requires_python)}">{escape(filename)}</a>'
        for filename, (href, requires_python) in sorted(links.items())
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Links for {name}</title>
  </head>
  <body>
    <h1>Links for {name}</h1>
{anchors}
  </body>
</html>
"""


def build_index(simple: Path) -> None:
    for repository, projects in RELEASE_PROJECTS.items():
        links_by_project = {}
        for name in projects:
            index = simple / name / "index.html"
            links = WheelLinks()
            links.feed(index.read_text(encoding="utf-8"))
            links_by_project[name] = links.links

        for release in public_releases(repository):
            public = release_wheels(release, projects)
            if public is not None:
                name, links = public
                links_by_project[name].update(links)

        for name, links in links_by_project.items():
            (simple / name / "index.html").write_text(format_page(name, links), encoding="utf-8")
            print(f"Indexed {len(links)} wheels for {name}")


if __name__ == "__main__":
    build_index(Path(sys.argv[1]))
