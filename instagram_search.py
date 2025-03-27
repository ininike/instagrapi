from instagrapi import Client
import logging
from aiograpi.exceptions import (
    BadPassword, ReloginAttemptExceeded, ChallengeRequired,
    SelectContactPointRecoveryForm, RecaptchaChallengeForm,
    FeedbackRequired, PleaseWaitFewMinutes, LoginRequired
)
import asyncio

logger = logging.getLogger()
cl = Client()

USERNAME = 'asap.nike'
PASSWORD = 'ini100%!'

class InstagramSearch:
    
    @staticmethod
    async def search(query: str,USERNAME: str,PASSWORD: str) -> list:
        cl.login(USERNAME,PASSWORD)
        
        users = [ InstagramSearch._to_dict(user) for user in cl.search_users(query) ]
        for user in users:
            posts = [ InstagramSearch._to_dict(post) for post in cl.user_medias(user['pk']) ]
            
            # for post in posts:
            #     comments= cl.media_comments(media_id=post['pk'],amount=5)
            #     post['comments'] = [ InstagramSearch._to_dict(comment) for comment in comments ]
            #     # post['comments_min_id'] = comments_min_id
                
            stories = [ InstagramSearch._to_dict(post) for post in cl.user_stories(user['pk']) ]
            posts.extend(stories)
            user['posts'] = posts
        with open('response.txt','w',encoding='utf-8') as f:
            print(users)
            f.write(str(users))
            
    @staticmethod
    async def _fetch_next_comments(post_id: str, comments_end_cursor: str) -> dict:
        """ Paginate thtough comments"""
        comments, comments_end_cursor = cl.media_comments_gql_chunk(post_id, comments_end_cursor)
        comments = [ InstagramSearch._to_dict(comment) for comment in comments ]
        return {'comments': comments, 'comments_end_cursor': comments_end_cursor}
        
    @classmethod
    async def _login(self,USERNAME,PASSWORD):
        
        session = cl.load_settings("./session.json")

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

                    awaold_session = cl.get_settings()

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
        


if __name__ == '__main__':
     asyncio.run(InstagramSearch.search(query='imbryantbarnes',USERNAME=USERNAME,PASSWORD=PASSWORD))