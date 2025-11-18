import re

with open('README.md', 'r') as f:
    content = f.read()

# Fix the thumbnail lines
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'thumbnail' in line and 'thumbnail.png' in line:
        # Current: \"thumbnail\": \"[![...](...) \\"title")](...) "
        # Should be: "thumbnail": "[![...](...) \\"title\\")](...) "
        # Replace \"thumbnail\": with "thumbnail":
        line = line.replace('\\"thumbnail\\":', '"thumbnail":')
        # Replace the value part
        # Find the value between "thumbnail": " and the last "
        start = line.find('"thumbnail": "') + len('"thumbnail": "')
        end = line.rfind('"')
        if start != -1 and end != -1 and end > start:
            value = line[start:end]
            # Escape all " in value
            escaped_value = value.replace('"', '\\"')
            line = line[:start] + escaped_value + line[end:]
        lines[i] = line

content = '\n'.join(lines)

with open('README.md', 'w') as f:
    f.write(content)

print('Fixed README')