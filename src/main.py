from load_data import load_users
from cleanup_planner import build_prompt
from gemini_client import call_gemini

with open("prompts/cleanup_prompt.txt") as f:
    base_prompt = f.read()

users = load_users("data/sample_users.csv")
final_prompt = build_prompt(users, base_prompt)

output = call_gemini(final_prompt)

# Clean the output
output = output.strip().lstrip('```csv').rstrip('```').strip()

with open("output/cleanup_report.csv", "w") as f:
    f.write(output)

print("Cleanup plan generated successfully.\n")
print(output)