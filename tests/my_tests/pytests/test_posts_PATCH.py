import json
from re import T
from webbrowser import get
from tests.utils import make_token

class TestAuthentication:
    def test_auth_not_authenticated(self,client):
        """sound return a 401 response"""
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "401 UNAUTHORIZED"

    def test_auth_not_an_author(self,client):
        """Should return a 401 response"""
        token = make_token(1)
        post_id = 2
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "401 UNAUTHORIZED"

    def test_auth_as_author(self,client):
        """Should return a 200 response with post body"""
        token = make_token(1)
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"

class TestFindPost:
    def test_postid_not_found(self,client):
        """Shound return a 404 error message"""
        token = make_token(1)
        post_id = -1
        data = {"tags": ["travel", "vacation"], "text": "my text", "authorIds": [1, 5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "404 NOT FOUND"

    def test_postid_found(self,client):
        """should return a 200 response with no content changes"""
        token = make_token(1)
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"

class TestAuthorIds:
    def test_authorids_absent(self,client):
        """should return HTTP 200 w/ a JSON response with no changes to authorIds"""
        token = make_token(1)
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_absent_expected_result, sort_keys=True)

    def test_authorids_blank(self,client):
        """should return HTTP 200 w/ a JSON response with no changes to authorIds"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":""}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_blank_expected_result, sort_keys=True)

    def test_authorids_empty_array(self,client):
        """should return HTTP 200 w/ a JSON response with no changes to authorIds"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":[]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_absent_expected_result, sort_keys=True)

    def test_authorids_invalid(self,client):
        """Should return a 400 code and a JSON error message"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":"1,5"}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "400 BAD REQUEST"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_invalid_expected_result, sort_keys=True)

    def test_authorids_nonexistant_author(self,client):
        """Should return HTTP 400 / a json with an error mesage"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":[-1]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "400 BAD REQUEST"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_nonexistant_author_expected_result, sort_keys=True)


    def test_authorids_single_author(self,client):
        """should return HTTP 200 / a JSON with modified authorIds"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":[1]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_nonexistant_author_expected_result, sort_keys=True)

    def test_authorids_multiple_authors(self,client):
        """Should reuturn HTTP 200 / a JSON with modified authorIds"""
        token = make_token(1)
        post_id = 1
        data = {"authorIds":[1,5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_multiple_authors_expected_result, sort_keys=True)

    patch_authorids_invalid_expected_result = {
        "error":"The passed authorIds (1,5) is not of a valid data type. Expected array of ints. E.x. [1,4]"
    }
    patch_authorids_nonexistant_author_expected_result = {
        "error":"The used referenced by id (-1) does not exist. Cannot add as author."
    }

class TestTags:
    def test_tags_absent(self,client):
        """should return a HTTP 200 / a json with no changes to tags"""
        token = make_token(1)
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_absent_expected_result, sort_keys=True)

    def test_tags_blank(self,client):
        """should return a HTTP 200 / a json with no changes to tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ""}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_blank_expected_result, sort_keys=True)

    def test_tags_empty_array(self,client):
        """Should return an HTTP 200 / a JSON with no changes to tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": []}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_empty_array_expected_result, sort_keys=True)

    def test_tags_invalid(self,client):
        """Should return a HTTP 406 / a JSON error message."""
        token = make_token(1)
        post_id = 1
        data = {"tags": "sports,music"}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_invalid_expected_result, sort_keys=True)

    def test_tags_single_tag(self,client):
        """should return a HTTP 200 / a json with new tag"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ["travel"]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_single_tag_expected_result, sort_keys=True)

    def test_tags_multiple_tags(self,client):
        """should return a HTTP 200 / a json with new tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ["travel", "vacation"]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tags_multiple_tags_expected_result, sort_keys=True)

class TestText:
    def test_text_absent(self,client):
        """Should return a HTTP 200 / a json with no changes to text"""
        token = make_token(1)
        post_id = 1
        data = {}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_text_absent_expected_result, sort_keys=True)

    def test_text_blank(self,client):
        """Should return a HTTP 200 / a json with no changes to text"""
        token = make_token(1)
        post_id = 1
        data = {"text": ""}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_text_blank_expected_result, sort_keys=True)

    def test_text_invalid(self,client):
        """Should return a HTTP 406 / a json with error message"""
        token = make_token(1)
        post_id = 1
        data = {"text": 1}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_text_invalid_expected_result, sort_keys=True)

    def test_text_present(self,client):
        """Should return a HTTP 200 / a json with changed to text"""
        token = make_token(1)
        post_id = 1
        data = {"text": "my text"}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_text_present_expected_result, sort_keys=True)

class TestMultiChanges:
    def test_change_author_ids_and_tags(self,client):
        """Shound return HTTP 200 / json with modified author id and tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ["travel", "vacation"], "authorIds":[1,5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_and_tags_expected_result, sort_keys=True)

    def test_change_author_ids_and_text(self,client):
        """Shound return HTTP 200 / json with modified author id and text"""
        token = make_token(1)
        post_id = 1
        data = {"text": "my text", "authorIds":[1,5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_authorids_and_text_expected_result, sort_keys=True)

    def test_change_tags_and_text(self,client):
        """Shound return HTTP 200 / json with modified text and tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ["travel", "vacation"], "text": "my text"}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_tag_and_text_expected_result, sort_keys=True)

    def test_change_author_ids_tags_and_text(self,client):
        """Shound return HTTP 200 / json with modified author id, text, and tags"""
        token = make_token(1)
        post_id = 1
        data = {"tags": ["travel", "vacation"], "text": "my text", "authorIds":[1,5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "x-access-token": token,
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "200 SUCCESS"
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.patch_all_expected_result, sort_keys=True)
