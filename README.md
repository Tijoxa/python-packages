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

The Snowpark release workflow builds wheels for Windows and Linux x86-64 and for Apple Silicon macOS. Snowpark and Polars Cactus require CPython 3.13 or newer. Polars Cactus is available here for Windows x86-64. Mosecapy is a pure Python wheel that requires Python 3.9. Use a separate project or environment for Mosecapy.

## Publish a wheel

Snowpark wheels are published by [Tijoxa/snowpark-rs](https://github.com/Tijoxa/snowpark-rs/releases). This repository refreshes their Simple index from the public releases hourly. Run the **Publish package index** workflow to refresh it on demand.

For other packages, follow these steps.

1. Build a distribution wheel with `uv build --wheel` in the package's source repository.
2. Upload the wheel to a public GitHub Release.
3. Add a link to `simple/<normalized-package-name>/index.html` with the filename as link text, a `#sha256=` fragment with the wheel's hash, and an HTML-escaped `data-requires-python` attribute matching its metadata. Keep existing links for older wheels. For a new package, also add it to `simple/index.html`.
4. Push the index update to `main` to trigger GitHub Pages deployment.
