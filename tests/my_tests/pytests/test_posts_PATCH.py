import json
from webbrowser import get
from tests.utils import make_token

class TestAuthentication:
    def test_auth_not_authenticated(self,client):
        """sound return a 401 response"""
        post_id = 1
        data = {"tags": ["travel", "vacation"], "text": "my text", "authorIds": [1, 5]}
        response = client.patch(
            f"/api/posts/{post_id}",
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps(data),
        )
        assert response.status == "401 UNAUTHORIZED"


    def test_auth_not_an_author(self,client):
        pass

    def test_auth_as_author(self,client):
        pass

class TestFindPost:
    def test_postid_not_found(self,client):
        pass

    def test_postid_found(self,client):
        pass

class TestAuthorIds:
    def test_authorids_absent(self,client):
        pass

    def test_authorids_blank(self,client):
        pass

    def test_authorids_single_author(self,client):
        pass

    def test_authorids_multiple_authors(self,client):
        pass

class TestTags:
    def test_tags_absent(self,client):
        pass

    def test_tags_blank(self,client):
        pass

    def test_tags_single_tag(self,client):
        pass

    def test_tags_multiple_tags(self,client):
        pass

class TestText:
    def test_text_absent(self,client):
        pass

    def test_text_blank(self,client):
        pass

    def test_text_present(self,client):
        pass