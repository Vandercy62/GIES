"""Remove @classmethod from validators in Pydantic V1"""
import re

file_path = r'C:\GIES\backend\schemas\financeiro_schemas.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove @classmethod que vem DEPOIS de @validator
# Padrão: @validator(...)\n    @classmethod
content = re.sub(
    r'(@validator\([^\)]+\))\s+@classmethod',
    r'\1',
    content,
    flags=re.MULTILINE
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removidos todos os @classmethod dos validators!")
print(f"Arquivo atualizado: {file_path}")
