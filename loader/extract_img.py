import fitz  # PyMuPDF
import io
from PIL import Image
import os
import re
from openpyxl import Workbook

def extract_images_from_pdf(pdf_path, output_folder):
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    current_date_folder = "unknown_date"
    previous_date_folder = "unknown_date"
    previous_date_y = 0
    text_by_date = {}

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        image_list = page.get_images(full=True)
        blocks = page.get_text("dict")["blocks"]

        page_dates = date_pattern.findall(page.get_text())
        if page_dates:
            current_date_folder = page_dates[0]
            previous_date_folder = current_date_folder
            previous_date_y = 0  # 페이지가 바뀌면 이전 날짜의 y좌표 초기화

        if current_date_folder not in text_by_date:
            text_by_date[current_date_folder] = ""

        # 텍스트 블록에서 날짜를 추출하고 y좌표를 기록
        date_positions = []
        for block in blocks:
            # 텍스트 추출
            if "lines" in block:
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                dates = date_pattern.findall(block_text)
                if dates:
                    y_position = block["bbox"][1]
                    date_positions.append((dates[-1], y_position))
                    previous_date_folder = current_date_folder
                    previous_date_y = y_position
                    current_date_folder = dates[-1]
                    if current_date_folder not in text_by_date:
                        text_by_date[current_date_folder] = ""

        # 디버깅을 위해 텍스트 블록과 날짜의 y좌표 출력
        print(f"Page {page_num + 1} text blocks with dates and their y-coordinates:")
        for date, y in date_positions:
            print(f"Date: {date}, y-coordinate: {y}")

        # 이미지 처리
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))

            # 이미지의 y좌표 가져오기
            img_bbox = None
            for block in blocks:
                if block.get("image") == xref:
                    img_bbox = block["bbox"]
                    break

            if img_bbox:
                image_y = img_bbox[1]

                # 디버깅을 위해 이미지의 y좌표 출력
                print(f"Page {page_num + 1}, Image {img_index + 1}, y-coordinate: {image_y}")

                # 이미지가 속할 날짜 폴더 결정
                assigned_date = previous_date_folder
                for date, y_position in date_positions:
                    if image_y > y_position:
                        assigned_date = date
                        break
            else:
                assigned_date = current_date_folder

            # 이미지 저장 폴더 생성 (이미 모든 이미지를 같은 폴더에 저장)
            page_output_folder = output_folder
            os.makedirs(page_output_folder, exist_ok=True)
        
            # 파일 이름 및 경로 지정
            image_filename = f"img_{page_num + 1}_{img_index + 1}.jpg"
            image_path = os.path.join(page_output_folder, image_filename)
        
            # 이미지 저장
            image.save(image_path)
            print(f"Saved image: {image_path}")

# Define the paths
pdf_path = "/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_05.pdf"
output_folder = "/Users/sinequanon/Documents/PerfectS/data/images"

# Call the function to extract images and text
extract_images_from_pdf(pdf_path, output_folder)