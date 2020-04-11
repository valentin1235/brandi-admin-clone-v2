import re

from flask import request, Blueprint, jsonify, g
from flask_request_validator import (
    GET,
    FORM,
    PATH,
    JSON,
    Param,
    Pattern,
    validate_params
)
from product.service.product_service import ProductService
from connection import get_db_connection
from utils import login_required, ImageUpload


class ProductView():
    """
    프로덕트 뷰
    """
    product_app = Blueprint('product_app', __name__, url_prefix='/product')

    @product_app.route("/category", methods=["GET"])
    @login_required
    def get_first_categories():

        """ 상품 분류별 1차 카테고리 표 엔드포인트

        Returns:
            200: 셀러가 속한 상품 분류에 따른 1차 카테고리
            400: 데이터베이스 연결 에러
            500: server error

        Authors:
            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-02 (leesh3@brandi.co.kr): 초기 생성

        """
        db_connection = get_db_connection()
        if db_connection:
            try:
                product_service = ProductService()
                categories = product_service.get_first_categories(db_connection)

                return categories

            except Exception as e:
                return jsonify({'message': f'{e}'}), 400

            finally:
                try:
                    db_connection.close()

                except Exception as e:
                    return jsonify({'message': f'{e}'}), 400
        else:
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 400

    @product_app.route(
        "/category/<int:first_category_no>",
        methods=["GET"], endpoint='get_second_categories')
    @login_required
    @validate_params(
        Param('first_category_no', PATH, int),
    )
    def get_second_categories(first_category_no):

        """ 상품 2차 카테고리 목록 표출

        선택된 상품 1차 카테고릭에 따라 해당하는 2차카테고리 목록 표출

        Args:
            first_category_no(integer): 1차 카테고리 인덱스 번호

        Returns:
            200: 1차 카테고리에 해당하는 2차 카테고리 목록
            400: 데이터베이스 연결 에러
            500: server error

        Authors:

            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-02 (leesh3@brandi.co.kr): 초기 생성
            2020-04-07 (leesh3@brandi.co.kr): URL 구조 변경
        """

        db_connection = get_db_connection()

        if db_connection:
            try:
                product_service = ProductService()
                categories = product_service.get_second_categories(db_connection, first_category_no)
                return categories

            except Exception as e:
                return jsonify({'message': f'{e}'}), 400

            finally:
                try:
                    db_connection.close()

                except Exception as e:
                    return jsonify({'message': f'{e}'}), 400
        else:
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 400

    @product_app.route("/<int:product_no>", methods=["GET"], endpoint='get_product_detail')
    @login_required
    @validate_params(Param('product_no', PATH, int))
    def get_product_detail1(product_no):

        """ 상품 등록/수정시 나타나는 개별 상품의 기존 정보 표출 엔드포인트

        상품의 번호를 path parameter 로 받아 해당하는 상품의 기존 상세 정보를 표출.

        Args:
            product_no(integer): 상품 id

        Returns:
            200: 상품별 상세 정보
            500: 데이터베이스 에러

        Authors:
            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-03 (leesh3@brandi.co.kr): 초기 생성
            2020-04-07 (leesh3@brandi.co.kr): 파라미터 변수를 product_info_no -> product_no로 변경
        """
        db_connection = get_db_connection()
        if db_connection:
            try:
                product_service = ProductService()
                product_infos = product_service.get_product_detail(product_no, db_connection)

                return product_infos

            except Exception as e:
                return jsonify({'message': f'{e}'}), 500

            finally:
                try:
                    db_connection.close()
                except Exception as e:
                    return jsonify({'message': f'{e}'}), 500
        else:
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

    @product_app.route('', methods=['POST'], endpoint='insert_new_product')
    @login_required
    @validate_params(
        Param('is_available', FORM, int),
        Param('is_on_display', FORM, int),
        Param('first_category_id', FORM, int),
        Param('second_category_id', FORM, int, required=False),
        Param('name', FORM, str,
              rules=[Pattern(r"^((?!(?=.*\")(?=.*\')).)*$")]),
        Param('short_description', FORM, str, required=False),
        Param('color_filter_id', FORM, int),
        Param('style_filter_id', FORM, int),
        Param('long_description', FORM, str),
        Param('youtube_url', FORM, str, required=False),
        Param('stock', FORM, int),
        Param('price', FORM, int),
        Param('discount_rate', FORM, float),
        Param('discount_start_time', FORM, str, required=False),
        Param('discount_end_time', FORM, str, required=False),
        Param('min_unit', FORM, int),
        Param('max_unit', FORM, int),
        Param('tags', FORM, str, required=False),
        Param('selected_account_no', FORM, int)
    )
    def insert_new_product(*args):
        print(args)
        """ 상품 등록 엔드포인트

        새로운 상품을 등록하는 엔드포인트.
        등록하려는 셀러의 정보에 따라 내부 내용이 달라지므로, 데코레이터에서 셀러 정보를 먼저 읽어옴.
        등록 상세 정보는 request.body 내부에 존재함.
        유효성 검사를 위한 조건 통과 후 product_info 변수에 내용을 담아 product_service로 전달.

        Args:
            *args: 등록할 제품의 상세 정보

        g.account_info: 데코레이터에서 넘겨받은 수정을 수행하는 계정 정보
            auth_type_id: 계정의 권한정보
            account_no: 데코레이터에서 확인된 계정번호

        Returns: Http 응답코드
            200: 신규 상품 등록 성공
            500: 데이터베이스 에

        Authors:
            leesh3@brandi.co.kr (이소헌)
            
        History:
            2020-04-06 (leesh3@brandi.co.kr): 초기 생성

        """

        image_uploader = ImageUpload()
        uploaded_images = image_uploader.upload_product_image(request)

        product_info = {
            'auth_type_id': g.account_info['auth_type_id'],
            'account_no': g.account_info['account_no'],
            'uploader': g.account_info['account_no'],
            'modifier': g.account_info['account_no'],
            'is_available': args[0],
            'is_on_display': args[1],
            'first_category_id': args[2],
            'second_category_id': args[3],
            'name': args[4],
            'short_description': args[5],
            'color_filter_id': args[6],
            'style_filter_id': args[7],
            'long_description': args[8],
            'youtube_url': args[9],
            'stock': args[10],
            'price': args[11],
            'discount_rate': args[12]/100,
            'discount_start_time': args[13],
            'discount_end_time': args[14],
            'min_unit': args[15],
            'max_unit': args[16],
            'tags': args[17],
            'selected_account_no': args[18],
            'images': uploaded_images,
        }
        db_connection = get_db_connection()

        if db_connection:
            try:
                product_service = ProductService()
                product_insert_result = product_service.insert_new_product(product_info, db_connection)

                return product_insert_result

            except Exception as e:
                return jsonify({'message': f'{e}'}), 500

            finally:
                try:
                    db_connection.close()
                except Exception as e:
                    return jsonify({'message': f'{e}'}), 500

        return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500

    @product_app.route("/<int:product_id>", methods=['PUT'], endpoint='update_product_info')
    @login_required
    @validate_params(
        Param('is_available', JSON, int),
        Param('is_on_display', JSON, int),
        Param('product_sort_id', JSON, int),
        Param('first_category_id', JSON, int),
        Param('second_category_id', JSON, int),
        Param('name', JSON, str,
              rules=[Pattern(r"^((?!(?=.*\")(?=.*\')).)*$")]),
        Param('short_description', JSON, str, required=False),
        Param('color_filter_id', JSON, int),
        Param('style_filter_id', JSON, int),
        Param('long_description', JSON, str),
        Param('youtube_url', JSON, str, required=False),
        Param('stock', JSON, int),
        Param('price', JSON, int),
        Param('discount_rate', JSON, float),
        Param('discount_start_time', JSON, str, required=False),
        Param('discount_end_time', JSON, str, required=False),
        Param('min_unit', JSON, int),
        Param('max_unit', JSON, int),
        Param('tags', JSON, list, required=False),
        Param('product_id', PATH, int),
        Param('seller_account_no', JSON, int),
    )
    def update_product_info(*args):

        """ 상품 정보 수정 엔드포인트

        상품의 정보를 수정하는 엔드포인트.
        등록하려는 셀러의 정보에 따라 내부 내용이 달라지므로, 데코레이터에서 셀러 정보를 먼저 읽어옴.
        수정 상세 정보는 request.body 내부에 존재함.
        유효성 검사를 위한 조건 통과 후 product_info 변수에 내용을 담아 product_service로 전달.

        Args:
            *args: 등록할 제품의 상세 정보

        g.account_info: 데코레이터에서 넘겨받은 수정을 수행하는 계정 정보
            auth_type_id: 계정의 권한정보
            account_no: 데코레이터에서 확인된 계정번호

        Returns: Http 응답코드
            200: 상품 정보 수정 성공
            500: 데이터베이스 에러

        Authors:
            leesh3@brandi.co.kr (이소헌)

        History:
            2020-04-08 (leesh3@brandi.co.kr): 초기 생성
        """

        image_uploader = ImageUpload()
        uploaded_images = image_uploader.upload_product_image(request)

        # 이미지 업로더를 호출한 결과값에 애러코드 400이 포함되어있으면 utils.py에서 발생한 러메세지를 그대로 리턴
        if (400 or 500) in uploaded_images:
            return uploaded_images

        product_info = {
            'auth_type_id': g.account_info['auth_type_id'],
            'token_account_no': g.account_info['account_no'],
            'modifier': g.account_info['account_no'],
            'is_available': args[0],
            'is_on_display': args[1],
            'product_sort_id': args[2],
            'first_category_id': args[3],
            'second_category_id': args[4],
            'name': args[5],
            'short_description': args[6],
            'color_filter_id': args[7],
            'style_filter_id': args[8],
            'long_description': args[9],
            'youtube_url': args[10],
            'stock': args[11],
            'price': args[12],
            'discount_rate': args[13],
            'discount_start_time': args[14],
            'discount_end_time': args[15],
            'min_unit': args[16],
            'max_unit': args[17],
            'tags': args[18],
            'product_id': args[19],
            'seller_account_id': args[20],
            'images': uploaded_images,
        }

        db_connection = get_db_connection()
        if db_connection:
            try:
                product_service = ProductService()
                product_update_result = product_service.update_product_info(product_info, db_connection)

                return product_update_result

            except Exception as e:
                return jsonify({'message': f'{e}'}), 500

            finally:
                try:
                    db_connection.close()
                except Exception as e:
                    return jsonify({'message': f'{e}'}), 500
        else:
            return jsonify({'message': 'NO_DATABASE_CONNECTION'}), 500
