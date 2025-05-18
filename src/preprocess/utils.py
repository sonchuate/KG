import re
from src.preprocess.stop_word import STOP_WORD

def process_string(s:str) -> str:
    """Normalize text"""
    s = re.sub(r'\s+', ' ', s).strip()
    for c in """%#@!^&*:,/.-+'()\"""":
        s = s.replace(c, '')
    
    s = s.lower().replace(' ', '_')

    for sw in STOP_WORD:
        s = s.replace(sw, '')

    return s.strip('_')

if __name__ == "__main__":
    print(process_string("Hà Đông"))