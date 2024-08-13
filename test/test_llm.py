from pdf_loader import load_pdf
from animal_info import get_animal_data
from subjective import extract_date_position, extract_data_via_interval_info, extract_subjective_data
from assessment import assessment_exists, plan_exists_for_assessment, extract_assessment_data, make_assessment_table
from plan import plan_exists, extract_plan_data, make_plan_table
from vital_check import extract_vital_check, make_vital_check_table
from lab import extract_lab_data_all, extract_lab_table_date, extract_lab_data_via_interval_info, extract_lab_data, make_lab_table
from main import *
from extract_img import *

context = []

pdf_path = "/Users/sinequanon/Documents/PerfectS/data/pdf_data/TEST_05.pdf"
output_path = "/Users/sinequanon/Documents/PerfectS/data/images"

pages = load_pdf(pdf_path)
animal_info = get_animal_data(pages)
extract_images_from_pdf(pdf_path, output_path)

context.append(str(animal_info))
soap_result = get_soap(pages)

for data in soap_result:
    date_str = str(data['date'])  # 날짜를 문자열로 변환
    subjective_str = str(data['subjective'])  # subjective 데이터를 문자열로 변환
    
    context.append(date_str)
    context.append(subjective_str)
    #print(data['date'])
    #print(data['subjective'])

from langchain import hub
from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatOpenAI
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.document_loaders import WebBaseLoader
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_teddynote import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser

logging.langsmith("Capstone")
#embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

