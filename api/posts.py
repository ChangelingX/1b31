from flask import jsonify, request, g, abort, Response

from api import api
from db.shared import db
from db.models.user_post import UserPost
from db.models.post import Post

from db.utils import row_to_dict
from middlewares import auth_required

VALID_SORTS = ["id","reads","likes","popularity"]

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

@api.get('/posts')
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
        return jsonify({"error":"Must specify at least 1 author Id as a positive integer."}),400
    if len(authorIds) == 0:
        return jsonify({"error":"Must provide at least one authorId to search for."}),400
    try:
        authorIds = [int(x) for x in args.get("authorIds").split(",")] #split arg into an array of ints.
    except ValueError:
        return jsonify({"error":"All ids passed must be a positive integer. Integers must be separated by a comma. [,]"}),400

    print(f"authorIds: {authorIds}")

    #default to "id", error if passed value not valid.
    sortBy = args.get("sortBy")
    if sortBy is None:
        sortBy = "id"
    if sortBy not in VALID_SORTS:
        return jsonify({"error":f'Invalid sortBy passed. Must be one of {VALID_SORTS}'}),400

    print(f"Sort by: {sortBy}")

    #default to ascending, error if passed value not valid.
    direction = args.get("direction")  
    if direction is None:
        direction = "asc"
    if direction not in ["asc","desc"]:
        return jsonify({"error":'Invalid sort order specified. Must be one of ["asc","desc"]'}),400
    
    print(f"Direction: {direction}")

    return Response(status=200)

@api.patch('/posts')
@auth_required
def update_posts():
    pass