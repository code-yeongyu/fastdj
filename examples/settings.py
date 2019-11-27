project_name = "community"  # snake_case suggested

user_model = {
    "custom_user": True,  # set to make custom user model
    "token_auth": True,  # set to use token auth to authenticate
    "allow_register": True,  # set to use auto-craeted register function
    "models": {
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
            "choices",
            "choices": [("ST", "STUDENT"), ("BS", "BUSINESS MAN"),
                        ("PR", "PROGRAMMER"), ("ETC", "ETC")],
            "options": ["max_length=2", "default=ETC"]
        }
    }
}

app = {
    "article": { # app name here
        "models": { # check available fields at https://docs.djangoproject.com/en/2.2/ref/models/fields/
            "writer": {
                "template": "model_owner"
                """
                replacable with:
                    field: "ForeignKey",
                    options: ["'auth.user'", "related_name='article_writer'", "on_delete=models.CASCADE", "null=False"],
                    serializer: { # check available fields at https://www.django-rest-framework.org/api-guide/fields/
                    field: "ReadOnlyField",
                    options: ["source='writer.username"]
                """
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
        "views": {
            "post_detail_view": { # make a route for reading, updating, deleting a post
                "template": "detail_view",
                "permissions": "AllowAny" # check available permission options at https://www.django-rest-framework.org/api-guide/permissions/#api-reference
            },
            "all_posts_view": { # make a route for read all datas of its model in the DB, create a data of its model in the DB
                "template": "all_objects_view",
                "permissions": "AllowAnyOrReadOnly" # check available permission options at https://www.django-rest-framework.org/api-guide/permissions/#api-reference
            },
            "my_posts_view": { # get all posts with writer = request.user
                "template": "filter_objects_view",
                "options": ["writer=request.user"]
            }
        }
    },
    "comment": {
        "models": {
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
        "views": {
            "get_comments_view": {
                "template": "filter_objects_view",
                "url_getters": "article_pk",
                "options": ["article_id=article_pk"]
            }
        }
    }
}