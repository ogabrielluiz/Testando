from app import mongo
from app.models import load_user, Post
from datetime import datetime


def paginate(current_user_id, page_num, posts_per_page):
    """returns a set of documents belonging to page number `page_num`
    where size of each page is `posts_per_page`.
    """
    skip_stage = {"$skip": posts_per_page * (page_num - 1)}
    limit_stage = {"$limit": posts_per_page}
    pipeline = [{
        '$match': {
            '_id': current_user_id
        }
    }, {
        '$lookup': {
            'from': 'post',
            'localField': '_id',
            'foreignField': 'author',
            'as': 'posts'
        }
    }, {
        '$unwind': {
            'path': '$posts'
        }
    },

    ]
    if skip_stage["$skip"] > 0:
        pipeline.append(dict(skip_stage))
        pipeline.append(dict(limit_stage))
    else:
        pipeline.append(dict(limit_stage))

    cursor = mongo.db.usuario.aggregate(pipeline, allowDiskUse=True)
    # Return documents
    return cursor


def get_post_objects(cursor):
    list_of_posts = []
    for post in cursor:
        u = load_user(post['posts']['author'])
        p = Post(body=post['posts']['body'], author=u)
        list_of_posts.append(p)
    return list_of_posts



