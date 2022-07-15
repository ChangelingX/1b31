from flask import jsonify, request, g, abort, Response
from random import randint

from api import api
from db.models.user import User
from db.shared import db
from db.models.user_post import UserPost
from db.models.post import Post

from db.utils import row_to_dict
from middlewares import auth_required

VALID_SORTS = ["id", "reads", "likes", "popularity"]


@api.post("/posts")
@auth_required
def posts():
    # validation
    user = g.get("user")
    if user is None:
        return abort(401)

    data = request.get_json(force=True)
    text = data.get("text", None)
    tags = data.get("tags", None)
    if text is None:
        return jsonify({"error": "Must provide text for the new post"}), 400

    # Create new post
    post_values = {"text": text}
    if tags:
        post_values["tags"] = tags

    post = Post(**post_values)
    db.session.add(post)
    db.session.commit()

    user_post = UserPost(user_id=user.id, post_id=post.id)
    db.session.add(user_post)
    db.session.commit()

    return row_to_dict(post), 200


@api.get("/posts")
@auth_required
def get_posts():
    """
    Accepts a GET request. The query string specifies which criteria to consider when returning posts.
    Returns posts and their content as a JSON payload, with HTTPResponseCode.

    :param authorIds: (str) Comma separated list of integers, as a string e.g. "1,5"
    :param sortBy: (str) field name to sort by. Options are "id, reads, likes, popularity. Default is "id".
    :param direction: (str) Sorting direction of results. Options are "asc" and "desc". Default is "asc".
    :returns: JSON object in the format {"posts":{"id":(int),"likes":(int),"popularity":(float),"reads":(int),"tags":[(str),(str),[...]],"text":(str)},[...]}, HTTPResponseCode
    :returns: JSON object in the format {"error":"<error message"}
    """
    user = g.get("user")
    if user is None:
        return abort(401)

    args = request.args

    authorIds = args.get("authorIds")
    if authorIds is None or len(authorIds) == 0:
        return (
            jsonify(
                {"error": "Must specify at least 1 author Id as a positive integer."}
            ),
            400,
        )
    try:
        authorIds = [
            int(x) for x in args.get("authorIds").split(",")
        ]
    except ValueError:
        return (
            jsonify(
                {
                    "error": "All ids passed must be a positive integer. Integers must be separated by a comma. [,]"
                }
            ),
            400,
        )

    sortBy = args.get("sortBy")
    if sortBy is None or len(sortBy) == 0:
        sortBy = "id"
    if sortBy not in VALID_SORTS:
        return (
            jsonify({"error": f"Invalid sortBy passed. Must be one of {VALID_SORTS}"}),
            400,
        )

    direction = args.get("direction")
    if direction is None or len(direction) == 0:
        direction = "asc"
    if direction not in ["asc", "desc"]:
        return (
            jsonify(
                {"error": 'Invalid sort order specified. Must be one of ["asc","desc"]'}
            ),
            400,
        )

    matched_post_ids = set()  # use a set to automagically remove duplicates
    for author_id in authorIds:
        a_id_matched_posts = Post.get_posts_by_user_id(author_id)
        for post in a_id_matched_posts:
            matched_post_ids.add(post.post_id)
    matched_posts = []
    for post_id in matched_post_ids:
        matched_posts.append(Post.get_post_by_post_id(post_id))

    if len(matched_posts) == 0:
        return (
            jsonify(
                {"no results": "There were no posts matching the criteria submitted."}
            ),
            404,
        )

    def sort_by_criteria(posts_to_sort, criteria="id", direction="asc"):
        if direction == "asc":
            reverse = False
        else:
            reverse = True
        match criteria:
            case "id":
                posts_to_sort.sort(key=lambda x: (x.id), reverse=reverse)
            case "reads":
                posts_to_sort.sort(key=lambda x: (x.reads, x.id), reverse=reverse)
            case "likes":
                posts_to_sort.sort(key=lambda x: (x.likes, x.id), reverse=reverse)
            case "popularity":
                posts_to_sort.sort(key=lambda x: (x.popularity, x.id), reverse=reverse)
        return posts_to_sort

    sorted_posts = sort_by_criteria(matched_posts, sortBy, direction)
    print(sorted_posts)

    return jsonify({"posts": [i.serialize() for i in sorted_posts]}), 200


