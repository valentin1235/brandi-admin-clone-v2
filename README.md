## Backend Part Introduction

Fasion startup admin page building. 

#### Topic 
 (주)브랜디 어드민 페이지 클론 프로젝트

#### Team 
 프론트앤드 2명(김승준, 최예지), 백앤드 3명(윤희철, 이소헌, 이종민)

#### Project Period 
  2020.03.22 - 2020.04.18

#### Coworking 
- Trello를 스크럼방식 협업
- 주단위 백로그작성
- 일단위 스탠드업미팅
         
## 담당 개발 내역
#### Modeling
- 초기 데이터베이스 스크립트 생성 : 테이블, 외래키 관계설정 
- 셀러, 상품, 기획전 데이터에 선분이력 적용
- 데이터의 새로운 이력이 생성되면 이전 선분을 끊어주고 새로운 이력의 시작 날짜를 일치하도록 설계 

#### Flask 프로젝트 초기 설계
- MVC layered pattern(model, service, view)
- Blueprint(라우팅 경로 설정)
- config.py : database, redis 정보 정의
- connection.py : database, redis connection 관리
- app.py : Flask app 생성
- manage.py : 프로젝트 실행
- requirements.txt : 개발 환경 공유

#### 전체 셀러 리스트 표출
- Pagination 
- Keyword Searching : 이름, 이메일, 전화번호 등을 통한 셀러 검색

#### 셀러 리스트 엑셀 다운로드
- 키워드 검색결과를 excel로 만들어줌
- pandas로 로컬에 엑셀파일 생성 후 S3에 업로드하여 다운로드 링크 리턴

#### 셀러 상태 변경
- 선분이력 고력한 이전 이력 중단과 새로운 이력 생성

#### 이미지 리사이즈 & 업로더 작성(utils.py)
- pillow : 이미지 리사이즈
- IO : 리사이즈 된 pillow 객체를 메모리상에 bytes 형태로 일시적으로 저장
- boto3 client : 메모리상의 bytes를 S3에 업로드 후 url 리턴

#### S3 버킷 생성 / 관리

#### 기획전 등록
- Flask validator를 통한 유효성 검사
- 기획전 타입별 input 값 유효성 검사

#### 기획전 수정
- 선분이력을 고려한 이전 이력 중단과 새로운 이력 생성
- 기획전 타입별 유효성 검사

#### 기획전 상세정보 GET
- 기획전 타입에 프로모션 상품포함되어야 하면 프로모션 상품도 같이 리턴

## Demo
Click below image to see our demo.


[![Brandi demo](https://media.vlpt.us/images/valentin123/post/3cd13470-baf9-4e1f-8ea0-8f8e143fe48b/%EC%8A%A4%ED%81%AC%EB%A6%B0%EC%83%B7,%202020-04-21%2016-37-34.png)](https://www.youtube.com/watch?v=BuQ6t9gCedA&feature=youtu.be)

## Features
+ [GET] Displaying existing seller list under the master authorization (Heechul Yoon).
+ [GET] Searching seller with keywords (Heechul Yoon).
+ [GET] Downloading seller list as excel file (Heechul Yoon).
+ [PUT] Changing seller status under the master authorization (Heechul Yoon).
+ [POST] Image resizing and uploading to S3 responsing back with URL (Heechul Yoon).
+ [POST] Registering promotional event under the master authorization (Heechul Yoon, Jongmin Lee).
+ [GET] Displaying existing event detail datas on editting page (Heechul Yoon, Jongmin Lee).
+ [PUT] Updating new information on existing event (Heechul Yoon, Jongmin Lee). 
+ [POST] Login authentication and ID/password validation (Yeji Choi).
+ [GET] Displaying detail information of a product (Soheon Lee).
+ [GET] Listing down product categories and subcategories according to the seller type (Soheon Lee).
+ [GET] Listing product color categories (Soheon Lee).
+ [POST] Registering new product by both master account and seller accounts (Soheon Lee).
+ [PUT] Updating product's detail information (Soheon Lee).
+ [GET] Listing existing product discount events and their related products with searching options (Soheon Lee).


## Technologies(Backend)
- Python 3.8.0
- Flask 1.1.2
- MySQL
- Git : rebase 커밋관리
- Pymysql : 데이터베이스 CRUD
- Pillow : 이미지 리사이즈
- Pandas : 엑셀파일 생성
- Boto3 : Python S3 업로더
- Bcrypt : 패스워드 암호화
- JWT : 토큰 발행
- AWS RDS
- AWS S3
- Flask-request-validator : 유효성 검사
- Blueprint : 라우팅 경로설정

## API Documentation(Backend)
+ [seller, product, event](https://documenter.getpostman.com/view/10892890/Szf6WTQ3?version=latest)

## Database Modeling
![Brandi ERD](https://brandi-intern.s3.ap-northeast-2.amazonaws.com/brandi_erd.png)

## Participations
##### Heechul Yoon <a href="https://github.com/valentin1235">github</a>
##### Jongmin Lee <a href="https://github.com/jomminii">github</a>
##### Seungjune Kim <a href="https://github.com/DanSJKim">github</a> 
##### Soheon Lee <a href="https://github.com/soheon-lee">github</a>
##### Yeji Choi <a href="https://github.com/yeji0120">github</a>
