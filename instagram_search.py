from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio

logger = logging.getLogger()
cl = Client()

USERNAME = '----'
PASSWORD = '----'


class InstagramSearch:
    executor = ThreadPoolExecutor(max_workers=5)
    
    @staticmethod
    async def search(query: str,USERNAME: str,PASSWORD: str) -> list:
        cl.delay_range = [1, 3]
        cl.challenge_code_handler = challenge_code_handler
        login_user()
        users = [ InstagramSearch._to_dict(user) for user in cl.search_users(query) ]
        for user in users:
            posts = [ InstagramSearch._to_dict(post) for post in cl.user_medias(user['pk'],50) ]
            
            for post in posts:
                try:
                    comments , comments_min_id= await InstagramSearch.run_in_thread(cl.media_comments_chunk,post['pk'],100)
                except:
                    login_user()
                    comments , comments_min_id= await InstagramSearch.run_in_thread(cl.media_comments_chunk,post['pk'],100)
                post['comments'] = [ InstagramSearch._to_dict(comment) for comment in comments ]
                post['comments_min_id'] = comments_min_id
                
            # stories = [ InstagramSearch._to_dict(post) for post in cl.user_stories(user['pk']) ]
            # posts.extend(stories)
            user['posts'] = posts
        with open('response.txt','w',encoding='utf-8') as f:
            print(users)
            f.write(str(users))
            
    @classmethod
    async def run_in_thread(self, func, *args):
        """Run blocking functions inside a ThreadPoolExecutor asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)
            
    @staticmethod
    async def _fetch_next_comments(post_id: str, comments_min_id: str) -> dict:
        """ Paginate thtough comments"""
        comments, comments_min_id = cl.media_comments_chunk(post_id, 10, comments_min_id)
        comments = [ InstagramSearch._to_dict(comment) for comment in comments ]
        return {'comments': comments, 'comments_min_id': comments_min_id}
    
    @classmethod    
    def _to_dict(self, obj):
        dict = obj.__dict__
        dict = InstagramSearch._test_dict(dict)
        return dict
    
    @classmethod
    def _test_dict(self, dict: dict) -> bool:
            for k, v in dict.items():
                if type(v).__module__ == 'instagrapi.types':
                    dict[k] = InstagramSearch._to_dict(dict[k])
                    continue
                if isinstance(v,list):
                    for i, obj in enumerate(v):
                        if type(obj).__module__ == 'instagrapi.types':
                            dict[k][i] = InstagramSearch._to_dict(dict[k][i])
            return dict
        
"""--------`------------------------------------------------------------"""
        
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import logging

logger = logging.getLogger()

def login_user():
    """
    Attempts to login to Instagram using either the provided session information
    or the provided username and password.
    """
    session = cl.load_settings("session.json")

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            cl.set_settings(session)
            cl.login(USERNAME, PASSWORD)

            # check if session is valid
            try:
                cl.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = cl.get_settings()

                # use the same device uuids across logins
                cl.set_settings({})
                cl.set_uuids(old_session["uuids"])

                cl.login(USERNAME, PASSWORD)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if cl.login(USERNAME, PASSWORD):
                login_via_pw = True
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session")
"""--------------------------------------------------------------------"""
        
"""
Handle Email/SMS challenges
"""
import email
import imaplib
import re

from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice

CHALLENGE_EMAIL = "____@gmail.com"
CHALLENGE_PASSWORD = "____"

def get_code_from_email(username):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(CHALLENGE_EMAIL, CHALLENGE_PASSWORD)
    mail.select("inbox")
    result, data = mail.search(None, "(UNSEEN)")
    assert result == "OK", "Error1 during get_code_from_email: %s" % result
    ids = data.pop().split()
    for num in reversed(ids):
        mail.store(num, "+FLAGS", "\\Seen")  # mark as read
        result, data = mail.fetch(num, "(RFC822)")
        assert result == "OK", "Error2 during get_code_from_email: %s" % result
        msg = email.message_from_string(data[0][1].decode())
        payloads = msg.get_payload()
        if not isinstance(payloads, list):
            payloads = [msg]
        code = None
        for payload in payloads:
            body = str(payload.get_payload(decode=True))
            if "<div" not in body:
                continue
            match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
            if not match:
                continue
            print("Match from email:", match.group(1))
            match = re.search(r">(\d{6})<", body)
            if not match:
                print('Skip this email, "code" not found')
                continue
            code = match.group(1)
            if code:
                return code
    return False


def get_code_from_sms(username):
    while True:
        code = input(f"Enter code (6 digits) for {username}: ").strip()
        if code and code.isdigit():
            return code
    return None


def challenge_code_handler(username, choice):
    if choice == ChallengeChoice.SMS:
        return get_code_from_sms(username)
    elif choice == ChallengeChoice.EMAIL:
        return get_code_from_email(username)
    return False

"""--------------------------------------------------------------------"""     


if __name__ == '__main__':
     asyncio.run(InstagramSearch.search(query='imbryantbarnes',USERNAME=USERNAME,PASSWORD=PASSWORD))
