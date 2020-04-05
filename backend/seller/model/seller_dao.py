from flask import jsonify
from mysql.connector.errors import Error

from connection import DatabaseConnection


class SellerDao:

    """ 셀러 모델

    Authors:
        leesh3@brandi.co.kr (이소헌)
    History:
        2020-03-25 (leesh3@brandi.co.kr): 초기 생성
    """

    def insert_seller(self, new_seller, db_connection):

        """ 신규 셀러 계정 INSERT INTO DB

        입력된 인자가 새로운 셀러로 가입됩니다.
        가입된 셀러의 매니저 인포도 동시에 저장됩니다.
        셀러 인포와 매니저 인포가 모두 정상 저장되어야만 계정 저장이 완료됩니다.

        Args:
            new_seller(dictionary): 신규 가입 셀러
            db_connection: 데이터베이스 커넥션 객체

        Returns: http 응답코드
            200: 신규 셀러 계정 저장 완료
            400: key error
            500: server error

        Authors:
            leesh3@brandi.co.kr (이소헌)

        History:
            2020-03-25 (leesh3@brandi.co.kr): 초기 생성
        """
        try:
            with db_connection.cursor()  as db_cursor:

                new_seller_info_data = {
                    'name_kr': new_seller['name_kr'],
                    'name_en': new_seller['name_en'],
                    'site_url': new_seller['site_url'],
                    'center_number': new_seller['center_number']
                }

                new_manager_info_data = {
                    'contact_number': new_seller['contact_number'],
                    'is_deleted': new_seller['is_deleted']
                }

                # 트랜잭션 시작
                db_cursor.execute("START TRANSACTION")
                # 자동 커밋 비활성화
                db_cursor.execute("SET AUTOCOMMIT=0")

                # seller_infos 테이블 INSERT INTO
                insert_seller_info_statement = """
                    INSERT INTO seller_infos (
                    name_kr,
                    name_en,
                    site_url,
                    center_number
                ) VALUES (
                    %(name_kr)s,
                    %(name_en)s,
                    %(site_url)s,
                    %(center_number)s
                )"""

                db_cursor.execute(insert_seller_info_statement, new_seller_info_data)

                new_manager_info_data['seller_id'] = db_cursor.lastrowid

                # manager_infos 테이블 INSERT INTO
                insert_manager_info_statement = ("""
                    INSERT INTO manager_infos (
                    contact_number,
                    is_deleted,
                    seller_id
                ) VALUES (
                    %(contact_number)s,
                    %(is_deleted)s,
                    %(seller_id)s
                )""")

                db_cursor.execute(insert_manager_info_statement, new_manager_info_data)

                db_connection.commit()
                return jsonify({'message': 'SUCCESS'}), 200

        except KeyError as e:
            print(f'KEY_ERROR_WITH {e}')
            db_connection.rollback()
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            db_connection.rollback()
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 400

    # noinspection PyMethodMayBeStatic
    def get_account_password(self, account_info, db_connection):

        """ 계정의 암호화된 비밀번호 표출

        비밀번호 변경 시 기존 비밀번호를 제대로 입력했는지 확인하기 위해,
        인자로 받아온 account_info['parameter_account_no'] 의 password 를 표출합니다.

        Args:
            account_info: account 정보
            (parameter_account_no: 비밀번호를 확인할 account_no)
            db_connection: 연결된 database connection 객체

        Returns:
            200: 요청된 계정의 계정번호 및 암호화된 비밀번호
            400: 존재하지 않는 계정 정보
            500: SERVER ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-03-31 (leejm3@brandi.co.kr): 초기 생성
        """

        try:
            with db_connection.cursor()  as db_cursor:

                # SELECT 문에서 확인할 데이터
                account_info_data = {
                    'account_no': account_info['parameter_account_no']
                }

                # accounts 테이블 SELECT
                select_account_password_statement = """
                    SELECT account_no, password 
                    FROM accounts 
                    WHERE account_no = %(account_no)s
                """

                # SELECT 문 실행
                db_cursor.execute(select_account_password_statement, account_info_data)

                # 쿼리로 나온 기존 비밀번호를 가져옴
                original_password = db_cursor.fetchone()
                return original_password

        except KeyError as e:
            print(f'KEY_ERROR WITH {e}')
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500

    # noinspection PyMethodMayBeStatic
    def change_password(self, account_info, db_connection):

        """ UPDATE 계정 비밀번호 DB

        Args:
            account_info: account 정보
            (parameter_account_no: 비밀번호를 확인할 account_no
            db_connection: 연결된 database connection 객체

        Returns: http 응답코드
            200: SUCCESS 비밀번호 변경 완료
            400: INVALID_KEY
            500: DB_CURSOR_ERROR, SERVER_ERROR

        Authors:
            leejm@brandi.co.kr (이종민)

        History:
            2020-03-31 (leejm3@brandi.co.kr): 초기 생성
        """

        try:
            with db_connection.cursor()  as db_cursor:

                # SELECT 문에서 확인할 데이터
                account_info_data = {
                    'account_no': account_info['parameter_account_no'],
                    'password': account_info['new_password'],
                }

                # accounts 테이블 UPDATE
                update_password_statement = """
                    UPDATE 
                    accounts 
                    SET
                    password = %(password)s
                    WHERE
                    account_no = %(account_no)s
                """

                # UPDATE 문 실행
                db_cursor.execute(update_password_statement, account_info_data)

                # 실행 결과 반영
                db_connection.commit()
                return jsonify({'message': 'SUCCESS'}), 200

        except KeyError:
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500

    # noinspection PyMethodMayBeStatic
    def get_seller_info(self, account_info, db_connection):

        """ 계정의 셀러정보 표출

        인자로 받아온 account_info['parameter_account_no'] 의 셀러정보를 표출합니다.

        Args:
            account_info: account 정보
            (parameter_account_no: 셀러정보를 확인할 account_no)
            db_connection: 연결된 database connection 객체

        Returns:
            200: 요청된 계정의 셀러정보
            400: 존재하지 않는 계정 정보
            500: DB_CURSOR_ERROR, SERVER_ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-03-31 (leejm3@brandi.co.kr): 초기 생성
            2020-04-01 (leejm3@brandi.co.kr): seller_info 기본 정보 표출
            2020-04-02 (leejm3@brandi.co.kr): 외래키 관련 정보 표출
            2020-04-03 (leejm3@brandi.co.kr): 표출 정보에 외래키 id 값 추가
        """
        try:
            with db_connection.cursor()  as db_cursor:

                # 셀러 기본 정보(외래키 제외)
                # SELECT 문 조건 데이터
                account_info_data = {
                    'account_no': account_info['parameter_account_no']
                }

                # seller_info 테이블 SELECT (get 기본 정보)
                select_seller_info_statement = """
                    SELECT 
                    seller_info_no,
                    seller_account_id,
                    profile_image_url,
                    c.status_no as seller_status_no,
                    c.name as seller_status_name,
                    d.seller_type_no as seller_type_no,
                    d.name as seller_type_name,
                    e.account_no as account_no,
                    e.login_id as account_login_id,
                    f.app_user_no as brandi_app_user_no,
                    f.app_id as brandi_app_user_app_id,
                    name_kr,
                    name_en,
                    brandi_app_user_id,
                    ceo_name,
                    company_name,
                    business_number,
                    certificate_image_url,
                    online_business_number,
                    online_business_image_url,
                    background_image_url,
                    short_description,
                    long_description,
                    site_url,
                    insta_id,
                    center_number,
                    kakao_id,
                    yellow_id,
                    zip_code,
                    address,
                    detail_address,
                    weekday_start_time,
                    weekday_end_time,
                    weekend_start_time,
                    weekend_end_time,
                    bank_name,
                    bank_holder_name,
                    account_number
                    
                    FROM seller_accounts AS a
                    
                    -- seller_info 기본 정보
                    INNER JOIN seller_infos AS b
                    ON a.seller_account_no = b.seller_account_id
                    
                    -- 셀러 상태명
                    INNER JOIN seller_statuses as c
                    ON b.seller_status_id = c.status_no

                    -- 셀러 속성명
                    INNER JOIN seller_types as d
                    ON b.seller_type_id = d.seller_type_no

                    -- 셀러계정 로그인 아이디
                    LEFT JOIN accounts as e
                    ON e.account_no = a.account_id
                    AND e.is_deleted =0

                    -- 브랜디 앱 아이디
                    LEFT JOIN brandi_app_users as f
                    ON b.brandi_app_user_id = f.app_user_no
                    AND f.is_deleted = 0
                    WHERE a.account_id = %(account_no)s
                    AND a.is_deleted = 0
                    AND b.close_time = '2037-12-31 23:59:59'
                """

                # SELECT 문 실행
                db_cursor.execute(select_seller_info_statement, account_info_data)

                # seller_info_result 에 쿼리 결과 저장
                seller_info_result = db_cursor.fetchone()

                # 담당자 정보
                # SELECT 문 조건 데이터
                seller_info_no_data = {
                    'seller_info_no': seller_info_result['seller_info_no']
                }
                # manager_infos 테이블 SELECT(get *)
                select_manager_infos_statement = """
                                SELECT
                                b.name,
                                b.contact_number,
                                b.email,
                                b.ranking
                                FROM seller_infos AS a
                                INNER JOIN manager_infos AS b
                                ON a.seller_info_no = b.seller_info_id
                                WHERE seller_info_no = %(seller_info_no)s
                                AND b.is_deleted = 0
                                LIMIT 3
                            """

                # SELECT 문 실행
                db_cursor.execute(select_manager_infos_statement, seller_info_no_data)

                # manager_infos 출력 결과 저장
                manager_infos = db_cursor.fetchall()

                # seller_info_result 에 manager_info 저장
                seller_info_result['manager_infos'] = [info for info in manager_infos]

                # 셀러 상태 변경 기록
                # SELECT 문 조건 데이터
                account_info_data = {
                    'seller_account_id': seller_info_result['seller_account_id']
                }

                # seller_status_change_histories 테이블 SELECT
                select_status_history_statement = """
                                SELECT
                                changed_time,
                                c.name as seller_status_name,
                                d.login_id as modifier
                                FROM
                                seller_accounts as a

                                -- 셀러상태이력 기본정보
                                INNER JOIN
                                seller_status_change_histories as b
                                ON a.seller_account_no = b.seller_account_id

                                -- 셀러 상태명
                                INNER JOIN
                                seller_statuses as c
                                ON b.seller_status_id = c.status_no

                                -- 수정자 로그인아이디
                                LEFT JOIN
                                accounts as d
                                ON d.account_no = a.account_id

                                WHERE a.seller_account_no = %(seller_account_id)s
                                AND d.is_deleted = 0
                                ORDER BY changed_time
                            """

                # SELECT 문 실행
                db_cursor.execute(select_status_history_statement, account_info_data)

                # seller_status_change_histories 출력 결과 저장
                status_histories = db_cursor.fetchall()

                # seller_info_result 에 seller_status_change_histories 저장
                seller_info_result['seller_status_change_histories'] = [history for history in status_histories]

                # 셀러 속성 리스트(마스터가 셀러의 속성 변경하는 옵션 제공용)
                # SELECT 문 조건 데이터
                account_info_data = {
                    'seller_info_no': seller_info_result['seller_info_no']
                }

                # seller_types 테이블 SELECT
                select_seller_types_statement = """
                                SELECT
                                c.seller_type_no as seller_type_no,
                                c.name as seller_type_name
                                FROM 
                                product_sorts as a
                                
                                -- 셀러정보
                                INNER JOIN
                                seller_infos as b
                                ON a.product_sort_no = b.product_sort_id
                               
                                -- 상품속성
                                INNER JOIN
                                seller_types as c
                                ON a.product_sort_no = c.product_sort_id

                                WHERE b.seller_info_no = %(seller_info_no)s
                            """

                # SELECT 문 실행
                db_cursor.execute(select_seller_types_statement, account_info_data)

                # seller_types 출력 결과 저장
                seller_types = db_cursor.fetchall()

                # seller_info_result 에 seller_types 저장
                seller_info_result['seller_types'] = seller_types

                return seller_info_result

        except KeyError as e:
            print(f'KEY_ERROR WITH {e}')
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500

    # noinspection PyMethodMayBeStatic
    def get_seller_list(self, request, db_connection):
        """ GET 셀러 리스트를 표출하고, 검색 키워드가 오면 키워드 별 검색 가능.

        Args:
            db_connection: 연결된 database connection 객체
            request: 쿼리파라미터를 가져옴

        Returns: http 응답코드
            200: 셀러 리스트 표출(검색기능 포함)
            500: SERVER ERROR

        Authors:
            heechul@brandi.co.kr (윤희철)

        History:
            2020-04-03(heechul@brandi.co.kr): 초기 생성
        """
        # offset과 limit에 음수가 들어오면  default값 지정
        offset = 0 if int(request.args.get('offset', 0)) < 0 else int(request.args.get('offset', 0))
        limit = 10 if int(request.args.get('limit', 10)) < 0 else int(request.args.get('limit', 10))

        # sql에서 where 조건문에 들어갈 필터 문자열
        filter_query = ''

        # request에 쿼리파라미터가 들어오고 값이 존재하면 filter_query에 조건 쿼리문을 추가해줌.
        seller_account_no = request.args.get('seller_account_no', None)
        if seller_account_no:
            filter_query += f" AND seller_accounts.seller_account_no = {seller_account_no}"

        login_id = request.args.get('login_id', None)
        if login_id:
            filter_query += f" AND accounts.login_id = '{login_id}'"

        name_kr = request.args.get('name_kr', None)
        if name_kr:
            filter_query += f" AND name_kr = '{name_kr}'"

        name_en = request.args.get('name_en', None)
        if name_en:
            filter_query += f" AND name_en = '{name_en}'"

        brandi_app_user_id = request.args.get('brandi_app_user_id', None)
        if brandi_app_user_id:
            filter_query += f" AND brandi_app_user_id = {brandi_app_user_id}"

        manager_name = request.args.get('manager_name', None)
        if manager_name:
            filter_query += f" AND manager_infos.name = '{manager_name}'"

        seller_status = request.args.get('seller_status', None)
        if seller_status:
            filter_query += f" AND seller_statuses.name = '{seller_status}'"

        manager_contact_number = request.args.get('manager_contact_number', None)
        if manager_contact_number:
            filter_query += f" AND manager_infos.contact_number LIKE '%{manager_contact_number}%'"

        manager_email = request.args.get('manager_email', None)
        if manager_email:
            filter_query += f" AND manager_infos.email = '{manager_email}'"

        seller_type_name = request.args.get('seller_type_name', None)
        if seller_type_name:
            filter_query += f" AND seller_types.name = '{seller_type_name}'"

        start_date = request.args.get('start_time', None)
        end_date = request.args.get('close_time', None)
        if start_date and end_date:
            start_date = str(request.args.get('start_time', None)) + ' 00:00:00'
            end_date = str(request.args.get('close_time', None)) + ' 23:59:59'
            filter_query += f" AND seller_accounts.created_at > '{start_date}' AND seller_accounts.created_at < '{end_date}'"

        try:
            with db_connection.cursor()  as db_cursor:

                # 상품 개수를 가져오는 sql 명령문
                select_product_count_statement = '''
                    SELECT 
                    COUNT(products.product_no) as product_count
                    FROM seller_infos
                    right JOIN seller_accounts ON seller_accounts.seller_account_no = seller_infos.seller_account_id
                    LEFT JOIN product_infos ON seller_infos.seller_account_id = product_infos.seller_id
                    LEFT JOIN products ON product_infos.product_id = products.product_no 
                    GROUP BY seller_accounts.seller_account_no
                '''
                db_cursor.execute(select_product_count_statement)
                product_count = db_cursor.fetchall()

                # 셀러 리스트를 가져오는 sql 명령문, 쿼리가 들어오면 쿼리문을 포메팅해서 검색 실행
                select_seller_list_statement = f'''
                    SELECT 
                    seller_account_id, 
                    accounts.login_id,
                    name_en,
                    name_kr,
                    brandi_app_user_id,
                    seller_statuses.name as seller_status,
                    seller_status_id,
                    seller_types.name as seller_type_name,
                    site_url,
                    seller_accounts.created_at,
                    manager_infos.name as manager_name,
                    manager_infos.contact_number as manager_contact_number,
                    manager_infos.email as manager_email
                    FROM seller_infos
                    right JOIN seller_accounts ON seller_accounts.seller_account_no = seller_infos.seller_account_id
                    LEFT JOIN accounts ON seller_accounts.account_id = accounts.account_no
                    LEFT JOIN seller_statuses ON seller_infos.seller_status_id = seller_statuses.status_no
                    LEFT JOIN seller_types ON seller_infos.seller_type_id = seller_types.seller_type_no
                    LEFT JOIN manager_infos on manager_infos.seller_info_id = seller_infos.seller_info_no 
                    WHERE seller_infos.close_time = '2037-12-31 23:59:59.0' 
                    AND manager_infos.ranking = 1{filter_query}
                    LIMIT %(limit)s OFFSET %(offset)s                   
                '''
                parameter = {
                    'limit' : limit,
                    'offset' : offset
                }

                # sql 쿼리와 pagination 데이터 바인딩
                db_cursor.execute(select_seller_list_statement, parameter)
                seller_info = db_cursor.fetchall()

                # 데이터 베이스에서 가져온 셀러, 매니저, 상품 개수 정보 리스트화
                seller_list = [{**seller_info[i], **product_count[i]} for i in range(0, len(seller_info))]
                print(seller_list)
                for seller in seller_list:
                    if seller['seller_status'] == '입점':
                        seller['action'] = ['휴점 신청', '퇴점 신청 처리']
                    elif seller['seller_status'] == '입점대기':
                        seller['action'] = ['입점 승인', '입점 거절']
                    elif seller['seller_status'] == '휴점':
                        seller['action'] = ['휴점 해제', '퇴점 신청 처리']
                    elif seller['seller_status'] == '퇴점대기':
                        seller['action'] = ['휴점 신청', '퇴점 확정 처리', '퇴점 철회 처리']
                print(seller_list)

                return jsonify({'data': seller_list}), 200

        # 데이터베이스 error
        except Exception as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'error': 'DB_CURSOR_ERROR'}), 500

    # noinspection PyMethodMayBeStatic
    def change_seller_info(self, account_info, db_connection):

        """ 계정 셀러정보를 수정(새로운 이력 생성) INSERT INTO DB

        계정 셀러정보를 수정합니다.
        선분이력 관리를 위해 기존 셀러정보 updated_at(수정일시)와 close_time(종료일시)를 업데이트하고,
        새로운 셀러정보 이력을 생성합니다.
        입력한 브랜디 앱 아이디가 존재하는지 확인하는 절차를 가집니다.

        기존 셀러정보와 새로운 셀러정보, 담당자 정보, 셀러 상태 변경 기록이 모두 정상 저장되어야 프로세스가 완료됩니다.
        기존 셀러정보의 종료일시를 새로운 셀러정보의 시작일시와 맞추기 위해 새로운 셀러정보를 먼저 등록했습니다.

        Args:
            account_info: 엔드포인트에서 전달 받은 account 정보
            db_connection: 연결된 database connection 객체

        Returns: http 응답코드
            200: 셀러정보 수정(새로운 이력 생성) 완료
            400: INVALID_APP_ID (존재하지 않는 브랜디 앱 아이디 입력)
            500: SERVER_ERROR, DB_CURSOR_ERROR

        Authors:
            leejm3@brandi.co.kr (이종민)

        History:
            2020-04-03 (leejm3@brandi.co.kr): 초기 생성
            2020-04-04 (leejm3@brandi.co.kr): 기본정보, 담당자정보 수정 저장 확인
            2020-04-05 (leejm3@brandi.co.kr): 에러 처리 추가 확인

        """
        try:
            with db_connection.cursor()  as db_cursor:

                # 트랜잭션 시작
                db_cursor.execute("START TRANSACTION")
                # 자동 커밋 비활성화
                db_cursor.execute("SET AUTOCOMMIT=0")

                # 브랜디앱유저 검색 정보
                brandi_app_user_data = {
                    'app_id': account_info['brandi_app_user_app_id']
                }

                # brandi_app_users 테이블 SELECT
                select_app_id_statement = """
                    SELECT
                    app_user_no
                    FROM
                    brandi_app_users
                    WHERE app_id = %(app_id)s
                    AND is_deleted = 0
                """

                db_cursor.execute(select_app_id_statement, brandi_app_user_data)

                # app_id 출력 결과 저장
                app_id_result = db_cursor.fetchone()

                # app_id가 있으면보 account_info 에 app_user_no 저장
                if app_id_result:
                    account_info['app_user_no'] = app_id_result['app_user_no']

                # app_id가 없으면 app_id가 존재하지 않는다고 리턴
                else:
                    return jsonify({'message': 'INVALID_APP_ID'}), 400

                # list 인 manager_infos 가 SQL 에 들어가면 에러를 반환해 미리 manager_infos 에 저장하고 account_info 에서 삭제
                manager_infos = account_info['manager_infos']
                del account_info['manager_infos']

                # 셀러 기본 정보 생성
                # seller_infos 테이블 INSERT INTO
                insert_seller_info_statement = """
                    INSERT INTO seller_infos (
                    seller_account_id,
                    profile_image_url,
                    seller_status_id,
                    seller_type_id,
                    product_sort_id,                 
                    name_kr,
                    name_en,
                    brandi_app_user_id,
                    ceo_name,
                    company_name,
                    business_number,
                    certificate_image_url,
                    online_business_number,
                    online_business_image_url,
                    background_image_url,
                    short_description,
                    long_description,
                    site_url,
                    kakao_id,
                    insta_id,
                    yellow_id,
                    center_number,
                    zip_code,
                    address,
                    detail_address,
                    weekday_start_time,
                    weekday_end_time,
                    weekend_start_time,
                    weekend_end_time,
                    bank_name,
                    bank_holder_name,
                    account_number,
                    modifier
                ) VALUES (
                    %(seller_account_id)s,
                    %(profile_image_url)s,
                    %(seller_status_no)s,
                    %(seller_type_no)s,
                    (SELECT product_sort_id FROM seller_types WHERE seller_type_no = %(seller_type_no)s),                     
                    %(name_kr)s,
                    %(name_en)s,
                    %(app_user_no)s,                    
                    %(ceo_name)s,
                    %(company_name)s,
                    %(business_number)s,
                    %(certificate_image_url)s,
                    %(online_business_number)s,
                    %(online_business_image_url)s,
                    %(background_image_url)s,
                    %(short_description)s,
                    %(long_description)s,
                    %(site_url)s,
                    %(kakao_id)s,
                    %(insta_id)s,
                    %(yellow_id)s,                    
                    %(center_number)s,
                    %(zip_code)s,
                    %(address)s,
                    %(detail_address)s,
                    %(weekday_start_time)s,
                    %(weekday_end_time)s,
                    %(weekend_start_time)s,
                    %(weekend_end_time)s,
                    %(bank_name)s,
                    %(bank_holder_name)s,
                    %(account_number)s,
                    %(decorator_account_no)s
                )"""

                # 셀러 기본정보 insert 함
                db_cursor.execute(insert_seller_info_statement, account_info)

                # 위에서 생성된 새로운 셀러정보의 id 값을 가져옴
                seller_info_no = db_cursor.lastrowid

                # manager_infos 테이블 INSERT INTO
                insert_manager_info_statement = """
                    INSERT INTO manager_infos (
                    name,
                    contact_number,
                    email,
                    ranking,
                    seller_info_id
                ) VALUES (
                    %(name)s,
                    %(contact_number)s,
                    %(email)s,
                    %(ranking)s,
                    %(seller_info_id)s
                )"""

                # for 문을 돌면서 담당자 정보를 insert 함
                for i in range(len(manager_infos)):
                    manager_info_data = {
                        'name': manager_infos[i]['name'],
                        'contact_number': manager_infos[i]['contact_number'],
                        'email': manager_infos[i]['email'],
                        'ranking': manager_infos[i]['ranking'],
                        'seller_info_id': seller_info_no
                    }

                    db_cursor.execute(insert_manager_info_statement, manager_info_data)

                # 이전 셀러정보 수정일시, 종료일시 업데이트
                previous_seller_info_data = {
                    'previous_seller_info_no': account_info['previous_seller_info_no'],
                    'new_seller_info_no': seller_info_no
                }

                # previous_seller_info 테이블 UPDATE
                update_previous_seller_info_statement = """
                    UPDATE seller_infos
                    SET
                    updated_at = 
                    (SELECT a.start_time FROM 
                    (SELECT start_time FROM seller_infos WHERE seller_info_no = %(new_seller_info_no)s) as a),
                    close_time = 
                    (SELECT b.start_time FROM 
                    (SELECT start_time FROM seller_infos WHERE seller_info_no = %(new_seller_info_no)s) as b)
                    WHERE seller_info_no = %(previous_seller_info_no)s
                """

                db_cursor.execute(update_previous_seller_info_statement, previous_seller_info_data)

                # 이전 셀러정보의 셀러 상태값과 새로운 셀러정보의 셀러 상태값이 다르면, 셀러 상태정보이력 테이블 INSERT INTO
                if account_info['previous_seller_status_no'] != account_info['seller_status_no']:

                    # INSERT INTO 문에서 확인할 데이터
                    seller_status_data = {
                        'seller_account_id': account_info['seller_account_id'],
                        'new_seller_info_no': seller_info_no,
                        'seller_status_id': account_info['seller_status_no'],
                        'modifier': account_info['decorator_account_no']
                    }

                    # seller_status_change_histories 테이블 INSERT INTO
                    insert_status_history_statement = """
                        INSERT INTO seller_status_change_histories (
                        seller_account_id,
                        changed_time,
                        seller_status_id,
                        modifier
                    ) VALUES (
                        %(seller_account_id)s,
                        (SELECT start_time FROM seller_infos WHERE seller_info_no = %(new_seller_info_no)s),
                        %(seller_status_id)s,
                        %(modifier)s
                    )"""

                    db_cursor.execute(insert_status_history_statement, seller_status_data)

                db_connection.commit()
                return jsonify({'message': 'SUCCESS'}), 200

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            db_connection.rollback()
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500

    def get_seller_name_list(self, keyword, db_connection):

        """

        Args:
            keyword(string):
            db_connection(DatabaseConnection):

        Returns:
            200: 검색된 셀러 10개
            400: key error
            500: server error

        Authors:

            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-05 (leesh3@brandi.co.kr): 초기 생성
        """
        try:
            with db_connection.cursor()  as db_cursor:
                get_stmt = """
                    SELECT seller_info_no, profile_image_url, name_kr
                    FROM seller_infos 
                    WHERE name_kr 
                    LIKE '%"""+keyword+"""%'
                """
                db_cursor.execute(get_stmt)

                names = db_cursor.fetchmany(10)

                if names:
                    return jsonify({'search_results': names}), 200
                return jsonify({'message': 'SELLER_DOES_NOT_EXISTS'}), 404

        except KeyError as e:
            print(f'KEY_ERROR_WITH {e}')
            db_connection.rollback()
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            db_connection.rollback()
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500

    def change_seller_status(self, seller_status_id, seller_account_id, db_connection):

        """ 마스터 권한 셀러 상태 변경
            Args:
                seller_status_id: 셀러 상태 아이디
                seller_account_id: 셀러 정보 아이디
                db_connection: 데이터베이스 커넥션 객체

            Returns:
                200: 셀러 상태 정보 수정 성공
                500: 데이터베이스 error

            Authors:
                yoonhc@brandi.co.kr (윤희철)

            History:
                2020-04-05 (yoonhc@brandi.co.kr): 초기 생성

        """

        # 데이터베이스 커서 실행
        try:
            with db_connection.cursor()  as db_cursor:

                # 셀러 상태 변경 sql 명령문
                update_seller_status_statement = """
                    UPDATE
                    seller_infos
                    SET
                    seller_status_id = %(seller_status_id)s
                    WHERE
                    seller_account_id = %(seller_account_id)s
                """

                # service에서 넘어온 셀러 데이터
                seller_status_data = {
                    'seller_status_id' : seller_status_id,
                    'seller_account_id' : seller_account_id
                }

                # 데이터 sql명령문과 셀러 데이터 바인딩
                db_cursor.execute(update_seller_status_statement, seller_status_data)
                db_connection.commit()
                return jsonify({'message' : 'SUCCESS'}), 200

        # 데이터베이스 error
        except Exception as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'error': 'DB_CURSOR_ERROR'}), 500

    def get_account_info(self, account_info, db_connection):

        """ 로그인 정보 확인

        account_info 를 통해서 DB 에 있는 특정 계정 정보의 account_no 와 암호화 되어있는 password 를 가져와서 return

        Args:
            account_info: 유효성 검사를 통과한 account 정보 (login_id, password)
            db_connection: 연결된 database connection 객체

        Returns:
            200: db_account_info db 에서 get 한 account_no 와 password
            400: INVALID_KEY
            500: DB_CURSOR_ERROR

        Authors:
            choiyj@brandi.co.kr (최예지)

        History:
            2020-04-05 (choiyj@brandi.co.kr): 초기 생성
            2020-04-05 (choiyj@brandi.co.kr): SQL 문을 통해 DB 에서 원하는 정보를 가지고 와서 return 하는 함수 구현
        """

        try:
            # db_cursor 는 db_connection 에 접근하는 본체 (가져온 정보는 cursor 가 가지고 있다)
            with db_connection as db_cursor:

                # sql 문 작성 (원하는 정보를 가져오거나 집어넣거나)
                select_account_info_statement = """
                    SELECT
                    account_no,
                    password
                    
                    FROM accounts
                    
                    where login_id = %(login_id)s AND is_deleted = 0
                """

                # SELECT 문 실행
                db_cursor.execute(select_account_info_statement, account_info)

                # DB 에 저장하는 로직 작성 (fetchone, fetchall, fetchmany)
                account_info_result = db_cursor.fetchone()

                # DB 에서 꺼내온 정보를 return
                return account_info_result

        except KeyError as e:
            print(f'KEY_ERROR WITH {e}')
            return jsonify({'message': 'INVALID_KEY'}), 400

        except Error as e:
            print(f'DATABASE_CURSOR_ERROR_WITH {e}')
            return jsonify({'message': 'DB_CURSOR_ERROR'}), 500
