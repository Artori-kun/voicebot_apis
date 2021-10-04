import numpy as np
from django_apis.core.voice_utils import extra_feature
from django_apis.core.voice_utils import compare_similarity, compare_feautures
from mysql.connector import MySQLConnection, Error
import time

import torch

def connect():
    """ Kết nối MySQL bằng module MySQLConnection """
    db_config = {
        'host': 'localhost',
        'database': 'rasa_voicebot',
        'user': 'root',
        'password': '123456'
    }

    # Biến lưu trữ kết nối
    conn = None

    try:
        conn = MySQLConnection(**db_config)

        if conn.is_connected():
            return conn

    except Error as error:
        print(error)

    return conn


def save_feautures(feautures, user_name, file_name):
    torch.save(feautures, file_name)
    query = "INSERT INTO tutorials_user_feature(id, username, vector) " \
            "VALUES(%s,%s,%s)"
    all_saved_users = load_all_saved_user()
    max_id = 0
    for user in all_saved_users:
        if user[0] > max_id:
            max_id = user[0]
    id = max_id + 1
    args = (id, user_name, file_name)
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    except Error as error:
        print(error)
        return None
    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()
    return args


def load_features(user_name):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tutorials_user_feature where username = " + "\"" + user_name + "\"")
        list_feautures = []
        row = cursor.fetchone()
        while row is not None:
            list_feautures.append(torch.load(row[1]))
            row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()
    return list_feautures


def load_all_saved_user():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tutorials_user_feature")
        list_saved_user = []
        row = cursor.fetchone()
        while row is not None:
            list_saved_user.append(row)
            row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()
    return list_saved_user

# print(feature)
# save_feautures(feature, 'userman', 'saved_feautures/f4.pt')
# load_f = load_features('user3')
# print(load_f)
# print(load_all_saved_user())


def check_user(file_data):
    all_saved_users = load_all_saved_user()
    to_check_feautures = extra_feature(file_data)
    best_match_user_name = None
    max_similarity = 0
    for user in all_saved_users:
        user_name = user[1]
        user_feauture = torch.load(user[2])
        similar = compare_feautures(to_check_feautures, user_feauture)
        if similar > max_similarity:
            max_similarity = similar
            if max_similarity >= 0.3:
                best_match_user_name = user_name
            else:
                best_match_user_name = None

    return best_match_user_name, max_similarity

# xoas DL
def delete_user(user_name):
    query = "DELETE FROM tutorials_user_feature WHERE username = %s"

    try:
        conn = connect()

        # Thực thi câu truy vấn
        cursor = conn.cursor()
        cursor.execute(query, (user_name,))

        # Chấp nhận sự thay đổi
        conn.commit()

    except Error as error:
        print(error)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # delete_user('user4')
    # print(record_log_in())
    # print(record_signup( 'user14', 'saved_feautures/f.pt'))
    # feature = extra_feature('data/00001.wav')
    # print(feature)
    feature = extra_feature('data/00001.wav')
    save_feautures(feature, 'user1', 'saved_feautures/f1.pt')
    # print(save_feautures(feature1, 'user1', 'saved_feautures/f2.pt'))
    print(load_all_saved_user())
    # match_user, similarity = check_user('data/00001.wav')
    # print(match_user, similarity)


