from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from dotenv import load_dotenv
from log import Log
import json
import csv
import datetime
import time
import os 






class Selenium():
  '''
  Selenium 활용한 크롤링 공통 함수 정리
  '''
  
  def __init__(self, headless: bool = False):
    try:
      # log 설정
      self.log = Log(self.__class__.__name__).logger

      # .env 파일 로드
      load_dotenv()

      # user_agent 가져오기
      self.user_agent = os.getenv('USER_AGENT')

      # chrome driver option 생성
      self.driver_option = webdriver.ChromeOptions()

      # Selenium headless 설정
      if headless:
        self.driver_option.headless = True
      elif not headless:
        self.driver_option.headless = False

      # Selenium Option 설정
      self.options = {
        'disable_gpu' : 'disable-gpu',
        'lang'        : 'lang=ko_KR',
        'User_Agent'  : f'user-agent={self.user_agent}',
        'window-size' : '1920x1080'
      }

      for i in self.options.values() :
        self.driver_option.add_argument(i)

      # 불필요한 에러 메세지 삭제
      self.driver_option.add_experimental_option("excludeSwitches", ["enable-logging"])
      self.driver_option.add_experimental_option('excludeSwitches', ['enable-automation'])
      self.driver_option.add_experimental_option('useAutomationExtension', False)

      # 브라우저 꺼짐 방지 옵션
      self.driver_option.add_experimental_option("detach", True)

      # 크롬 드라이버 버전 설정: 버전명시 안하면 최신
      self.service = Service(executable_path=ChromeDriverManager().install())

    except Exception as ex:
      self.log.exception(f'Init 에러 {ex}\n')

  def set_driver(self) -> webdriver.Chrome: 
    """
    driver 생성
    return : `driver`
    """

    self.driver = webdriver.Chrome(service=self.service, options=self.driver_option) 
    return self.driver

  def open(self, url: str) -> None:
    """
    Selenium 열기
      param 
        url : `접속할 url`
    """
    try:
      self.driver.get(url)
      self.driver.implicitly_wait(10)
      self.log.info(f'----- Open url: {url} -----\n')
    except Exception as ex:
      self.log.exception(f'----- Open 에러  -----\n{str(ex)}')

  def quit(self) -> None:
    """
    Selenium 종료
    """
    self.log.info('----- 셀레니움 종료 -----\n')
    time.sleep(2)
    self.driver.quit()  

  def date_replace(self, date: str) -> str:
    """
    날짜 YYYY-MM-DD 형식으로 바꾸기
      param
        date: `날짜`

      return 
        date: `YYYY-MM-DD 형식`
    """
    date = date.replace('.', '').replace('-','')
    if len(date) == 6:
      date = f'20{date}'
    date = datetime.datetime.strptime(date,'%Y%m%d')
    return str(date)  
  
  def make_csv(self, 
              file_path: str, 
              field_names: list,
              data_list: list,
              file_name: str = None) -> None: 
    """
    csv 파일 만들기
      params
        file_path: `파일 경로`\n
        field_names: `csv 헤더 필드 리스트`\n
        data_list: `데이터 리스트`\n
        file_name: `파일 이름`\n
    """
    # 파일 경로 없으면 생성
    if not os.path.isdir(file_path): 
      os.mkdir(file_path)

    if file_name == '' or file_name == None:
      # 현재 시간 가져오기
      current_time = datetime.datetime.now()
      # 원하는 포맷으로 포맷팅
      formatted_time = current_time.strftime('%Y-%m-%d')

      # 2023-08-01.csv
      filename = f'{file_path}/{formatted_time}.csv'
    else:
      filename = f'{file_path}/{file_name}.csv' 

    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
      csv_writer = csv.DictWriter(csvfile, fieldnames=field_names)
      
      # 헤더를 쓰기 전에 필드 이름을 확인하고 쓰기
      csv_writer.writeheader()
      
      for data in data_list:
        csv_writer.writerow(data)

    self.log.info(f'{filename} 파일에 데이터 {len(data_list)} 개 저장 완료!\n')

  def get_element_by_xpath(self, 
                          xpath: str,
                          print_elem: bool = False):
    """
    element 가져오기
      params
        xpath: `태그 xpath`
      
      return
        elem: `태그 element`
    """
    try:
      elem = self.driver.find_element(By.XPATH, xpath)

      if print_elem == True:
        self.print_elem(elem)
      return elem
    except NoSuchElementException as ex:
      self.log.exception(f'----- Element 가져오기 에러 -----\n{str(ex)}')



  def get_elements_by_ul(self, 
                        ul_xpath: str, 
                        print_elem: bool = False):
    """
    ul 태그로 list 가져오기
      params
        ul_tag: `ul 태그 xpath`
      
      return
        elem: `태그 element`
    """
    try:
      elem = self.driver.find_element(By.XPATH, ul_xpath)
      elem = elem.find_elements(By.TAG_NAME, 'li')

      if print_elem == True:
        self.print_elem(elem)
      return elem
    except NoSuchElementException as ex:
      self.log.exception(f'----- Element 가져오기 에러 -----\n{str(ex)}')

  def get_elements_by_tbody(self,
                            tbody_xpath: str,
                            print_elem: bool = False):
    """
    tbody 태그로 list 가져오기
      params
        tbody_xpath: `tbody 태그 xpath`
      
      return
        elem: `태그 element`
    """
    try:
      elem = self.driver.find_element(By.XPATH, tbody_xpath)
      elem = elem.find_elements(By.TAG_NAME, 'tr')

      if print_elem == True:
        self.print_elem(elem)
      return elem
    except NoSuchElementException as ex:
      self.log.exception(f'----- Element 가져오기 에러 -----\n{str(ex)}')


  def click_element_get_url(self, elem) -> str:
    """
    element 클릭 후 해당 url 리턴
      params
        elem: `element`
      
      return
        url: `클릭한 페이지 url`
    """

    #  클릭
    self.actions = webdriver.ActionChains(self.driver).move_to_element(elem).click(elem)
    self.actions.perform()
    self.driver.implicitly_wait(10)

    url = self.driver.current_url
    return url
  
  
  def elem_click(self, elem) -> None:
    """
    element 클릭 
      params
        elem: `'클릭할 페이지' 태그 element`
    """

    # 클릭
    actions = webdriver.ActionChains(self.driver).move_to_element(elem).click(elem)
    actions.perform()
    self.driver.implicitly_wait(10)

  def page_back(self) -> None:
    """
    뒤로가기 함수
    """
    self.driver.back()
    self.driver.implicitly_wait(10)

  def page_forward(self) -> None:
    """
    앞으로 가기 함수
    """
    self.driver.forward()
    self.driver.implicitly_wait(10)

  def print_elem(self, elem, text:bool = False) -> None:
    """
    element 출력
      params
        elem: `element`
    """
    if text == True:
      for i in elem:
        self.log.info(i.text)
    elif text == False:
      for i in elem:
        self.log.info(i)