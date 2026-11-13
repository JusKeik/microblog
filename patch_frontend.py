import re
from pathlib import Path

file = Path("frontend/js/app.ee2cdef2.js")
text = file.read_text(encoding="utf-8", errors="ignore")

state_pattern = r'currentUserApiKey:"test"'
state_replacement = (
    'currentUserApiKey:localStorage.getItem("api_key")||"test"'
)

button_pattern = (
    r'this\.\$store\.commit\("setCurrentUserApiKey",'
    r'this\.newApiKey\),'
    r'this\.\$store\.dispatch\("setLogOut"\),'
    r'this\.\$router\.push\(\{path:"/login"\}\)'
)

button_replacement = (
    'this.$store.commit("setCurrentUserApiKey",this.newApiKey),'
    'localStorage.setItem("api_key",this.newApiKey),'
    'localStorage.setItem("apiKey",this.newApiKey),'
    'this.$store.dispatch("setLogOut"),'
    'this.$router.push({path:"/login"}).then('
    '(function(){location.reload()}))'
)

text, state_count = re.subn(
    state_pattern,
    state_replacement,
    text,
)

text, button_count = re.subn(
    button_pattern,
    button_replacement,
    text,
)

print(f"State replacements: {state_count}")
print(f"Button replacements: {button_count}")

if state_count == 0 or button_count == 0:
    print("Patch was not applied completely")
else:
    file.write_text(text, encoding="utf-8")
    print("Frontend bundle patched successfully")