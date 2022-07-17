# Prompt

The product team has decided that we want to make a change to this application such that authors of a blog post can have different roles:

    Authors can be owners, editors, or viewers of a blog post. For any blog post, there must always be at least one owner of the blog post. Only owners of a blog post can modify the authors' list to a blog post (adding more authors, changing their role).

Questions:

    What database changes would be required to the starter code to allow for different roles for authors of a blog post? Imagine that we’d want to also be able to add custom roles and change the permission sets for certain roles on the fly without any code changes.
    How would you have to change the PATCH route given your answer above to handle roles?

Considerations

    Please format your answers so that they are easy to digest, and do not include any code in your pull request related to these questions above. We will be evaluating both the quality of your answer as well as the quality of your written explanation of that answer.
    Please include a file in the root of the repo called roles-proposal.md that addresses these questions.

## Response

### 1. What database changes [...]?

I would modify the user_post table to contain a Role field for each row. This would mean that for each user-post relationship, there would also be an associated Role. I would define the relationship to validate that at least one of the entries in the relationship was an Owner. 

I would then create a Role table which contained the Roles and their permissions. The permissions would be (C)reate, (R)ead, (U)pdate, (D)elete. Owners would have CRUD, Editors would have RU, viewers would only have R. This table would facilitate adding new roles and permissions as necessary, without requiring a change to legacy code as new roles or permissions were added.

It may be appropriate to break out things like Update Users, Update Text, etc. for the Update role rather than having it be one monolithic permission.

### 2. How would you have to change the PATCH route [...]?

When the user submits a request, rather than just confirming that the user was associated with the post, it would also confirm that the user has the appropriate permission (Update) in its Role relationship with the post for the given action. 

For updating tags or text, the user would need to be in a role which had the Update value set. For updating Users, the user would need to have the Owner role associated (or would need to have the Update Users permission associated with their role).

Possible edge cases include:

1. A user trying to update a database entry that they are not authorized to modify at all - This would result in a 401 code being returned.
2. A user trying to update a field of a database entry that they are not authorized to modify - this would also return a 401.
3. A user trying to remove the last Owner of a post. This would need to return a 400 error to show that the request is malformed given the state of the database.
4. A user trying to view a post they are not a Reader for. This would return a 401 forbidden error.