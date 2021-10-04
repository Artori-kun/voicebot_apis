# import required libraries
import kwargs as kwargs
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import numpy as np
from django_apis.core.voice_utils import extra_feature
from django_apis.core.voice_utils import compare_similarity, compare_feautures
from mysql.connector import MySQLConnection, Error
import time
import torch
import wave
import numpy as np
def  record_signup(user, vector):
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = 5

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()
    # Convert the NumPy array to audio file
    wv.write("data/record.wav", recording, freq, sampwidth=2)
    feature= extra_feature('data/record.wav')
    return save_feautures(feature, user, vector)


def record_log_in():
    # Sampling frequency
    freq = 44100

    # Recording duration
    duration = 5

    # Start recorder with the given values
    # of duration and sample frequency
    recording = sd.rec(int(duration * freq),
                       samplerate=freq, channels=1)

    # Record audio for the given number of seconds
    sd.wait()
    # Convert the NumPy array to audio file
    wv.write("data/recording1.wav", recording, freq, sampwidth=2)
    feature = extra_feature('data/recording1.wav')
    max_similarity = 0
    match_user = None
    match_user, similarity = check_user('data/recording1.wav')
    if max_similarity >= 0.3:
        result = match_user
    else:
        result = None
    return result
# record()
# print(extra_feature("record_file/recording1.wav"))
def _login(file_name):
    all_saved_users = load_all_saved_user()
    to_check_feautures = extra_feature(file_name)
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

    return best_match_user_name

def save_wav_channel(fn, wav, channel):
    '''
    Take Wave_read object as an input and save one of its
    channels into a separate .wav file.
    '''
    # Read data
    nch   = wav.getnchannels()
    depth = wav.getsampwidth()
    wav.setpos(0)
    sdata = wav.readframes(wav.getnframes())

    # Extract channel data (24-bit data not supported)
    typ = { 1: np.uint8, 2: np.uint16, 4: np.uint32 }.get(depth)
    if not typ:
        raise ValueError("sample width {} not supported".format(depth))
    if channel >= nch:
        raise ValueError("cannot extract channel {} out of {}".format(channel+1, nch))
    data = np.fromstring(sdata, dtype=typ)
    ch_data = data[channel::nch]

    # Save channel to a separate file
    outwav = wave.open(fn, 'w')
    outwav.setparams(wav.getparams())
    outwav.setnchannels(1)
    outwav.writeframes(ch_data.tostring())
    outwav.close()

# wav = wave.open('data/ha1.wav')
# save_wav_channel('data/ha1.wav', wav, 0)
# print(extra_feature("data/ha1.wav"))

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

if __name__ == "__main__":
    print(_login('data/00003.wav'))
    # print(record_signup( 'user14', 'saved_feautures/f.pt'))
    # print(extra_feature("record_file/recording1.wav"))
    # feature = extra_feature('record_file/recording1.wav')
    # print(save_feautures(feature, 'userman', 'saved_feautures/f4.pt'))
    # print(load_all_saved_user())
    # match_user, similarity = check_user('data/ha1.wav')
    # print(match_user, similarity)

