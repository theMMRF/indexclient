"""Caller credentials and the opt-in visibility field survive client operations."""

import json
from unittest.mock import MagicMock, patch

from indexclient.client import Document, IndexClient


def test_reads_and_bulk_preserve_credentials():
    auth = MagicMock()
    client = IndexClient("https://commons.example/index", auth=auth)
    response = MagicMock(status_code=200)
    response.json.return_value = {
        "did": "private",
        "rev": "1",
        "visibility": "restricted",
    }
    with patch("indexclient.client.requests.get", return_value=response) as get:
        assert client.get("private").visibility == "restricted"
        assert get.call_args.kwargs["auth"] is auth
        client._get("index", auth=("override", "password"))
        assert get.call_args.kwargs["auth"] == ("override", "password")
    response.json.return_value = []
    with patch("indexclient.client.requests.post", return_value=response) as post:
        assert client.bulk_request(["private"]) == []
        assert post.call_args.kwargs["auth"] is auth


def test_visibility_can_be_added_to_legacy_document():
    client = IndexClient("https://commons.example/index", auth=("service", "password"))
    document = Document(
        client,
        "private",
        json={"did": "private", "rev": "1", "authz": ["/private"], "urls": []},
    )
    document.visibility = "restricted"
    assert document._doc_for_update()["visibility"] == "restricted"


def test_create_serializes_visibility():
    client = IndexClient("https://commons.example/index")
    response = MagicMock(status_code=200)
    response.json.return_value = {"did": "private", "rev": "1"}
    with patch.object(client, "_post", return_value=response) as post, patch.object(
        client, "_get", return_value=response
    ):
        client.create(
            hashes={"md5": "a" * 32},
            size=1,
            authz=["/private"],
            visibility="restricted",
        )
        assert json.loads(post.call_args.kwargs["data"])["visibility"] == "restricted"
