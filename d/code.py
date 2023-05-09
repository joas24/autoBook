from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from datetime import datetime, timedelta
import time
import os
import chromedriver_autoinstaller

#날짜
tdy = datetime.today()
tmr = tdy + timedelta(days=1)

#오늘 / 내일
def date_input():
    date_choice = int(input(f"\n-날짜 선택-\n1. 오늘 ({tdy.month}/{tdy.day})  2. 내일 ({tmr.month}/{tmr.day})\n"))
    match date_choice:
        case 1:
            mon = tdy.month
            day = tdy.day
        case 2:
            mon = tmr.month
            day = tmr.day
    return mon, day

#월, 일, 팀플실 입력
def set_date(mon, day, num): 
    Select(driver.find_element(By.XPATH,'//*[@id="reserveMonth"]')).select_by_value(str(mon).zfill(2))
    Select(driver.find_element(By.XPATH,'//*[@id="reserveDay"]')).select_by_value(str(day).zfill(2))
    Select(driver.find_element(By.XPATH,'//*[@id="classRoomNo"]')).select_by_index(num)

#조회하기
def see_one(mon, day, num):
    set_date(mon, day, num)
    list_tbody = driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody')
    for tr in list_tbody.find_elements(By.TAG_NAME, 'tr'):
        print(tr.get_attribute("innerText"))
    
#예약하기
def book(mon, day, num, startH, startM, t=4, people = 2, msg = "스터디"):
    endH = startH + (startM+t)//2
    endM = (startM+t)%2
    
    set_date(mon, day, num)

    Select(driver.find_element(By.XPATH, '//*[@id="reserveStartTimeH"]')).select_by_value(str(startH).zfill(2))
    Select(driver.find_element(By.XPATH, '//*[@id="reserveStartTimeM"]')).select_by_index(startM)
    Select(driver.find_element(By.XPATH, '//*[@id="reserveEndTimeH"]')).select_by_value(str(endH).zfill(2))
    Select(driver.find_element(By.XPATH, '//*[@id="reserveEndTimeM"]')).select_by_index(endM)
    Select(driver.find_element(By.XPATH, '//*[@id="reserveMember"]')).select_by_index(people-2)
    driver.find_element(By.XPATH, '//*[@id="memo"]').send_keys(msg)

    driver.find_element(By.XPATH, '//*[@id="content"]/form/table[3]/tbody/tr/td/a/button').click()
    al = driver.switch_to.alert
    print(al.text)
    al.accept()
    table = driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody')
    for tr in table.find_elements(By.TAG_NAME, 'tr'):
        print(tr.get_attribute("innerText"))

#취소하기
def cancel(mon, day, num):
    set_date(mon, day, num)

    list_tbody = driver.find_element(By.XPATH, '//*[@id="content"]/table/tbody')
    for tr in list_tbody.find_elements(By.TAG_NAME, 'tr'):
        if tr.find_elements(By.TAG_NAME,'td')[-1].get_attribute("innerText")=="예약취소":
            tr.find_elements(By.TAG_NAME,'td')[-1].find_element(By.TAG_NAME, 'a').click()
            aler = driver.switch_to.alert
            aler.accept()
            print(aler.text)
            aler.accept()



#사이트 접속

chromedriver_autoinstaller.install()
    
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver=webdriver.Chrome(options=options)
driver.set_window_size(1400,1000)
driver.get("https://cse.cau.ac.kr/main.php")

driver.find_element(By.XPATH,'//*[@id="top"]/div[2]/div/div[1]/a[5]').click()
driver.find_element(By.XPATH,'//*[@id="sub05"]/div/a[4]').click()
time.sleep(1)


#아이디 비밀번호 입력 / 로그인
done = 0
autoT = 1 #자동입력되는 아이디가 틀릴 경우 0
print("\n6피 팀플실 예약 프로그램")
while not done:

    if os.path.exists("id.txt") and autoT:#자동 로그인
        f = open("id.txt",'r')
        id = f.readline().strip()
        pwd = f.readline().strip()
        f.close()
    else:#직접 로그인
        id = input("\nID : ")
        pwd = input("PWD : ")

    driver.find_element(By.XPATH,'//*[@id="txtUserID"]').send_keys(id)#id 입력
    driver.find_element(By.XPATH,'//*[@id="txtPwd"]').send_keys(pwd,Keys.ENTER)#pwd 입력
    time.sleep(1)

    alert = driver.switch_to.alert
    al_msg = alert.text
    alert.accept()
    if "환영합니다" in al_msg: 
        f = open("id.txt",'w')
        f.write(f"{id}\n{pwd}")
        f.close()  
        done = 1
    else: 
        print("아이디 또는 비밀번호가 틀렸습니다.")
        autoT = 0 #자동 로그인이었을 경우 다시 자동 로그인 방지



#할 일 선택
choice = 0
mon, day, num = 0,0,0
while choice != 4:
    choice = int(input("\n1. 예약 상황 조회\n2. 예약하기\n3. 예약 취소하기\n4. 종료\n"))

    match choice:

        case 1:
            mon, day = date_input()
            num = int(input("\n팀플실(1~6) : "))
            see_one(mon,day,num)

        case 2:
            date_custum = int(input(f"\n- 날짜, 팀플실 -\n1. 최근 조회한대로({mon}/{day} 팀플실 {num})\n2. 직접 입력\n"))

            if date_custum == 2:
                mon, day = date_input() 
                num = int(input("\n팀플실(1~6) : "))
            
            startH = int(input("\nstart hour : "))
            startM = int(input("start minute(1. 정각 2. 30분) : "))-1

            info_custum = int(input("\n- 시간, 인원, 목적 -\n1. 2시간 / 2명 / 스터디\n2. 직접 입력\n"))

            if info_custum == 2:
                t = int(input("\n- 이용 시간 - \n1. 30분\n2. 1시간\n3. 1시간 30분\n4. 2시간\n"))
                people = int(input("\n인원수 : "))
                msg = input("이용 목적 : ")
                book(mon, day, num, startH, startM, t, people, msg)

            elif info_custum == 1: 
                book(mon, day, num, startH, startM)
                
            else: print("정해진 숫자를 입력해주세요.")

        case 3:
            date_custum = int(input("\n- 날짜, 팀플실 -\n1. 최근 조회한대로({mon}/{day} 팀플실 {num})\n2. 직접 입력\n"))
            if date_custum == 2:
                mon, day = date_input()
                num = int(input("\n팀플실(1~6) : "))
            cancel(mon, day, num)
            
        case 4:
            driver.quit()
            break