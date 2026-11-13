import json
from pathlib import Path

frontend = Path("frontend")
output = Path("frontend_source")
output.mkdir(exist_ok=True)

for map_file in frontend.glob("js/*.js.map"):
    with map_file.open(encoding="utf-8") as file:
        source_map = json.load(file)

    sources = source_map.get("sources", [])
    contents = source_map.get("sourcesContent") or []

    for source, content in zip(sources, contents):
        if not content:
            continue

        clean_source = (
            source.replace("webpack:///", "")
            .replace("../", "")
            .replace("src/", "")
        )
        target = output / clean_source
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

print(f"Sources extracted to: {output.resolve()}")