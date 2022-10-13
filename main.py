DEBUG = False
if not DEBUG:
    import os

    os.environ["NTCHAT_LOG"] = "ERROR"

import ntchat_client

ntchat_client.init()
