import json
with open('file merge code.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
with open('file_merge_code.py', 'w', encoding='utf-8') as f:
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            f.write(''.join(cell['source']) + '\n\n')
