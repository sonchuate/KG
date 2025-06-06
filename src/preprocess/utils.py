import re
from src.preprocess.stop_word import STOP_WORD
from nltk.stem import PorterStemmer
ps = PorterStemmer()

abbreviation_dict = {}
try:
    with open("data/abbreviation/abbreviation.txt", 'r', encoding='utf-8') as f:
        data = f.read()
        for line in data.split('\n'):
            if len(line.strip()) < 3:
                continue
            try:
                ab_word, word = line.split("\t")

                # abbreviation_dict[ab_word.lower()] = word.lower()
                abbreviation_dict[ps.stem(ab_word.lower())] = ps.stem(word.lower())
            except ValueError:
                print(f"Bỏ qua dòng không hợp lệ (không tách được bằng tab): {line}")
except FileNotFoundError:
    print("Không tồn tại file viết tắt")

def expand_abbreviations(text:str):
    """
    Thay thế các từ viết tắt trong văn bản bằng dạng đầy đủ của chúng.
    
    Args:
        text (str): Văn bản đầu vào.

    Returns:
        str: Văn bản đã được mở rộng.
    """
    return_s = ""
    for w in text.split():
        if w in abbreviation_dict.keys():
            return_s += " " + abbreviation_dict[w]
        else:
            return_s += " " + w
    return return_s.strip()

def remove_parentheses_content(text):
    """
    Xóa toàn bộ nội dung trong ngoặc đơn (cả dấu ngoặc) khỏi chuỗi.
    
    Args:
        text (str): Chuỗi đầu vào.

    Returns:
        str: Chuỗi đã loại bỏ nội dung trong ngoặc đơn.
    """
    return re.sub(r'\s*\([^)]*\)', '', text)

def process_string(s:str) -> str:
    """Normalize text"""
    s = remove_parentheses_content(s)

    for c in """%#@!^&*:,/.-+'()\"""":
        s = s.replace(c, ' ')

    s = re.sub(r'\s+', ' ', s).strip()

    s = s.lower()

    s = ps.stem(s) # stem

    s = expand_abbreviations(s)
    
    s = s.replace(' ', '_')

    for sw in STOP_WORD:
        s = s.replace(sw, '')

    s = re.sub(r'_+', '_', s).strip('_')
    return s

if __name__ == "__main__":
    print(process_string("Hà Đông"))
    print(process_string("APIs"))
    print(process_string("Relational Database (RDBMS)"))
    print(process_string("RDBMS"))
    print(process_string("Ai"))