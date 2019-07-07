from LocationTrendRepository import *

SETTINGS = load_settings()
auth_token = get_auth_token(SETTINGS)
digest = get_trends(auth_token, SETTINGS)

store_trends(digest)