project_name = "community"  # snake_case suggested

user_model = {
    "token_auth": True,  # set to use token auth to authenticate
    "allow_register": True,  # set to use auto-craeted register function
    "fields":
    {  # check available fields at https://docs.djangoproject.com/en/2.2/ref/models/fields/
        "nickname": {
            "field": "CharField",
            "options": ["max_length=10"]
        },
        "bio": {
            "field": "TextField",
            "options": []
        },
        "website": {
            "field": "URLField",
            "options": []
        },
        "job": {
            "field":
            "ChoiceField",
            "choices": [("ST", "STUDENT"), ("BS", "BUSINESS MAN"),
                        ("PR", "PROGRAMMER"), ("ETC", "ETC")],
            "options": ["max_length=2", "default='ETC'"]
        }
    }
}

apps = {
    "article": { # app name here
        "models": {  # check available fields at https://docs.djangoproject.com/en/2.2/ref/models/fields/
            "Article":{
                "writer": {
                    "template": "model_owner"
                },
                "content": {
                    "field": "TextField",
                    "options": ["null=False", "blank=True"]
                },
                "tag": {
                    "field": "TextField",
                    "options": ['default=""']
                },
            },
        },
        "views": {
            "PostDetail": { # make a route for reading, updating, deleting a post
                "template": "detail_view_ud",
                "model": "Article",
                "permissions": "AllowAny" # check available permission options at https://www.django-rest-framework.org/api-guide/permissions/#api-reference
            },
            "PostOverall": { # make a route for read all posts of its model in the DB, create a data of its model in the DB
                "template": "all_objects_view",
                "model": "Article",
                "owner_field_name": "writer",
                "permissions": "AllowAnyOrReadOnly" # check available permission options at https://www.django-rest-framework.org/api-guide/permissions/#api-reference
            },
            "my_posts_view": { # get all posts with writer = request.user
                "template": "filter_objects_view",
                "model": "Article",
                "options": ["writer=request.user"]
            }
        }
    },
    "comment": {
        "models": {
            "Comment":{
                "writer": {
                    "template": "model_owner"
                },
                "article_id": {
                    "field": "IntegerField",
                    "options": ["null=False"]
                },
                "content": {
                    "field": "TextField",
                    "options": ["null=False", "blank=False"]
                },
            },
        },
        "views": {
            "get_comments_view": {
                "template": "filter_objects_view",
                "model": "Comment",
                "url_getters": "article_pk",
                "options": ["article_id=article_pk"]
            }
        }
    }
}

timezone = "Asia/Seoul"
language = 'ko-kr'