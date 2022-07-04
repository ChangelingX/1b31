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
    # check for validation
    user = g.get("user")
    if user is None:
        return abort(401)

    args = request.args

    # Checks that authorIds, sortBy, direction all conform to requirements.
    # Returns 400 error and JSON error message otherwise.

    # confirm authorIds exists and contains a list of positive integers separated by commas.
    authorIds = args.get("authorIds")
    if authorIds is None:
        return (
            jsonify(
                {"error": "Must specify at least 1 author Id as a positive integer."}
            ),
            400,
        )
    if len(authorIds) == 0:
        return (
            jsonify({"error": "Must provide at least one authorId to search for."}),
            400,
        )
    try:
        authorIds = [
            int(x) for x in args.get("authorIds").split(",")
        ]  # split arg into an array of ints.
    except ValueError:
        return (
            jsonify(
                {
                    "error": "All ids passed must be a positive integer. Integers must be separated by a comma. [,]"
                }
            ),
            400,
        )

    print(f"authorIds: {authorIds}")

    # default to "id", error if passed value not valid.
    sortBy = args.get("sortBy")
    if sortBy is None:
        sortBy = "id"
    if len(sortBy) == 0:
        sortBy = "id"
    if sortBy not in VALID_SORTS:
        return (
            jsonify({"error": f"Invalid sortBy passed. Must be one of {VALID_SORTS}"}),
            400,
        )

    print(f"Sort by: {sortBy}")

    # default to ascending, error if passed value not valid.
    direction = args.get("direction")
    if direction is None:
        direction = "asc"
    if len(direction) == 0:
        direction = "asc"
    if direction not in ["asc", "desc"]:
        return (
            jsonify(
                {"error": 'Invalid sort order specified. Must be one of ["asc","desc"]'}
            ),
            400,
        )

    print(f"Direction: {direction}")

    # get matching posts
    matched_posts = set()  # use a set to automagically remove duplicates
    for author_id in authorIds:
        matched_posts.update(Post.get_posts_by_user_id(author_id))
    matched_posts = list(matched_posts)

    # sort matching posts using specified sort criteria and direction.
    # This can probably be a part of the posts model
    # for this coding exercise it works here.
    def sort_posts_by_criteria(posts_to_sort, criteria) -> list:
        def compare(this, that, criteria):
            if getattr(this, criteria) < getattr(that, criteria):
                return -1
            if getattr(this, criteria) > getattr(that, criteria):
                return 1
            if getattr(this, criteria) == getattr(that, criteria):
                if getattr(this, "id") < getattr(that, "id"):
                    return -1
                if getattr(this, "id") > getattr(that, "id"):
                    return 1
                if getattr(this, "id") == getattr(that, "id"):
                    return 0

        # adapted from
        # https://realpython.com/sorting-algorithms-python/#the-quicksort-algorithm-in-python
        def quicksort(posts_to_sort):
            if len(posts_to_sort) < 2:
                return posts_to_sort

            low, same, high = [], [], []

            pivot = posts_to_sort[randint(0, len(posts_to_sort) - 1)]

            for item in posts_to_sort:
                if compare(item, pivot, criteria) < 0:
                    low.append(item)
                if compare(item, pivot, criteria) == 0:
                    same.append(item)
                if compare(item, pivot, criteria) > 0:
                    high.append(item)

            return quicksort(low) + same + quicksort(high)

        return quicksort(posts_to_sort)

    if len(matched_posts) == 0:
        return (
            jsonify(
                {"no results": "There were no posts matching the criteria submitted."}
            ),
            200,
        )

    sorted_posts = sort_posts_by_criteria(matched_posts, sortBy)

    if direction == "desc":
        sorted_posts.reverse()

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
    # check for user authentication
    user = g.get("user")
    if user is None:
        return abort(401)

    # get post by ID, verify it actually exists.
    post = Post.get_post_by_post_id(post_id)
    if post is None:
        return jsonify({"error": f"Post with id {post_id} could not be found."}), 404

    # confirm requestor of edit is an author on the post.
    if not user.isAuthor(post):
        return (
            jsonify({"error": "Users may only edit their own posts using this API."}),
            401,
        )

    print("request:", request, request.json)
    print("unmodified post\n", post)
    data = request.json

    # Below: Extract variables from json data. Ignore variables with blank values.

    author_ids = tags = text = None
    # authorIds
    if "authorIds" in data.keys():
        author_ids = data["authorIds"]
        if not isinstance(author_ids, list):
            return (
                jsonify({"error": "Must pass a list of integers for author_ids."}),
                400,
            )
        if len(author_ids) == 0:
            return jsonify({"error": "Cannot set author_ids to a blank list."}), 400
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

    # tags
    if "tags" in data.keys():
        tags = data["tags"]
        if not isinstance(tags, list):
            return (
                jsonify(
                    {"error": f'Must pass a list of strings for tags. Got "{tags}"'}
                ),
                400,
            )
        if len(tags) == 0:
            return (
                jsonify({"error": f"Cannot apply an empty set of tags. Got {tags}"}),
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

    # text
    if "text" in data.keys():
        text = data["text"]
        if not isinstance(text, str):
            return (
                jsonify(
                    {"error": f"Must pass field 'text' as a string. Got {type(text)}"}
                ),
                400,
            )
        if len(text) == 0:
            return jsonify({"error": "Cannot set text to a zero-length string."})

    # actually do the changes needed now that all data is verified.
    if author_ids is not None:
        UserPost.query.filter_by(post_id=post_id).delete()
        for a_id in author_ids:
            user = User.query.get(a_id)
            db.session.add(UserPost(user_id=a_id, post_id=post_id))
        print("post within author_ids conditional:\n", post)

    if tags is not None:
        post.tags = tags

    if text is not None:
        post.text = text

    print("post after all conditionals:\n", post)
    db.session.commit()
    db.session.refresh(post)
    post = Post.get_post_by_post_id(post_id)
    print("post after commit:\n", post)

    print("Returned post:", post.serialize(withUsers=True))
    # return post by ID from database.
    return jsonify({"post": post.serialize(withUsers=True)}), 200
