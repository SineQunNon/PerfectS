import pymupdf4llm

pdf_path = "/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_01.pdf"

md_text = pymupdf4llm.to_markdown(pdf_path)

print(md_text)