import requests


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

class OCR:
    def __init__(self, url:str):
        self.server_url = url

    def image2text(self, file_path):
        files=[
            ('file',(file_path.split('/')[-1], open(file_path,'rb'), 'image/png'))
        ]
        response = requests.request("POST", self.server_url + "/infer", headers={}, data={}, files=files)
        return response.json()['markdown_output']

    def pdf2text(self, file_path):
        files=[
            ('file',('hehe.pdf',open(file_path,'rb'),'application/pdf'))
        ]
        response = requests.request("POST", self.server_url + "/pdf-to-text", headers={}, data={}, files=files)
        return response.json()['markdown_output']

if __name__ == "__main__":
    ocr = OCR("https://3cff-35-201-16-170.ngrok-free.app")
    print(ocr.image2text("C:/Users/ADMIN/Downloads/graph.png"))
    print("_"*80)
    print(ocr.pdf2text("C:/Users/ADMIN/Downloads/TranCaoSon.pdf"))