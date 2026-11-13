from pathlib import Path

patterns = [
    "currentUserApiKey",
    "updateKey:function",
    "setCurrentUserApiKey",
]

for file in Path("frontend/js").glob("*.js"):
    text = file.read_text(encoding="utf-8", errors="ignore")

    for pattern in patterns:
        position = text.find(pattern)

        if position == -1:
            continue

        start = max(0, position - 150)
        end = min(len(text), position + 500)

        print(f"\n=== {file.name} | {pattern} | position {position} ===")
        print(repr(text[start:end]))