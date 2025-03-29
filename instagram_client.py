from instagrapi import Client
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio
from instagrapi.exceptions import LoginRequired
import email
import imaplib
import re
from instagrapi.mixins.challenge import ChallengeChoice
import time
import os  # Add this import at the top of the file

SESSION_DIRECTORY = './sessions'

class InstagramClient:
    def __init__(self, username: str, password: str, email:str , email_password:str, email_host:str):
        """
        Initialize the InstagramClient with the provided username, password, and email credentials.
        """
        self.username = username
        self.password = password
        self.email = email
        self.email_password = email_password
        self.email_host = email_host
        self.filepath = ''
        self.cl = Client()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def search(self, query: str) -> list:
        """
        Search for users and their posts based on the provided query.
        For each user, fetch their posts and comments.
        """
        self.cl.delay_range = [1, 3]
        self.cl.handle_exception = self._handle_exception
        self.cl.challenge_code_handler = self._challenge_code_handler
        self._get_session()
        self._login_user()
        users = [ self._to_dict(user) for user in self.cl.search_users(query) ]
        for user in users:
            posts = [ self._to_dict(post) for post in self.cl.user_medias(user['pk']) ]
            """i just commeneted out the comments part"""
            # for post in posts:
            #     comments , comments_min_id= await self._run_in_thread(self.cl.media_comments_chunk,post['pk'],10)
            #     post['comments'] = [ self._to_dict(comment) for comment in comments ]
            #     post['comments_min_id'] = comments_min_id
                
            stories = [ self._to_dict(post) for post in self.cl.user_stories(user['pk']) ]
            posts.extend(stories)
            user['posts'] = posts
        with open('response.txt','w',encoding='utf-8') as f:
            print(users)
            f.write(str(users))
    
    async def fetch_next_comments(self, post_id: str, comments_min_id: str) -> dict:
        """ Paginate thtough comments"""
        comments, comments_min_id = self.cl.media_comments_chunk(post_id, 10, comments_min_id)
        comments = [ self._to_dict(comment) for comment in comments ]
        return {'comments': comments, 'comments_min_id': comments_min_id}
                
    async def _run_in_thread(self, func, *args):
        """Run blocking functions inside a ThreadPoolExecutor asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, func, *args)
            
        
    def _to_dict(self, obj):
        dict = obj.__dict__
        dict = self._test_dict(dict)
        return dict
    
    def _test_dict(self, dict: dict) -> bool:
            for k, v in dict.items():
                if type(v).__module__ == 'instagrapi.types':
                    dict[k] = self._to_dict(dict[k])
                    continue
                if isinstance(v,list):
                    for i, obj in enumerate(v):
                        if type(obj).__module__ == 'instagrapi.types':
                            dict[k][i] = self._to_dict(dict[k][i])
            return dict
        
    def _login_user(self):
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """
        session = self.cl.load_settings(SESSION_DIRECTORY + f'/{self.username}.json')

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.cl.set_settings(session)
                self.cl.login(self.username, self.password)

                #check if session is valid
                try:
                    self.cl.get_timeline_feed()
                except LoginRequired:
                    logging.info("Session is invalid, need to login via username and password")

                    old_session = self.cl.get_settings()

                    # use the same device uuids across logins
                    self.cl.set_settings({})
                    self.cl.set_uuids(old_session["uuids"])

                    self.cl.login(self.username, self.password)
                login_via_session = True
            except Exception as e:
                logging.info("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            try:
                logging.info("Attempting to login via username and password. username: %s" % self.username)
                if self.cl.login(self.username, self.password):
                    login_via_pw = True
            except Exception as e:
                logging.info("Couldn't login user using username and password: %s" % e)

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

    def _get_session(self):
        """
        Create a session file if it does not already exist.
        """
        if not os.path.exists(SESSION_DIRECTORY + f'/{self.username}.json'):  # Check if the session file exists
            try:
                # Login and create the session file
                self.cl.login(self.username, self.password)
                self.cl.dump_settings(SESSION_DIRECTORY + f'/{self.username}.json')
                logging.info(f"Session file created for user: {self.username}")
            except Exception as e:
                logging.error(f"Error creating session for user {self.username}: {e}")
                raise
        else:
            logging.info(f"Session file already exists for user: {self.username}")
        
    def _challenge_code_handler(self,username, choice):
        if choice == ChallengeChoice.phon:
            return self.get_code_from_sms(username)
        elif choice == ChallengeChoice.EMAIL:
            return self.get_code_from_email(username)
        return False
        
    def _get_code_from_sms(self, username):
        attempts = 3
        while attempts > 0:
            code = input(f"Enter code (6 digits) for {username}: ").strip()
            if code and code.isdigit() and len(code) == 6:
                return code
            attempts -= 1
            print(f"Invalid code. {attempts} attempts remaining.")
        raise Exception("Failed to provide a valid code.")
    
    def _get_code_from_email(self):
        timeout = 60  # Wait for up to 60 seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            mail = imaplib.IMAP4_SSL(self.email_host)
            mail.login(self.email, self.email_password)
            mail.select("inbox")
            result, data = mail.search(None, "(UNSEEN)")
            if result != "OK":
                raise Exception(f"Error during get_code_from_email: {result}")

            ids = data[0].split()
            if ids:
                for num in reversed(ids):
                    result, data = mail.fetch(num, "(RFC822)")
                    if result != "OK":
                        raise Exception(f"Error fetching email: {result}")

                    msg = email.message_from_bytes(data[0][1])
                    body = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    match = re.search(r"\b\d{6}\b", body)
                    if match:
                        code = match.group(0)
                        mail.store(num, "+FLAGS", "\\Seen")  # Mark as read
                        return code
            time.sleep(5)  # Wait for 5 seconds before checking again

        raise Exception("Timeout waiting for verification code.")
    
    def _handle_exception(self, client, e):
        if isinstance(e, LoginRequired):
            logging.exception(e)
            client.relogin()
            return
        raise e
    
    def __del__(self):
        self.executor.shutdown(wait=True)