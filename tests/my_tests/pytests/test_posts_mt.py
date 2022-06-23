import json
from webbrowser import get
from tests.utils import make_token

class TestAuthentication:
    """
    This tests all of the authentication cases possible for the /api/posts module.
    """

    # Authentication - 
    # user is authenticated with a matching token
    # user is not authenticated - no token
    # user is not authenticated - invalid or expired token
    def test_get_posts_authenticated(self, client):
        """
        Should return a 200 response.
        """
        token = make_token(2)
        query_params = {"authorIds":"2"}
        print("attempting auth test")
        response = client.get(
            "/api/posts", headers={"x-access-token": token}, query_string=query_params
        )
        print(response.json)
        assert response.status == "200 OK"

    def test_get_posts_unauthenticated(self, client):
        """
        Should return a 401 response.
        """
        query_params = {"authorIds":"1"}
        response = client.get(
            "/api/posts", headers={}, query_string=query_params
        )
        assert response.status == "401 UNAUTHORIZED"

    def test_get_posts_invalid_token(self, client):
        """
        should return a 401 response.
        """
        query_params = {"authorIds":"1"}
        response = client.get(
            "/api/posts", headers= {"x-access-token": ""}, query_string=query_params
        )
        assert response.status == "401 UNAUTHORIZED"

class TestAuthorIds:
    
    # AuthorsIds - 
    # ID field is not specified
    # ID value is blank
    # ID value is not valid format
    # ID is valid
    #   contains 1 ID no match
    #   contains 1 ID with one result found.
    #   contains 1 ID with multiple results found.
    #   contains multiple ids no match
    #   contains multiple IDs with one result found.
    #   contains multiple IDs with multiple results found, no shared matches
    #   contains multiple IDs with multiple results found, some matches shared between authors.
    def test_get_posts_authorIds_not_specified(self, client):
        """
        Should return an error stating that author Ids must be specified.
        """
        token = make_token(1)
        query_params = {
            "sortBy": "id",
            "direction": "asc"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_not_specified_expected_result, sort_keys=True)
    
    def test_get_posts_authorIds_blank(self, client):
        """
        Should return an error stating that authorids must be specified.
        """
        token = make_token(1)
        query_params = {
            "authorIds": "",
            "sortBy": "id",
            "direction": "asc"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_blank_expected_result, sort_keys=True)

    def test_get_posts_authorIds_not_valid_format(self,client):
        """
        should return an error stating that a passed id is not a valid int.
        """
        token = make_token(1)
        query_params = {
            "authorIds": "fred",
            "sortBy": "id",
            "direction": "asc"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_not_valid_format_expected_result, sort_keys=True)

    def test_get_posts_authorIds_one_id_no_match(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "4"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_one_id_no_match_expected_result, sort_keys=True)

    def test_get_posts_authorIds_one_id_one_match(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "1"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_one_id_one_match_expected_result, sort_keys=True)

    def test_get_posts_authorIds_one_id_multiple_match(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_one_id_multiple_match_expected_result, sort_keys=True)

    def test_get_posts_authorIds_multiple_ids_no_match(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "4,5"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_multiple_ids_no_match_expected_result, sort_keys=True)

    def test_get_posts_authorIds_multiple_ids_one_match_no_shared_authors(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "1,4"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_multiple_ids_one_match_no_shared_authors_expected_result, sort_keys=True)

    # can't be tested with data set provided.
    # def test_get_posts_authorIds_multiple_ids_one_match_shared_authors(self,client):
    #     token = make_token(1)
    #     query_params = {
    #         "authorIds": "4,5"
    #     }
    #     response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
    #     assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_mutliple_ids_one_match_shared_authors_expected_result, sort_keys=True)

    def test_get_posts_authorIds_multiple_ids_multiple_matches_no_shared_authors(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "1,3"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_multiple_ids_multiple_matches_no_shared_authors_expected_result , sort_keys=True)

    def test_get_posts_authorIds_multiple_ids_multiple_matches_shared_authors(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "1,2"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_authorIds_multiple_ids_multiple_matches_shared_authors_expected_result, sort_keys=True)

    get_posts_authorIds_one_id_no_match_expected_result = {
        # id 4
    }
    get_posts_authorIds_one_id_one_match_expected_result = {
        # id 1
    }
    get_posts_authorIds_one_id_multiple_match_expected_result = {
        # id 2
    }
    get_posts_authorIds_multiple_ids_no_match_expected_result = {
        # id 4,5
    }
    get_posts_authorIds_multiple_ids_one_match_no_shared_authors_expected_result = {
        # id 1,4
    }
    get_posts_authorIds_multiple_ids_multiple_matches_no_shared_authors_expected_result = {
        # id 1,3
    }
    get_posts_authorIds_multiple_ids_multiple_matches_shared_authors_expected_result = {
        # id 1,2
    }

    get_posts_authorIds_not_specified_expected_result = {
        "error":"Must specify at least 1 author Id as a positive integer."
    }

    get_posts_authorIds_blank_expected_result = {
        "error":"Must provide at least one authorId to search for."
    }

    get_posts_authorIds_not_valid_format_expected_result = {
        "error":"All ids passed must be a positive integer. Integers must be separated by a comma. [,]"
    }

