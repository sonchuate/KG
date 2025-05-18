import pymupdf
class Reader:
    def __init__(self):
        pass
    
    def __call__(self, file:str) -> str:
        file = file.strip()

        extension = file.split('.')[-1]
        if extension not in ['txt', 'pdf']:
            raise Exception("Can read file with extension" + extension)
        
        if extension == "txt":
            return self.read_txt(file)
        if extension == "pdf":
            return self.read_pdf(file)
        
    def read_txt(self, file:str) -> str:
        with open(file, 'r', encoding="utf-8") as f:
            data = f.read()
        return self.normalize(data)
    
    def read_pdf(self, file:str) -> str:
        doc = pymupdf.open(file)

        all_text = []
        for page in doc: # iterate the document pages
            text = page.get_text()
            all_text.append(text)

        all_text = "\n".join(all_text)

        return self.normalize(all_text)
    
    def normalize(self, all_text:str) -> str:
        data = ""
        for line in all_text.split('\n'):
            if line.strip() == "":
                continue

            if data.endswith(' '):
                data += line
            elif line[0].islower():
                data += " " + line
            else:
                data += "\n" + line

        return data
    
if __name__ == "__main__":
    reader = Reader()
    print(reader(r"C:/Users/ADMIN/Downloads/pgnv.pdf"))