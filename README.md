# Tijoxa Python Packages

A [Simple Repository API](https://packaging.python.org/en/latest/specifications/simple-repository-api/) index hosted on GitHub Pages. The index serves HTML and links to wheels on GitHub Releases.

## Use with uv

Add the index and the package sources you need to your `pyproject.toml`.

```toml
[[tool.uv.index]]
name = "tijoxa"
url = "https://tijoxa.github.io/python-packages/simple/"
explicit = true

[tool.uv.sources]
snowpark-rs = { index = "tijoxa" }
snowpark-rs-session = { index = "tijoxa" }
polars-cactus = { index = "tijoxa" }
mosecapy = { index = "tijoxa" }
```

To install `snowpark-rs[session]`, include both Snowpark source entries and list `snowpark-rs-session` as a direct dependency in `project.dependencies`. This lets uv apply its source entry when resolving the extra from the explicit index.

The available Snowpark and Polars Cactus wheels target Windows x86-64 with CPython 3.13 or newer. Mosecapy is a pure Python wheel that requires Python 3.9. Use a separate project or environment for Mosecapy.

## Publish a wheel

1. Build a distribution wheel with `uv build --wheel` in the package's source repository.
2. Upload the wheel to a public GitHub Release. Snowpark wheels are hosted in this repository's Releases because their source repository is private.
3. Add a link to `simple/<normalized-package-name>/index.html` with the filename as link text, a `#sha256=` fragment with the wheel's hash, and an HTML-escaped `data-requires-python` attribute matching its metadata. Keep existing links for older wheels. For a new package, also add it to `simple/index.html`.
4. Push the index update to `main`. GitHub Pages publishes from the root of that branch.
