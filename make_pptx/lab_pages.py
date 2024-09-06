from loader.lab import get_pptx_tables
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt



def make_lab_page(prs, pdf_path):
    df = get_pptx_tables(pdf_path)
    print(df)
    if not df.empty:
        slide_layout = prs.slide_layouts[1]  # 빈 슬라이드
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        if title:
            title.text = "Lab Table"
        
        body_shape = None
        for shape in slide.shapes:
            if shape.has_text_frame:
                body_shape = shape
        
        # 텍스트 상자가 발견되면 제거합니다.
        if body_shape:
            sp = body_shape._element  # 텍스트 상자의 XML 요소를 가져옴
            slide.shapes._spTree.remove(sp)

        # 테이블을 삽입할 위치와 크기 설정
        x, y, cx, cy = Inches(0.5), Inches(3), Inches(8), Inches(2.5)

        # 날짜 컬럼을 헤더로 사용하므로, 중복된 날짜는 제거하여 헤더로 생성
        dates = df['date'].unique()

        # 행은 '검사명'이기 때문에 3개(검사명 + 범위), 열은 날짜 개수 + 1 (첫 열은 검사명, 범위 등)
        rows = len(df['검사명'].unique()) + 1  # 검사명 행과 범위 행
        cols = len(dates) + 1

        table = slide.shapes.add_table(rows, cols, x, y, cx, cy).table

        # 첫 번째 열 너비를 넓게 설정
        table.columns[0].width = Inches(2.0)

        # 헤더에 날짜를 추가
        for col_idx, date in enumerate(dates, start=1):
            cell = table.cell(0, col_idx)
            cell.text = str(date)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(91, 155, 213)  # 파란색
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].font.size = Pt(15)
            cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 흰색
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # 검사명, 범위 추가 (첫 번째 열에 검사명과 범위 표시)
        test_names = df['검사명'].unique()
        for row_idx, test_name in enumerate(test_names):
            # 검사명
            cell = table.cell(row_idx + 1, 0)
            cell.text = test_name
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(91, 155, 213)  # 회색
            cell.text_frame.paragraphs[0].font.size = Pt(15)
            cell.text_frame.paragraphs[0].font.bold = True
            cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)  # 흰색
            cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # 결과값 및 범위 추가
        for col_idx, date in enumerate(dates, start=1):
            filtered_data = df[df['date'] == date]
            for row_idx, test_name in enumerate(test_names):
                result_row = filtered_data[filtered_data['검사명'] == test_name]

                # 검사 결과 값 추가
                result_cell = table.cell(row_idx + 1, col_idx)
                value = result_row['결과값'].values[0]
                status = result_row['status'].values[0]
                if status == '▲':  # 상태 표시
                    result_cell.text = f"{value}({status})"
                    result_cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 0, 0)  # 빨간색
                elif status == '▼':
                    result_cell.text = f"{value}({status})"
                    result_cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 255)  # 파란색

                else:
                    result_cell.text = str(value)

                # 셀 스타일 적용
                result_cell.fill.solid()
                result_cell.fill.fore_color.rgb = RGBColor(255, 255, 255)  # 회색
                result_cell.text_frame.paragraphs[0].font.size = Pt(13)
                result_cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    else:
        print("lab table is empty")