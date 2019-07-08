import requests
import base64
import json
import pymysql
from datetime import datetime

def load_settings():
    """Function to load all the configuration settings for use throghout."""
    with open("settings.json", "r") as file:
        SETTINGS = json.loads(file.read())
    return SETTINGS
        
def get_auth_token(SETTINGS):
    """Function to get the authenticated access token for twitter API."""
    print ("Getting Twitter authentication ...", end = "")
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
        print ("FAILED!")
        return None
    print ("DONE!")
    return auth_resp.json()['access_token']
    
def get_trends(SETTINGS, auth_token):
    """Function to fetch the location trend data from twitter API."""
    print ("Fetching raw data from Twitter API...", end = "")
    headers = {
        'Authorization': 'Bearer {}'.format(auth_token)    
    }
    params = {
        'id': SETTINGS["woeid"]
    }

    url = '{}1.1/trends/place.json'.format(SETTINGS["base_url"])
    resp = requests.get(url, headers = headers, params = params)
    
    if resp.status_code != 200:
        print ("FAILED!")
        return None
    print ("DONE!")
    return resp.json()[0]
    
def store_trends(SETTINGS, digest):
    """Function to store the fetched location trends in SQL database."""
    try:
        print ("Storing data into DB...", end = "")
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
        
        #Insert Data in TwitterDigest Table
        query = """
            INSERT INTO TwitterDigest (
                created_at,
                as_of,
                woeid
            ) VALUES (
                (STR_TO_DATE('{}', '%Y-%c-%eT%TZ')),
                (STR_TO_DATE('{}', '%Y-%c-%eT%TZ')),
                {}
            )
        """.format(
            created_at,
            as_of,
            woeid
        )
        cursor.execute(query)
        
        #Store raw JSON
        query = """
            INSERT INTO DigestJson (
                date_time,
                digest
            ) VALUES (
                now(),
                '{}'
            )
        """.format(json.dumps(digest).replace("'", "\\'").replace('"', '\\"'))
        cursor.execute(query)
            
        #Get the max TwitterDigest ID:
        cursor.execute("SELECT MAX(id) FROM TwitterDigest")
        max_twitter_digest_id = int(cursor.fetchall()[0][0])
        
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
            name = trend["name"].replace("'", "\\'").replace('"', '\\"')
            if name[0] == "#": name = name[1:]
            try:
                tweet_volume = int(trend["tweet_volume"])
            except Exception as e:
                tweet_volume = "NULL"
            promoted_content = trend["promoted_content"]
            url = trend["url"]
            trend_values += "('{}', {}, '{}', '{}')".format(
                name,
                tweet_volume,
                promoted_content,
                url
            )
        query = """
            INSERT INTO Trends (
                name,
                tweet_volume,
                promoted_content,
                url
            ) VALUES {}
        """.format(trend_values)
        
        count = cursor.execute(query)
        new_trend_ids = [i for i in range(prev_trend_id + 1, prev_trend_id + count + 1)]
        id_combos = ""
        for id in new_trend_ids:
            if id_combos != "":
                id_combos += ","
            id_combos += "({}, {})".format(max_twitter_digest_id, id)
        
        #Insert into TimeTrendMapping
        query = """
            INSERT INTO TimeTrendMapping (
                digest_id,
                trend_id
            ) VALUES {}
        """.format(id_combos)
        cursor.execute(query)
        db.commit()
        print ("DONE!")
    except Exception as e:
        print ("FAILED!")
        raise(e)
        
def trend_in_interval(SETTINGS, start, end):
    """Function to retrieve data from SQL DB for trends in the given time interval."""
    try:
        trends = {}
        db = pymysql.connect(
            SETTINGS["db_host"], 
            SETTINGS["db_user"],
            SETTINGS["db_password"],
            SETTINGS["db_name"]
        )
        cursor = db.cursor()
        query = """
            SELECT 
                *
            FROM 
                TwitterDigest
            WHERE
               as_of >= '{}' and
               as_of <= '{}' and
               woeid = {}
        """.format(
            start,
            end,
            SETTINGS["woeid"]
        )
        cursor.execute(query)
        rows = cursor.fetchall()
        digest_ids = []
        for row in rows:
            digest_ids.append(row[0])
        if len(digest_ids) < 1:
            return trends
        
        trend_ids = []
        query = """
            SELECT 
                *
            FROM 
                TimeTrendMapping
            WHERE
               digest_id in ({})
        """.format(
            ",".join([str(d) for d in digest_ids])
        )
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            trend_ids.append(row[2])
        if len(trend_ids) < 1:
            return trends
        
        query = """
            SELECT 
                *
            FROM 
                Trends
            WHERE
               id in ({})
        """.format(
            ",".join([str(t) for t in trend_ids])
        )
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            trend = row[1].lower()
            if trend in trends:
                if trends[trend] is None:
                    trends[trend] = row[2]
                elif row[2] is not None and trends[trend] < row[2]:
                    trends[trend] = row[2]
            else:
                trends[trend] = row[2]
        return trends
    except Exception as e:
        raise(e)