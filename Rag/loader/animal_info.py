def extract_data_via_points(pages, x, y1, y2):
    for page in pages:
        metadata = page.metadata
        coordinates = metadata['coordinates']

        if metadata['page_number'] == 1 and coordinates['points'][0][0] == x \
            and coordinates['points'][0][1] > y1 \
                and coordinates['points'][1][1] < y2:
            return page.page_content
    
    return "Not Found"

def get_animal_data(pages):
    info = {}
    # 동물 정보 추출
    info['name'] = extract_data_via_points(pages, 265.62, 141, 150)
    info['breed'] = extract_data_via_points(pages, 78.54, 158, 167)
    info['sex'] = extract_data_via_points(pages, 78.54, 174, 184)
    info['species'] = extract_data_via_points(pages, 265.62, 157, 167)
    info['birth'] = extract_data_via_points(pages, 265.62, 174, 184)
    info['weight'] = extract_data_via_points(pages, 78.54, 209, 218)
    # 보호자 이름 추출
    info['protector'] = extract_data_via_points(pages, 214.6, 107, 116)
    return info