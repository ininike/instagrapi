from instagrapi import Client

def to_dict(obj):
    if isinstance(obj, list):
        return [ o.__dict__ for o in obj]
    dict = obj.__dict__
    return dict

cl = Client()
cl.login('frankthom596','ini100%!')

"""
Media types:
Photo - When media_type=1
Video - When media_type=2 and product_type=feed
IGTV - When media_type=2 and product_type=igtv
Reel - When media_type=2 and product_type=clips
Album - When media_type=8
"""

# user_id = cl.user_id_from_username('imbryantbarnes')
# user_medias = to_dict(cl.user_medias(user_id=user_id))
# user_stories = to_dict(cl.user_stories(user_id=user_id))
# user_reels = to_dict(cl.user_clips(user_id=user_id))
# user_highlights = to_dict(cl.user_highlights(user_id=user_id))
# medias_user_tagged = to_dict(cl.usertag_medias(user_id=user_id))
# general_search = to_dict(cl.top_search('lebron'))
# threads_search = to_dict(cl.direct_search('lebron'))
# user_search = to_dict(cl.search_users('ini ad'))
# tag_search = to_dict(cl.search_hashtags('lebron'))
# tags_media = to_dict(cl.hashtag_medias_v1(name='viral',amount=50))
# tags_reels = to_dict(cl.hashtag_medias_reels_v1('trending'))
# location = cl.location_search(6.4998,3.3608)[0]
# location = to_dict(cl.location_complete(location))
# location_media = to_dict(cl.location_medias_top(location['pk']))
comments, i = (cl.media_comments_chunk('3572482985196953810',10))
# to_dict(comments)

print(comments)