class TestSortBy:
    # no sortBy passed.
    # blank sortBy passed.
    # invalid sortBy passed.
    # valid sortBy passed.
        # id
        # reads
        # likes
        # popularity
    def get_posts_sortBy_not_passed(self,client):
        """
        Should return data sorted by id.
        """
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "direction": "asc"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_sortBy_not_passed_expected_result, sort_keys=True)
    
    def get_posts_sortBy_blank(self,client):
        """
        should return data sorted by ID
        """
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "",
            "direction": "asc"
        }
        response = client.get("/api/posts", headers={"x-access-token": token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_sortBy_not_passed_expected_result, sort_keys=True)

    def get_posts_sortedBy_invalid(self,client):
        """
        should return a 400 error.
        """
        pass

    def get_posts_sortBy_id(self,client):
        """
        should return posts sorted by ID
        """
        pass

    def get_posts_sortBy_reads(self,client):
        """
        should return posts sorted by reads (views)
        """
        pass

    def get_posts_sortBy_likes(self,client):
        """
        should return posts sorted by likes
        """
        pass

    def get_posts_sortBy_popularity(self,client):
        """
        should return posts sorted by popularity
        """
        pass

    
    # sortBy mock data
    get_posts_sortBy_not_passed_expected_result = {
        "posts": [
            {
                "tags": ["food", "recipes", "baking"],
                "id": 1,
                "text": "Excepteur occaecat minim reprehenderit cupidatat dolore voluptate velit labore pariatur culpa esse mollit. Veniam ipsum amet eu dolor reprehenderit quis tempor pariatur labore. Tempor excepteur velit dolor commodo aute. Proident aute cillum dolor sint laborum tempor cillum voluptate minim. Amet qui eiusmod duis est labore cupidatat excepteur occaecat nulla.",
                "likes": 12,
                "reads": 5,
                "popularity": 0.19,
            },
            {
                "tags": ["travel", "hotels"],
                "id": 2,
                "text": "Ea cillum incididunt consequat ullamco nisi aute labore cupidatat exercitation et sunt nostrud. Occaecat elit tempor ex anim non nulla sit culpa ipsum aliquip. In amet in Lorem ut enim. Consectetur ea officia reprehenderit pariatur magna eiusmod voluptate. Nostrud labore id adipisicing culpa sunt veniam qui deserunt magna sint mollit. Cillum irure pariatur occaecat amet reprehenderit nisi qui proident aliqua.",
                "likes": 104,
                "reads": 200,
                "popularity": 0.7,
            },
            {
                "tags": ["travel", "airbnb", "vacation"],
                "id": 3,
                "text": "Voluptate consequat minim commodo nisi minim ut. Exercitation incididunt eiusmod qui duis enim sunt dolor sit nisi laboris qui enim mollit. Proident pariatur elit est elit consectetur. Velit anim eu culpa adipisicing esse consequat magna. Id do aliquip pariatur laboris consequat cupidatat voluptate incididunt sint ea.",
                "likes": 10,
                "reads": 32,
                "popularity": 0.7,
            },
        ],
    }
    get_posts_sortBy_blank_expected_result = get_posts_sortBy_not_passed_expected_result #same outcome
    get_posts_sortBy_id_expected_result = get_posts_sortBy_not_passed_expected_result #same outcome
    get_posts_sortBy_invalid_expected_results = {
        "error":'Invalid sortBy passed. Must be one of ["id","reads","likes","popularity"]'
    }
    get_posts_sortBy_reads_expected_result = {
        "posts": [
            {
                "tags": ["travel", "hotels"],
                "id": 2,
                "text": "Ea cillum incididunt consequat ullamco nisi aute labore cupidatat exercitation et sunt nostrud. Occaecat elit tempor ex anim non nulla sit culpa ipsum aliquip. In amet in Lorem ut enim. Consectetur ea officia reprehenderit pariatur magna eiusmod voluptate. Nostrud labore id adipisicing culpa sunt veniam qui deserunt magna sint mollit. Cillum irure pariatur occaecat amet reprehenderit nisi qui proident aliqua.",
                "likes": 104,
                "reads": 200,
                "popularity": 0.7,
            },
            {
                "tags": ["travel", "airbnb", "vacation"],
                "id": 3,
                "text": "Voluptate consequat minim commodo nisi minim ut. Exercitation incididunt eiusmod qui duis enim sunt dolor sit nisi laboris qui enim mollit. Proident pariatur elit est elit consectetur. Velit anim eu culpa adipisicing esse consequat magna. Id do aliquip pariatur laboris consequat cupidatat voluptate incididunt sint ea.",
                "likes": 10,
                "reads": 32,
                "popularity": 0.7,
            },
            {
                "tags": ["food", "recipes", "baking"],
                "id": 1,
                "text": "Excepteur occaecat minim reprehenderit cupidatat dolore voluptate velit labore pariatur culpa esse mollit. Veniam ipsum amet eu dolor reprehenderit quis tempor pariatur labore. Tempor excepteur velit dolor commodo aute. Proident aute cillum dolor sint laborum tempor cillum voluptate minim. Amet qui eiusmod duis est labore cupidatat excepteur occaecat nulla.",
                "likes": 12,
                "reads": 5,
                "popularity": 0.19,
            }
        ],
    }
    get_posts_sortBy_likes_expected_result = {
        "posts": [
            {
                "tags": ["travel", "hotels"],
                "id": 2,
                "text": "Ea cillum incididunt consequat ullamco nisi aute labore cupidatat exercitation et sunt nostrud. Occaecat elit tempor ex anim non nulla sit culpa ipsum aliquip. In amet in Lorem ut enim. Consectetur ea officia reprehenderit pariatur magna eiusmod voluptate. Nostrud labore id adipisicing culpa sunt veniam qui deserunt magna sint mollit. Cillum irure pariatur occaecat amet reprehenderit nisi qui proident aliqua.",
                "likes": 104,
                "reads": 200,
                "popularity": 0.7,
            },
            {
                "tags": ["food", "recipes", "baking"],
                "id": 1,
                "text": "Excepteur occaecat minim reprehenderit cupidatat dolore voluptate velit labore pariatur culpa esse mollit. Veniam ipsum amet eu dolor reprehenderit quis tempor pariatur labore. Tempor excepteur velit dolor commodo aute. Proident aute cillum dolor sint laborum tempor cillum voluptate minim. Amet qui eiusmod duis est labore cupidatat excepteur occaecat nulla.",
                "likes": 12,
                "reads": 5,
                "popularity": 0.19,
            },
            {
                "tags": ["travel", "airbnb", "vacation"],
                "id": 3,
                "text": "Voluptate consequat minim commodo nisi minim ut. Exercitation incididunt eiusmod qui duis enim sunt dolor sit nisi laboris qui enim mollit. Proident pariatur elit est elit consectetur. Velit anim eu culpa adipisicing esse consequat magna. Id do aliquip pariatur laboris consequat cupidatat voluptate incididunt sint ea.",
                "likes": 10,
                "reads": 32,
                "popularity": 0.7,
            }
        ],
    }
    #secondary sort by ID
    get_posts_sortBy_popularity_expected_result = {
        "posts": [
            {
                "tags": ["travel", "hotels"],
                "id": 2,
                "text": "Ea cillum incididunt consequat ullamco nisi aute labore cupidatat exercitation et sunt nostrud. Occaecat elit tempor ex anim non nulla sit culpa ipsum aliquip. In amet in Lorem ut enim. Consectetur ea officia reprehenderit pariatur magna eiusmod voluptate. Nostrud labore id adipisicing culpa sunt veniam qui deserunt magna sint mollit. Cillum irure pariatur occaecat amet reprehenderit nisi qui proident aliqua.",
                "likes": 104,
                "reads": 200,
                "popularity": 0.7,
            },
            {
                "tags": ["travel", "airbnb", "vacation"],
                "id": 3,
                "text": "Voluptate consequat minim commodo nisi minim ut. Exercitation incididunt eiusmod qui duis enim sunt dolor sit nisi laboris qui enim mollit. Proident pariatur elit est elit consectetur. Velit anim eu culpa adipisicing esse consequat magna. Id do aliquip pariatur laboris consequat cupidatat voluptate incididunt sint ea.",
                "likes": 10,
                "reads": 32,
                "popularity": 0.7,
            },
            {
                "tags": ["food", "recipes", "baking"],
                "id": 1,
                "text": "Excepteur occaecat minim reprehenderit cupidatat dolore voluptate velit labore pariatur culpa esse mollit. Veniam ipsum amet eu dolor reprehenderit quis tempor pariatur labore. Tempor excepteur velit dolor commodo aute. Proident aute cillum dolor sint laborum tempor cillum voluptate minim. Amet qui eiusmod duis est labore cupidatat excepteur occaecat nulla.",
                "likes": 12,
                "reads": 5,
                "popularity": 0.19,
            }
        ],
    }

class TestDirection:
    #No direction passed - asc
    #blank direction passed - asc
    #invalid direction passed - 400
    #asc passed
    #desc passed
    def test_get_posts_direction_not_passed(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "id"
        }
        response = client.get('/api/posts', headers={"x-access-token":token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_direction_not_passed_expected_result, sort_keys=True)

    def test_get_posts_direction_blank(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "id",
            "direction":""
        }
        response = client.get('/api/posts', headers={"x-access-token":token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_direction_blank_expected_result, sort_keys=True)


    def test_get_posts_direction_invalid_option(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "id",
            "direction":"invalid"
        }
        response = client.get('/api/posts', headers={"x-access-token":token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_direction_invalid_option_expected_result, sort_keys=True)

    def test_get_posts_direction_asc(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "id",
            "direction":"asc"
        }
        response = client.get('/api/posts', headers={"x-access-token":token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_direction_asc_expected_result, sort_keys=True)
    
    def test_get_posts_direction_desc(self,client):
        token = make_token(1)
        query_params = {
            "authorIds": "2",
            "sortBy": "id",
            "direction":"desc"
        }
        response = client.get('/api/posts', headers={"x-access-token":token}, query_string=query_params)
        assert json.dumps(response.json, sort_keys=True) == json.dumps(self.get_posts_direction_desc_expected_result, sort_keys=True)

    # default case
    get_posts_direction_asc_expected_result = {
        #sorted by id ascending
    }

    get_posts_direction_not_passed_expected_result = get_posts_direction_asc_expected_result
    get_posts_direction_blank_expected_result = get_posts_direction_asc_expected_result
    
    get_posts_direction_invalid_option_expected_result = {
        "error":'Invalid sort order specified. Must be one of ["asc","desc"]'
    }

    get_posts_direction_desc_expected_result = {
        # sorted by id descending
    }