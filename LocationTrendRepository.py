import requests
import base64
import json
import pymysql

def load_settings():
    global SETTINGS
    
    with open('settings.json','r') as file:
        SETTINGS = json.loads(file.read())
    return SETTINGS
        
def get_auth_token(SETTINGS):
    key_secret = '{}:{}'.format(SETTINGS["client_key"], SETTINGS["client_secret"]).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')
    
    auth_url = '{}oauth2/token'.format(SETTINGS["base_url"])
    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    auth_data = {
        'grant_type': 'client_credentials'
    }
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
    if auth_resp.status_code != 200:
        return None
    return auth_resp.json()['access_token']
    
def get_trends(auth_token, SETTINGS):
    headers = {
        'Authorization': 'Bearer {}'.format(auth_token)    
    }
    params = {
        'id': SETTINGS["woeid"]
    }

    url = '{}1.1/trends/place.json'.format(SETTINGS["base_url"])
    resp = requests.get(url, headers = headers, params = params)
    
    if resp.status_code != 200:
        return None
    
    return resp.json()[0]
    
def store_trends(digest):
    try:
        db = pymysql.connect(
            SETTINGS["db_host"], 
            SETTINGS["db_user"],
            SETTINGS["db_password"],
            SETTINGS["db_name"]
        )
        cursor = db.cursor()
        
        created_at = digest["created_at"]
        as_of = digest["as_of"]
        woeid = digest["locations"][0]["woeid"]
        location_name = digest["locations"][0]["name"]
        
        #Insert into Location if needed
        count = cursor.execute("SELECT * FROM Locations WHERE woeid = {}".format(woeid))
        if count == 0:
            query = """
                INSERT INTO Locations (
                    woeid,
                    name
                ) VALUES (
                    {},
                    '{}'
                )
            """.format(
                woeid,
                location_name
            )
            cursor.execute(query)
        
        #Insert Data in DailyDigest Table
        query = """
            INSERT INTO DailyDigest (
                created_at,
                as_of,
                woeid
            ) VALUES (
                '{}',
                '{}',
                {}
            )
        """.format(
            created_at,
            as_of,
            woeid
        )
        cursor.execute(query)
            
        #Get the max DailyDigest ID:
        cursor.execute("SELECT MAX(id) FROM DailyDigest")
        max_daily_digest_id = int(cursor.fetchall()[0][0])
        
        #Get the max Trend ID:
        cursor.execute("SELECT MAX(id) FROM Trends")
        prev_trend_id = cursor.fetchall()[0][0]
        if prev_trend_id:
            prev_trend_id = int(prev_trend_id)
        else:
            prev_trend_id = 0
        
        #Insert data in Trend
        trends = digest["trends"]
        trend_values = ""
        for trend in trends:
            if trend_values != "":
                trend_values += ","
            trend_values += "('{}', '{}', '{}', '{}')".format(
                trend["name"], 
                trend["tweet_volume"], 
                trend["promoted_content"],
                trend["url"]
            )
        query = """
            INSERT INTO Trends (
                name,
                tweet_volume,
                promoted_content,
                url
            ) VALUES {}
        """.format(trend_values)
        
        print(prev_trend_id)
        count = cursor.execute(query)
        new_trend_ids = [i for i in range(prev_trend_id + 1, prev_trend_id + count + 1)]
        id_combos = ""
        for id in new_trend_ids:
            if id_combos != "":
                id_combos += ","
            id_combos += "({}, {})".format(max_daily_digest_id, id)
        
        #Insert into DailyTrends
        query = """
            INSERT INTO DailyTrends (
                daily_digest_id,
                trend_id
            ) VALUES {}
        """.format(id_combos)
        cursor.execute(query)
        db.commit()
    except Exception as e:
        db.commit()
        raise(e)