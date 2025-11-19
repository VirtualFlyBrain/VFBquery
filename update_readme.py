import re

# Read README
with open('README.md', 'r') as f:
    content = f.read()

# Read the correct JSON blocks
json_blocks = []
for i in range(1, 6):
    with open(f'json_block_{i}.json', 'r') as f:
        json_blocks.append(f.read().strip())

# Find all JSON blocks in README
json_pattern = r'```json\s*(.*?)\s*```'
matches = re.findall(json_pattern, content, re.DOTALL)

print(f'Found {len(matches)} JSON blocks in README')

# Replace each
new_content = content
for i, new_json in enumerate(json_blocks):
    old_block = matches[i]
    new_block = new_json
    old_full = f'```json\n{old_block}\n```'
    new_full = f'```json\n{new_block}\n```'
    new_content = new_content.replace(old_full, new_full, 1)

# Write back
with open('README.md', 'w') as f:
    f.write(new_content)

print('README updated')