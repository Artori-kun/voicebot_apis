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


def save_feautures(feautures, user_name, firstname, lastname, email):
    file_name = "saved_feautures/" + user_name + ".pt"
    torch.save(feautures, file_name)
    query = "INSERT INTO CustomUser(id, username, firstname, lastname, email, vector) " \
            "VALUES(%s,%s,%s,%s,%s, %s)"
    all_saved_users = load_all_saved_user()
    max_id = 0
    for user in all_saved_users:
        if user[0] > max_id:
            max_id = user[0]
    id = max_id + 1
    args = (id, user_name, firstname, lastname, email, file_name)
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
        cursor.execute("SELECT * FROM CustomUser where username = " + "\"" + user_name + "\"")
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
        cursor.execute("SELECT * FROM CustomUser")
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
        user_feauture = torch.load(user[11])
        similar = compare_feautures(to_check_feautures, user_feauture)
        if similar > max_similarity:
            max_similarity = similar
            if max_similarity >= 0.3:
                best_match_user_name = user_name
            else:
                best_match_user_name = None

    return best_match_user_name, max_similarity



# match_user, similarity = check_user('data/00003.wav')
# print(match_user, similarity)


# Test thử
# conn = connect()
# print(conn)


# Hàm hiển thị danh sách
def show_user(name):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CustomUser where username = " + "\"" + name + "\"")

        row = cursor.fetchone()
        print(type(row))
        print(type(row[1]))
        array_f = eval(row[1])
        print(array_f[0][0])
        # while row is not None:
        #   print(row)
        #   row = cursor.fetchone()

    except Error as e:
        print(e)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()


# show_user("user1")

# cập nhật DL
def update_user(name,vector):
    # Câu lệnh update dữ liệu
    query = """ UPDATE CustomUser
              SET vector = %s
              WHERE username = %s """

    data = (name,vector)

    try:
        # Kết nối database
        conn = connect()

        # Cập nhật
        cursor = conn.cursor()
        cursor.execute(query, data)

        # Chấp nhận sự thay đổi
        conn.commit()

    except Error as error:
        print(error)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()

# xoas DL
def delete_user(id):
    query = "DELETE FROM CustomUser WHERE id = %s"

    try:
        conn = connect()

        # Thực thi câu truy vấn
        cursor = conn.cursor()
        cursor.execute(query, (id,))

        # Chấp nhận sự thay đổi
        conn.commit()

    except Error as error:
        print(error)

    finally:
        # Đóng kết nối
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # feature = extra_feature('data/00001.wav')
    # print(feature)
    # print(feature.size())
    # print(save_feautures(feature, 'boy1'))
    # save_feautures(feature,"girl","Nguyen","Hong","nguyenhong@gmail.com")
    # match_user, similarity = check_user('data/00002.wav')
    # print(match_user, similarity)
    delete_user(7)
    print(load_all_saved_user())