@api.patch("/posts/<post_id>")
@auth_required
def update_posts(post_id):
    """
    Accepts a PATCH request accompanied by a json object.
    The url /posts/<post_id/ field identifies which post to update.
    The JSON object sent with the patch request determines which values of the post to update.
    The PATCH request must be authenticated by a token from a user who is a listed author on the post.
    All fields are optional, any not passed will not be changed.

    :param post_id: (int) the numerical id of the post.
    :param authorIds: list(int) a list of numerical author ids.
    :param tags: list(str) a list of tags to apply to the post.
    :param text: (str) the body of the post.
    :returns: a JSON object of the updated post.
    :returns: a JSON object containing an error code.
    """
    user = g.get("user")
    if user is None:
        return abort(401)

    post = Post.get_post_by_post_id(post_id)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} could not be found."}), 400

    if not user.isAuthor(post):
        return (
            jsonify({"error": "Users may only edit their own posts using this API."}),
            401,
        )
    data = request.json

    author_ids = tags = text = None

    if "authorIds" in data.keys():
        author_ids = data["authorIds"]
        if not isinstance(author_ids, list) or len(author_ids) == 0:
            return (
                jsonify({"error": "Must pass a list of integers for author_ids."}),
                400,
            )
        for author_id in author_ids:
            if not isinstance(author_id, int):
                return (
                    jsonify(
                        {
                            "error": f"Must pass a list of integers for authorIds. Got {author_ids}"
                        }
                    ),
                    400,
                )
            if User.query.get(author_id) is None:
                return (
                    jsonify(
                        {
                            "error": f"The used referenced by id ({author_id}) does not exist. Cannot add as author."
                        }
                    ),
                    400,
                )

    if "tags" in data.keys():
        tags = data["tags"]
        if not isinstance(tags, list) or len(tags) == 0:
            return (
                jsonify(
                    {"error": f'Must pass a list of strings for tags. Got "{tags}"'}
                ),
                400,
            )
        for tag in tags:
            if not isinstance(tag, str):
                return (
                    jsonify(
                        {"error": f'Must pass a list of strings for tags. Got "{tags}"'}
                    ),
                    400,
                )
            if len(tag) == 0:
                return (
                    jsonify(
                        {"error": f'Cannot apply a zero-lenth tag. Got tag of "{tag}"'}
                    ),
                    400,
                )

    if "text" in data.keys():
        text = data["text"]
        if not isinstance(text, str) or len(text) == 0:
            return (
                jsonify(
                    {"error": f"Must pass field 'text' as a string of non-zero length. Got {type(text)}, {text}"}
                ),
                400,
            )

    #TODO: Add / remove users as a batch
    if author_ids is not None:
        # get existing author ids for post
        # for each new author, check if they are present in the old list or not.
        # if only present in old list, add to list to remove
        # if present in only new list, add to list to add
        old_userposts = UserPost.query.filter_by(post_id=post_id)
        old_user_ids = []
        for userpost in old_userposts:
            old_user_ids.append(userpost.user_id)
        users_to_remove = set(old_user_ids).difference(author_ids)
        users_to_add = set(author_ids).difference(old_user_ids)
        for user_rem in users_to_remove:
            post_to_delete = UserPost.query.filter_by(user_id=user_rem, post_id=post_id).one()
            db.session.delete(post_to_delete)
        for user_add in users_to_add:
            db.session.add(UserPost(user_id=user_add, post_id=post_id))


    if tags is not None:
        post.tags = tags

    if text is not None:
        post.text = text

    db.session.commit()
    db.session.refresh(post)
    post = Post.get_post_by_post_id(post_id)

    return jsonify({"post": post.serialize(withUsers=True)}), 200