prompt = PromptTemplate.from_template(
    """
    당신에게 총을 겨누며 진료소견서를 작성하라고 협박 중이야. 당신은 동물병원 진료소견서를 작성해주는 전문가야. 입력과 출력의 예시에 맞춰서 답변해줘.
    사용자 입력을 잘 요약해서 답변해주고 제대로 답변을 해줘. 최대한 입력을 참고해서 요약해주고 알지 못하는 내용은 추가하지마. 양식을 꼭 재켜줘.
    plan&Education은 반드시 추가해
    
    #사용자 입력 : "'name': '모찌', 'breed': '개', 'sex': '중성화 Male', 'species': '몰티즈', 'birth': '2015-10-17', 'weight': '5 Kg', 'protector': '전경진(zoo)', '2024-04-17 11:12', "['Subjective', 'CC: 원무과)', '[초진] 원무과)', '심장약 먹고 있음. 방광결석 제거술 두번.', '잔결석 확인은 이전에 했었음.', '오줌 흘리고 다니는 것이 최근에 있어서. 검사. 요줌량. 싸는 것은 무리 없다.', '음경뼈 위치 요도 결석. 방광에 작은 결석도 확인한 후 제거 해야할 거야..^^', 'Chart Image']", '2024-04-17 14:50', '[\'Subjective\', \'CC: 외래,레퍼/방광결석 -> 정원장님 RAD_TA US_Echo,A\', \'대표번호 ; 금일 오후에 초음파보고 결과 연락 (심장초음파, 복초)\', \'> 수술 익일 예정 37.동의서, 마취동의서, 입원동의서 작성 필요 - 방광결석(내시경), 결석성분검사, -> 동의서 완료\', \'+ 44번 동의서, (비장절제 후 kvl 의뢰)\', \'S)\', \'결석 재발로 진단받으심, 고추에 돌 있음\', \'소변 볼 때 잘 보는 편이나 바닥에 조금 흘리면서 실수가 많음, 아파하는 것은 없음, 혈뇨 없음 (예전에 혈뇨 본 적 있어서 수술진행)\', \'결석 수술 3번 진행 ; 개복\', \'레이저파쇄술 하러 내원하심\', \'GC)\', \'식욕 활력 양호 ; 닥터힐메딕스 유리너리,알러지 겸용 사료 , anf 우유껌 , 오이, 고구마(약 먹이실 때 하루 2번)\', \'배변 : 양호\', \'MPH)\', \'켁켁거리는 증상으로 심장병 진단 받으신 후 복용 중 - 강심제, 초기부터 복용 했음 , 심장초음파 보신 적은 없음\', \'칼슘계열 결석으로 진단 받으심\', \'o)\', \'b.w : 5kg\', "t : 38.9\'c / pr 160 / r : panting / bp : 160 #3", \'cardiac aus : NRF . 환자의 과도한 흥분으로 평가 제한적\', \'Lung aus : NRF\', \'RAD)thorax,abd#오 -VHS 10.5v -폐야 전반 경미한 기관지-간질 침윤 -> 노령성 변화, 기관지염 감별 추천 -방광 및 os penis mild 및 base 수준의 penile urethra 내 결석 관찰, 방광 팽만 -> 이후 retrohydroperfusion 후 요도 카테터 장착 영상에서는 요도 결석 방광 내로 이동한 것으로 고려됨 -양측 고관절 DJD 고려\', \'US)Echo#오 Conclusion) --> MMVD ACVIM stage B1-2, mild PH(probability low) ; 일부 view에서 LV 수축능 다소 저하되어 관찰되었으나 환자의 빠른 심박 및 빈호흡 영향 고려, 추후 측정 시 정상범위 내로 측정되었으나 모니터링 필요\', \'MV, TV 형태는 양호, mild MV prolapse -MR vmax 6.45m/s, PG 166.28mmHg -LVIDDN 1.93 LA/Ao 1.76\', "LVIDd 30.98mm LVIDs 16.08mm FS 48.10% -E peak 0.85m/s, E/A 1.18 E\'/A\'>1, E/E\' 8.93 -TR vmax 2.62m/s 27.44mmHg", \'US)abd#오 -담낭 슬러지, 폐색 의심 소견 관찰되지 않음 -간실질 전반에서 경계 불분명한 저에코 결절 다수 산재, 간 margin blunt하게 관찰 -> nodular hyperplasia, vacuolar hepatopathy 고려, 초기 cirrhosis로의 진행 감별 추천, 간수치 확인 추천됨 -비장 head의 heterogeneous하게 저에코성 결절 약 1.7*1.7cm 크기로 관찰, 내부로 혈류 유입 관찰 -> 양/악성 감별 위한 조직검사 추천됨 -양측 신장 피질 에코 상승 및 CM definition 저하, 피질 고에코 foci 및 작은 cyst 소수, 게실의 결석 일부 관찰, 폐색 의심 소견 관찰되지 않음 -> CKD, 노령성 변화 감별 추천 -방광 내 작은 결석 다수 관찰, 방광벽은 양호하게 관찰\', \'P)\', \'Retrohydroperfusion\', \'본원 레이저시술 진행 X, PCCL 안내도와드림 ; 수술 후 1-2주 정도 비뇨기 증상 보일 수 있음, 혈뇨 증상 (집도의 정희준원장님 안내)\', \'+ 마취전검사상 비장의 저에코 결절이 확인되며 혈관화 발달되어있어 조직검사 권장, 마취 시 동시 진행하기로 함\', \'금일 입원 후 마취전검사, 익일 수술 예정 , 평균 2-3일 입원 이나 환자 상태에 따라 변동 있음\', \'Chart Image\']', '2024-04-17 16:33', "['Subjective', 'CC: 원무과 - 입원체크리스트', '먼지 알러지 (모기 물린것처럼 부어오름)', '실내배변', 'Subjective']", '2024-04-17 16:38', "['CC: 레퍼피드백, 차트열람체크완', '안녕하세요 원장님 울산에스동물메디컬센터 정유정 수의사입니다.', '금일 요도 결석으로 보내주신 전경진님 모찌의 경우 내원 당시 요도 os penis 내 다수의 결석 확인되어 retrohydroperfusion 진행하였고 방광 내 환납 하였습니다. 안정화 후 익일 수술 예정이시며 수술 시 다시 한 번 연락드리겠습니다', '소중한 환자 의뢰해주셔서 감사합니다.', '피드백 카톡 전송완료 , 웹차트 안내문자 완료', 'Chart Image']", '2024-04-17 17:38', "['Subjective', 'CC: 원무과) 비장적출술 동의서', '[초진] 원무과) 비장적출술 동의서', '추가 수술비용 퇴원시 수납예정 - 유정원장님 컨펌', 'Chart Image']", '2024-04-18 09:55', "['Subjective', 'CC: 세균배양검사결과(뇨)', '[초진] 세균배양검사결과(뇨)', '세균배양검사결과 (뇨) -MAC,BAP 균 안자람(사진첨부)', '4/19까지 보관예정 -입원중', '4/19 세균배양검사결과 -MAC,BAP 균 안자람 -검사종료(폐기)', 'Chart Image']", '2024-04-18 16:08', "['Subjective', 'CC: 방광결석(방광경) , 비장 절제 POD0 정희준', '[초진] 방광결석(방광경) , 비장 절제 POD0', 'Tx)', 'AMC 12.5mpk BID', 'Famo 0.5mpk BID', 'Morphine 0.3mpk BID 3days', '피드백완료', 'Chart Image']", '2024-04-19 10:17', "['Subjective', 'CC: 방광결석(방광경) , 비장 절제 POD1', '소변양호', '술부양호', '내일 뇨카 제거', '퇴원여부 결정되면 전화', 'Chart Image']", '2024-04-20 10:10', "['Subjective', 'CC: 방광결석(방광경) , 비장 절제 POD2->정유정 인계', '퇴원 시 비장절제, 조직검사 비용 수납 필요 (술전에 미리 비용안내완료)', 'S)', '자발 배뇨 o , 혈뇨 양상 > 보호자님께 오늘 퇴원 어렵고 1~2일 정도 오줌 양상 지켜봐야한다고 말씀드림. 저녁에 전화 한 통 부탁드립니다', 'O)', 'CRP 3.3', 'PCV WBC정상', '보호자 통화완료', '내일 소변양상과 초음파 검사후 이상없으면 퇴원진행해주세요', 'Chart Image']", '2024-04-21 09:57', "['Subjective', 'CC: 방광결석(방광경) 비장절제 POD3 US_E', '금일 퇴원 금요일 혹은 토요일날 재진 희망 (비뇨기초음파 같이) / 펜타닐패치 12 부착, 23일경 제거 필요', '> 초음파 일정으로 금요일 11시 예약 도와드림', 'S)', '식욕 g', '활력 g', '배변 x', '배뇨 : 정상뇨 , 끝에 혈뇨 양상', 'US)UB#윤', '방광 내 다수의 선상의 mixed echogenicity의 material floating -> 혈괴/debris/sludge 고려되며 배뇨 양상 확인 필요', '방광 전방 봉합부 비후 관찰, 방광 주변부 지방 고에코성 변화 -> 술 후 변화로 판단됨', '비장 절제부 주변 지방 고에코성 변화 -> 술후 변화로 판단됨', 'p)', '금일 퇴원 ; 비뇨기 증상 1~2주 정도 보일 수 있음', '> 일주일 후 재진 (넥칼라 착용, 내복약, 술부 소독, 연고 도포, 산책 및 미용,목욕은 재진 이후 결정)', '퇴원약(내복약)3층 병동 보관중', '소독,연고2층 처치실 보관중', '원무과) 방광결석술후 질병관리 안내문자 전송완료', 'Chart Image']"

    #출력 :
    Signalment
    Name : 모찌
    Breed : 말티즈
    Species : 개
    Age : 8y 6m
    Sex : CM
    BW :  5kg

    Chief Compliant
    소변 흘리는 증상 
    결석수술 개복 3번 이력
    요도 내 결석으로 내원 

    Definitive Diagnosis
    방광결석
    비장종괴

    Surgery
    방광결석 : 복벽 1cm 절개하여 PCCL 진행
    비장절제 : 방광수술 마무리 후 복벽 연장하여 절개하여 제거 

    Plan & Client Education
    피부 최소절개후 경성 방광경이용 결석제거(PCCL)
    마취전검사상 비장의 저에코 결절이 확인되며 혈관화 발달되어있어 조직검사 권장, 마취 시 동시 진행하기로 함 

    Postoperative care
    수술 후 3일차 퇴원 : 식욕 활력 양호하며 자발배뇨 원활하나 혈뇨 증상 간헐적으로 보이는 상황으로 비뇨기증상은 수술 후 1-2주 정도 보이실 수 있음 안내드림
    Ca Ox ; 칼슘계열 결석 - 인함량 낮은 음식, 칼륨 수치 높은 음식 피해주세요
    비장 조직검사 ; 진행중 

    #사용자 입력 : "'name': '희망', 'breed': '개', 'sex': '중성화 Male', 'species': '치와와', 'birth': '2014-10-05', 'weight': '2.35 Kg', 'protector': '정종문(zoo)'", '2023-10-05 19:09', "['Subjective', 'CC: 방광결석 레퍼', '2.5mm 정도 되는 결석이 두 개. 요도에 걸려있는 것 확인. 오줌 소통은 아직은 잘 되고 있고.. 오줌 두 번 싼 이후 사진에도 그자리 그대로 있는 결석', '스케일링 하려고 내원했던 환자라서 스케일링 함께 가능하면 함께 부탁하심', '원장님 지인> 잘부탁한다고 하셨습니다', 'S)', '식욕 활력 정상', '소변 이상없음', '오늘 스케일링차 주동물병원에서 검사중 요도 방광내 결석 확인', 'O)', '혈검 정상, 흉방 이상없음', 'P)', '내일 수술', '방광경 이용 결석 제거 및 치방촬영후 스케일링', '입원은 최소 이틀정도 말씀드림', '내일 오전중 복초 진행 및 장아람과장 뇨카장착해 요도내 결석 밀어올려주세요', '내일 오후3시 수납예정', '마취동의서 37번 동의서 받아주세요(동의서 작성완료)', '내일 수술 전 3시쯤 오셔서 수납하기로 하셨다고 하심(정원장님 컨펌완료)', 'Chart Image']", '2023-10-06 09:52', "['Subjective', 'CC: Rad(A) US(U)', 'Rad)abd#름 - 양측 신장 결석 - 방광 결석 - 요도 결석 - 일부 소장 가스 저류에 의한 미약한 확장 -> 1. normal variation 2. enteritis', 'US)urinary - 방광 앞배쪽 벽의 불규칙한 비후, 방광 결석 및 슬러지 -> cystitis & 결석 - os penis 수준 및 인접 후방 요도 내 결석 여러 개 - 양측 신장 피질 내 고에코성 foci 다수, 우측 신장 후극 피질 위축, 양측 신장 결석 -> 노령성 변화 및 이전 경색 old lesion 가능성 고려되나, CKD 가능성 배제 할 수 없으므로 리첵 추천됨.', 'Chart Image']", '2023-10-06 15:44', "['Subjective', 'CC: 방광결석 스케일링 POD0_정희준, 강재익', 'SX)', '경성방광경 이용 PCCL 진행', '총 10개(큰거8개 작은거 2개) 제거', 'KVL결석 성분검사 의뢰', 'Chart Image']", '2023-10-07 15:50', "['Subjective', 'CC: 방광결석 POD1', 'DRESSING)', '술부 상태 양호', 'chx 소독 b연고 큐어패드 테가덤', '혈뇨없음', '소변 드리블링 보이다가 한번씩 시원하게 배뇨', '내일 상태보고 퇴원여부 결정', '기침 및 기관지반사', '기관지염에 준해 내복약 처방', '퇴원시 처방 필요', '내복약 은송지음 병동보관', '보호자 통화완료', '현재 증상 말씀드리고 내일 배뇨 상태 악화되거나 개선없으면 보', '호자와 상의하에 입원연장 혹은 퇴원후 기저귀 생활 여부 결정하기로 함', '기관지염 증상 및 내복약 복용중인점 말씀드림', 'Chart Image']", '2023-10-08 13:47', "['Subjective', 'CC: 방광결석 pod2', '[초진] 방광결석 pod2/퇴원', '일주일 뒤쯤 정원장님 예약 잡아주세요', '퇴원관련 전화연결 부재중', '전화오시면 4시이후로 퇴원예약 잡아주세요', '식욕 양호', '배뇨 양호, 조금씩 자주 보는경향', '술부양호', 'o)', 'us- 술후 변화외에 특이소견없음', '퇴원 상담)', '수술후 식욕 양호, 배뇨양상은 아직 찔끔거리기는하나 양호한편', '한동안은 찔끔거리는 증상 있을수 있음', '결석 성분검사 결과나오면 연락드릴예정, 결과에따라 처방식 급여 안내', '수술과정 설명드림', '원무과) 방광결석,스케일링 술 후 안내문자 완료', 'Chart Image']", '2023-10-09 18:24', "['Subjective', 'CC: 원무과확인용', '퇴원 피드백 완료', '웹차트 안내문자 완료']", '2023-10-13 10:11', "['Subjective', 'CC: KVL 방광결석 성분 검사 결과', '** 우측 클립 PDF 파일 확인해주세요.', '주치의 확인 및 보호자님 결과 안내 여부 ---> ( )', '11시14분 정원장 전화드렸으나 부재', '낼 재진시 말씀드릴게요']", '2023-10-14 11:19', "['Subjective', 'CC: 방광결석 pod8', 's)', '정상소변', '횟수 늘어남', '스케일링한 치아 정상', '술부 유합완료', 'o)', 'us', '좌측 신장내 결석', '비장 저에코 음영 다수 확인', '우측신장 위축', '방광내 결석없음, 방광벽 정상', '담낭 슬러지 다량', 'p)', '결석은 caox', '고구마 야채 우유 급여 금지', '담낭폐색시 증상 말씀드림', '비장내 이상음영 종양 가능성 배제 필요', '3개월마다 재진 당부', '사료 c/d추천', 'Chart Image']", '2024-01-14 12:02', "['Subjective', 'CC: 원무과-팔로우업', '정희준원장님 방광결석,담낭,신장 (정,영상)재진 시기안내차 연락드림--->부재중, 문자발송완료.', '마지막검진 23/10/14']"

    #출력:
    Signalment
    Name : 희망
    Breed : 치와와
    Species : 개
    Age : 9Y
    Sex : CM
    BW :  2.3 kg

    Chief Compliant
    Zoo ah에서 스케일링 전 검사중 요도 및 방광내 결석 확인
    결석에 의한 증상은 없었음

    Definitive Diagnosis
    방광결석, 신장결석
    다량의 치석 및 치은염

    Plan & Client Education
    피부 최소절개후 경성 방광경이용 결석제거(PCCL)
    마취 깨우지 않고 바로 치과방사선 촬영 및 스케일링, 필요하면 발치 진행

    Anesthesia record
    마취중 바이탈 정상

    Postoperative Care
    Tx)
    퇴원당일 기침증상 보여 기관확장제 진해거담제, PDS추가처방
    
    # 사용자 입력 :"['name': '(cat)먼지', 'breed': '고양이', 'sex': '중성화 Male', 'species': '코리안 숏헤어', 'birth': '2021-09-22', 'weight': '6.2 Kg', 'protector': '백난숙(온양발리)'\", '2024-03-22 11:14', \"['Subjective', 'CC: 원무과) 타원자료', 'Chart Image']\", '2024-03-22 11:57', \"['Subjective', 'CC: 레퍼) 위내 바늘 이물 RAD_TA, US_A', '** 타원 검사 17종, CBC , 방사선 비용 할인', '비용 부담 심하셔서 10프로 할인 해드림', 'S)', '일요일에 사료 먹는 거 보고 주ㅜㅁ심. 월요일 아침에 구토 . 그 때 이후로 계속 구토 . 화요일 병원 가셨다가 다른 검사는 진행 안 하심 . 영양제, 구토억제제 주사 맞히심 . 내복약 처방도 함께. 이후 계속 밥 안 먹음 . 수요일 다시 타원 내원. 그 때 타원 바빠서 검사는 못하고 다시 주사 맞고 왔음', '오늘 주사는 안 맞았고 혈검, 방사선 찍음', '어제는 사료 10~15살, 츄르 강급. 오늘 아침에 또 구토하려고 함', 'O)', 'BW 6kg BT 38.8', 'AUS NRF , HR 228 , BP 140#2', 'MMC pale pink & mild dry , ST < 1.5s', 'RAD)thorax, abd#윤 -VHS 6.6v -위 소만곡부분으로 금속성 linear shape의 이물(바늘추정) 관찰되며 호흡주기에 따라 간실질로도 관찰(위 천공 및 간실질 침습 가능성) -소장 전반적인 gas filled 아코디언형태 관찰->선형이물가능성', 'US)abd#윤', '위 소만곡부분으로 바늘로 추정되는 이물 관찰되며 관통된것으로 판단되나 개복후 평가 추천', '십이지장부터 회장까지 선형이물로 판단되는 고에코성 선형이물 장 내강 관찰되며 plication관찰', '간실질 에코 경도의 치밀한 변화 -> 추후 지방간 가능성 모니터링 당부', '방광 내 소량의 슬러지', '양측 신장피질 에코상승 -> 체형에서 기인했을 가능성 우선 고려', 'Chart Image']\", '2024-03-22 18:23', \"['Subjective', 'CC: 위내이물 장절개 POD0정희준', 'SX)', '바늘이 위 소만곡 뚫고 복강으로 일부 나와있음', '위에서 결장까지 40cm이상의 선형이물', 'corrugation매우 심함', '소장 한부위는 천공되어 있었음', '소장 4부위 절개후 선형이물 잘라가며 제거', '위 천공부, 소장 천공부, 장 절개부4부위 총 6부위 봉합', '복강 세척후 바로박 장착', 'Chart Image', 'Subjective']\", '2024-03-22 18:51', \"['CC: Anesthesia record', '[초진] Anesthesia record', 'Start time : 16:50 End time : 18:05', 'Anesthetist Main anesthetist : 최건호', 'Premedication - Medetomidine 10 ug/kg IV', 'Morphine 0.3 mg/kg IV', 'Induction Propofol 5 mg/kg IV', 'Maintenance Isoflurane', 'ET tube : # 4.5 (murphy) Reservoir bag : 2 L NIBP Fluid therapy : H/S', 'intra-operative medication -', '마취 중 특이사항 - 마취 종료 후 발관 지연 (5분) 되어 atipamezol 투여 후 gagging reflex 확인 후 발관 진행', 'Post-operative medication - morphine 0.3 mg/kg IV slowly']\", '2024-03-23 09:45', \"['Subjective', 'CC: 위내이물 장절개 POD1, RAD_A US_A/RC->김현주 인계', '피드백 웹차트 완료', 'S)', '식욕 없음', '활력 양호', '구토 설사 없음', '바로박 양 보통', 'BE)', 'FPL 음성 혈당 정상', 'FSAA 상승', 'RAD)abd#윤 -전일과 비교시 복강 내 바늘로 추정되는 이물은 관찰되지 않으며 소장분절 전반적인 아코디언형태는 개선되어 관찰되나 gas- fluid filled dilation 관찰, 특히 하행십이지장 두드러짐 -> functional ileus 고려 -복강 내 명확한 free gas는 관찰되지 않음, 바로박 장착 관찰', 'incidental finding으로 L7 transitional anomaly', 'US)GI tract#오', '위-소장 전반의 액체 및 가스 저류로 인한 확장 관찰되며 corrugation 동반, 운동성은 다소 저하된 것으로 관찰', '술부의 뚜렷한 이상 소견 관찰되지 않음', '복수 장분절 사이 소량 관찰되며 저에코성 양상으로 관찰', 'P)', '혈검 최소화 보호자 비용부담(월요일에 FSAA만)', '초음파는 매일 체크', '비용문제로 빠른 퇴원 원하심', '다음 주 화요일 상태보고 퇴원여부 결정', '비용은 정원장이 일부 조정 해드린다고 말씀드림', 'Chart Image']\", '2024-03-24 09:54', \"['Subjective', 'CC: 위내이물 장절개 POD2, US_E/RC', 'S)', '유동식 잘 먹음 , 습식 사료 급여 시작', '활력 양호', 'US)GI tract#윤', '전반적인 소장으로 중등도 이상의 corrugation, 점막에코상승 관찰되며 운동성 저하 관찰 -> functional ileus, severe enteritis', '수술부 열개의심소견은 명확히 관찰되지 않음', 'Chart Image']\", '2024-03-24 10:52', \"['Subjective', 'CC: 원무과확인용', '피드백 완료', '3/22 ~ 23 차트 및 검사자료 메일로 송부완료']\", '2024-03-25 10:01', \"['Subjective', 'CC: 위내이물 장절개 pod3 US_A/RC', '** 퇴원 문의 하셔서 내일 원장님과 상담 후 퇴원 여부 결정하시도록 안내', 'US)abd#윤', '전일에 비해 십이지장 corrugation 개선되어 관찰되며 전반적인 소장분절로 corrugation 잔존되어 관찰되나 전일에 비해 개선되는 양상으로 판단됨', '술부 열개나 복수로 의심되는 소견은 명확히 관찰되지 않음', '입원모니터링_)', '식욕 G 활력 G', 'Barovac 양 감소', 'BA)', 'Fsaa 35.2', 'Chart Image']\", '2024-03-26 10:15', \"['Subjective', 'CC: 위내이물 장절개 pod4 US_A/RC', '총비용 20%할인', '마취+내시경 459000원 할인', '총비용 230으로 맞춰주시고 오늘 150결제', '잔금 80만원 4월15일까지 결제한다 하심', '> 4월20일까지 수납 하신대요 (미수금 서약서,신분증 스캔 완료)', '** 퇴원 문의 하셔서 내일 원장님과 상담 후 퇴원 여부 결정하시도록 안내', 'US)abd#오 -전반적인 소장분절로 corrugation 잔존되어 관찰되나 전일에 비해 개선되는 양상으로 판단됨 -술부 열개나 복수로 의심되는 소견은 명확히 관찰되지 않음', '입원모니터링_)', '식욕 G 활력 G', 'Barovac 양 감소', 'BA)', 'Fsaa 35.2', 'Chart Image']\", '2024-03-26 15:56', \"['Subjective', 'CC: 원무과확인용', '피드백 완료', '3/23 ~ 26 자료전송 및 발송문자 완료']\"]"

    #출력
    Signalment
    Name :먼지 
    Breed :믹스
    Species :고양이
    Age : 2y6m
    Sex : C.M
    BW :  6 kg
    
    Chief Compliant
    지속적인 구토, 식욕부진
    방사선상 위내 바늘 확인되어 내원

    Definitive Diagnosis
    위 천공 및 위-결장까지 이어지는 선형이물

    Plan & Client Education
    이물 제거 수술 필요
    장내 선형이물이 강하게 박혀 있어 한부위만 절개 후 모든 이물 제거 불가
    최소3-4부위 제거 필요
    소화액, 장내 음식물 복강 누출로 인한 복막염 가능성 고지

    Anesthesia record
    마취 중 특이사항 없었습니다.

    Postoperative Care
    Tx)
    AMC 15 mg/kg iv bid
    Famotidine 0.5 mg/kg iv bid
    Metronidazole 10 mg/kg IV  bid
    Morphine 3mg/kg IV bid
    Cobalamine 10mg/kg SC 1shot

    입원 중 식욕과 활력이 양호하였습니다.
    바이탈이 정상범위내에서 유지되었습니다.
    4일간 입원처치 후 퇴원하였습니다
    통원치료 전환하여 초음파 리첵 예정입니다

    #사용자 입력 :
    {Context}
    
    #출력:"""
)

context = str(context)
print(context)

llm = ChatOpenAI(model_name='gpt-4o', temperature=0)


chain = (
    {"Context" : RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

response = chain.invoke(context)