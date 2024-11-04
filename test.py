from make_pptx.lab_pages import get_pptx_AnionGap_and_other_tables
pdf_path = "/home/pjw/IBDP_test2.pdf"

x, y = get_pptx_AnionGap_and_other_tables(pdf_path)

print(x)

print(y)