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

USERNAME = ''
PASSWORD = ''

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
