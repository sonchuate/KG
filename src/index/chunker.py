class Chunker:
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size

    def character_chunking(self, text:str, split_character:str) -> list[str]:
        if len(text.split(' ')) < self.chunk_size:
            return [text]
        
        output = []
        if split_character in text:
            tmp = ""
            len_tmp = 0
            for sub_chunk in text.split(split_character):
                if sub_chunk.strip() == "":
                    continue

                len_sub_chunk = len(sub_chunk.split(' '))
                if len_tmp + len_sub_chunk > self.chunk_size:
                    output.append(tmp)
                    len_tmp = len_sub_chunk
                    tmp = sub_chunk
                else:
                    len_tmp += len_sub_chunk
                    tmp += ' ' + sub_chunk
                
            output.append(tmp)

            return output
        
        return [text]



    def paragraph_chunking(self, text:str) -> list[str]:
        if len(text.split(' ')) < self.chunk_size:
            return [text]
        paragraph_chunks = self.character_chunking(text=text, split_character='\n')

        output = []
        for paragraph_chunk in paragraph_chunks:
            if len(paragraph_chunk.split(' ')) > self.chunk_size:
                output.extend(self.character_chunking(text=paragraph_chunk, split_character='.'))
            else:
                output.append(paragraph_chunk)
        
        output = [i.strip() for i in output]
        output = [i for i in output if i != ""]

        return output
        
if __name__ == "__main__":
    chunker = Chunker(10)
    text = \
"""Tiền xử lý dữ liệu của bạn - Trước tiên, bạn cần tiền xử lý dữ liệu của mình để đảm bảo chất lượng trước khi xác định kích thước khối tốt nhất cho ứng dụng của bạn. Ví dụ: nếu dữ liệu của bạn được lấy từ web, bạn có thể cần xóa các thẻ HTML hoặc các thành phần cụ thể chỉ thêm nhiễu.
Chọn một phạm vi kích thước khối - Sau khi dữ liệu của bạn được xử lý trước, bước tiếp theo là chọn một phạm vi kích thước khối tiềm năng để kiểm tra. Như đã đề cập trước đó, lựa chọn nên tính đến bản chất của nội dung (ví dụ: tin nhắn ngắn hoặc tài liệu dài), mô hình nhúng bạn sẽ sử dụng và khả năng của nó (ví dụ: giới hạn mã thông báo). Mục tiêu là tìm sự cân bằng giữa việc bảo toàn ngữ cảnh và duy trì độ chính xác. Bắt đầu bằng cách khám phá nhiều kích thước khối khác nhau, bao gồm các khối nhỏ hơn (ví dụ: 128 hoặc 256 mã thông báo) để nắm bắt thông tin ngữ nghĩa chi tiết hơn và các khối lớn hơn (ví dụ: 512 hoặc 1024 mã thông báo) để giữ lại nhiều ngữ cảnh hơn.
Đánh giá hiệu suất của từng kích thước khối - Để kiểm tra nhiều kích thước khối khác nhau, bạn có thể sử dụng nhiều chỉ mục hoặc một chỉ mục duy nhất với nhiều không gian tên . Với một tập dữ liệu đại diện, hãy tạo nhúng cho các kích thước khối mà bạn muốn kiểm tra và lưu chúng trong chỉ mục (hoặc các chỉ mục) của bạn. Sau đó, bạn có thể chạy một loạt các truy vấn để đánh giá chất lượng và so sánh hiệu suất của nhiều kích thước khối khác nhau. Đây rất có thể là một quá trình lặp đi lặp lại, trong đó bạn kiểm tra các kích thước khối khác nhau so với các truy vấn khác nhau cho đến khi bạn có thể xác định kích thước khối có hiệu suất tốt nhất cho nội dung và các truy vấn dự kiến ​​của mình.
"""
    print(chunker.paragraph_chunking(text))
