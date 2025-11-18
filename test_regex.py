import re

pattern = r'\[\!\[([^\]]+)\]\(([^\'"\s]+)(?:\s+[\'"]([^\'"]*)[\'"])?\)\]\(([^)]+)\)'
string = "[![fru-M-000204 aligned to JFRC2](http://www.virtualflybrain.org/data/VFB/i/0000/0333/VFB_00017894/thumbnail.png 'fru-M-000204 aligned to JFRC2')](VFB_00017894,VFB_00000333)"

print('string:', repr(string))
match = re.search(pattern, string)
if match:
    print('Match found')
    print('group 1:', repr(match.group(1)))
    print('group 2:', repr(match.group(2)))
    print('group 3:', repr(match.group(3)))
    print('group 4:', repr(match.group(4)))
    new_string = f"[![{match.group(1)}]({match.group(2)} \"{match.group(3)}\")]({match.group(4)})"
    print('new_string:', repr(new_string))
else:
    print('No match')