import requests
import sys, os
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin


###SQL 인젝션 공격 기법
#Classic SQLI
#Blind SQLI
#Time-Based SQLI
#Error-Based SQLI
#UNION-Based SQLI
#Out-of-band SQLI
#Second-Order SQLI

def exploitsFile1(x_file1):
    with open(x_file1,'r') as file:
        explits = file.read().splitlines()
    return explits

#Classic SQL Injection(해당 파일들)
def classicSQLI(action_url, form_data):
    #form_data 딕셔너리를 이용하여 필요한 정보 사용
    #input, textarea가 사용자가 입력하는 값이
    method = form_data["method"]
    input_fields = form_data["input_fields"] #key: 'name','type' 
    textarea_fields = form_data["textarea_fields"] #key: 'name'
    # select_fields = form_data["select_fields"] #key: 'name'
    # button_fields = form_data["button_fields"] #key: 'name'

    #데이터를 처리하는 파일에서 취약점 점검 시작
    print(f"\nAttack URL: {action_url}")
    if method == "GET":
        print("Method: GET")
    elif method == "POST":
        print("Method: POST")
        #exploit code 불러와서 담기
        
        x_file1 = "./VulnerabilityList/classic_sqli_post.txt"
        exploits = exploitsFile1(x_file1)
        #print(f"exploits: {exploits}")
        
        #HTML->input->type
        #text, password, radio, checkbox, submit, file, email, number, date, color
        #값을 작성하여 조작할 수 있는 text, password, email을 활용
        for exploit in exploits:
            data = {}
            for field in input_fields:
                name = field.get("name")
                if name:
                    data[name] = exploit
            for field in textarea_fields:
                name = field.get("name")
                if name:
                    data[name] = exploit
            print(f"[*]Data: {data}") 
            response = requests.post(action_url, data)
            # print(response.text)

            #[위험, 주의, 양호]- 해당 키워드 주의에 해당
            error_keywords = ['SQL', 'SELECT', 'syntax', 'version', 'MySQL', 'MariaDB']
            for keyword in error_keywords:
                if keyword in response.text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    body_content = soup.find('body')
                    if body_content:
                        error_message = body_content.get_text().strip()
                        print(f"Attack Detected: {exploit}")
                        print(f"Error Message: Caution")
                
                break
            logic_keywords = ['', '', '', '', '', '']

    else:
        print("Error occurred while attempting(POST/GET)")


# def BlindSQLI():
#     return
# def TimeBasedSQLI():
#     return
# def ErrorBasedSQLI():
#     return
# def UNIONBasedSQLI():
#     return
# def OutofbandSQLI():
#     return
# def SecondOrderSQLI():
#     return


#main에서 매개변수로 전달된 url, check_url 받아와서 점검 항목 수행
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Error code: url[1], check_url[2] 인자 전달받지 못함")
        sys.exit(1)
    url = sys.argv[1]
    urls_json = json.loads(sys.argv[1])

    #정적 콘텐츠 제공하는 확장자 제외(.jpg, .jpeg, .png, etc., .css, .js)
    static_extensions = {'.jpg', '.jpeg', '.png', '.css', '.js'}
    check_files = [file for file in urls_json if os.path.splitext(file)[1] not in static_extensions]
    #print(f"check_files: {check_files}")

    #취약점(SQL Injection)에 해당되는 파일 식별
    for file in check_files:
        # print(f"\nChecking {file}")
        #페이지 내용 가져오기
        response = requests.get(file)
        soup = BeautifulSoup(response.text, 'html.parser')
        #form 태그 찾기 + input, textarea, select, button
        form = soup.find('form')
        if form is None:
            print(f"No forms found in {file}\n")
            continue
        #해당 데이터를 분석 후 저장할 딕셔너리
        form_data = {
            #데이터 전송과 목적지 확인 
            "method" : form.get('method', '').upper(),
            "action" : form.get('action',''),
            "input_fields": [],
            "textarea_fields": [],
            "select_fields": [],
            "button_fields": []            
        }
        # print(f"||Form method||: {form_data['method']}")
        # print(f"||Form action||: {form_data['action']}")
        #input 태그 속성 데이터 식별
        # print("||Input field||")
        inputs = form.find_all('input')
        for i in inputs:
            input_info = {
                "name": i.get('name'),
                "type": i.get('type')
            }
            form_data["input_fields"].append(input_info)
            # print(f"name: {i.get('name')}, type: {i.get('type')}")
        #textarea 태그 속성 데이터 식별
        # print("||Textarea field||")
        textareas = form.find_all('textarea')
        for i in textareas:
            textarea_info = {
                "name": i.get('name')
            }
            form_data["textarea_fields"].append(textarea_info)
            # print(f"name: {i.get('name')}")
        #select 태그 속성 데이터 식별
        # print("||Selects field||")
        selects = form.find_all('select')
        for i in selects:
            select_info = {
                "name": i.get('name')
            }
            form_data["select_fields"].append(select_info)
            # print(f"name: {i.get('name')}")
        #button 태그 속성 데이터 식별
        # print("||button field||")
        buttons = form.find_all('button')
        for i in buttons:
            button_info = {
                "name": i.get('name')
            }
            form_data["button_fields"].append(button_info)        
            # print(f"name: {i.get('name')}")

        #Classic SQLI함수 호출
        action_url = urljoin(url, form_data["action"])
        classicSQLI(action_url, form_data)

        #일시적 점검을 위한 중단
        break
  