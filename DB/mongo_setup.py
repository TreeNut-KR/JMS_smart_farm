from pymongo import MongoClient
import datetime

class DatabaseManager:
    def __init__(self, db_name='JMSPlant'):
        self.client = MongoClient('localhost', 27017)  # MongoDB 서버에 연결
        self.db = self.client[db_name]

    def __call__(self):
        self.create_collections()
        self.insert_sample_data()  # 샘플 데이터 추가 메소드 호출

    def create_collections(self):
        # smartFarm 컬렉션 생성
        smart_farm_collection = self.db['smartFarm']
        smart_farm_collection.create_index([('idx', 1)], unique=True)
        
        # user_info 컬렉션 생성
        user_info_collection = self.db['user_info']
        user_info_collection.create_index([('id', 1)], unique=True)

    def insert_sample_data(self):
        # smartFarm 컬렉션에 샘플 데이터 추가
        smart_farm_data = {
            "IsRun": False,
            "sysfan": True,
            "wpump": True,
            "led": True,
            "humidity": 50.5,
            "temperature": 22.5,
            "ground1": 500,
            "ground2": 500,
            "created_at": datetime.datetime.now(),
            "updated_at": datetime.datetime.now(),
            "deleted_at": None
        }
        self.db.smartFarm.insert_one(smart_farm_data)

DB_setup = DatabaseManager()
DB_setup()
