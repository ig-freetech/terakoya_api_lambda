import os
import sys
from decimal import Decimal
from typing import List
import requests
import json

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.domain import timeline
from functions.models.timeline import CommentItem, PostItem, Reaction
from functions.utils.dt import DT
from tests.utils.const import base_url, headers
from tests.samples.timeline import post_timeline_item_json, post_comment_item_json, put_reaction_json, TYPE_LIKE
from tests.samples.user import pytest_user_account_request_body_json, PYTEST_USER_UUID, PYTEST_USER_NAME


class TestFunc:
    def test_post_timeline_item(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post timeline item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None
        
        # Check whether the timeline item has been posted 
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item.get("post_id") == post_id

        # Clean up the test data
        # timeline.delete_timeline_item(post_id)

    def test_post_comment_item(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Post the comment to the test data
        comment_response = timeline.post_comment_item(
            post_id=post_id,
            comment=CommentItem(**{
                "post_id": post_id,
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"comment_response: {comment_response}")
        comment_id = comment_response.get("comment_id")
        assert comment_id is not None

        # Check whether the comment has been posted
        # Comment item
        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item is not None
        assert comment_item.get("comment_id") == comment_id
        # Timeline item
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        assert timeline_item.get("comment_count") == 1

        # Clean up the test data
        # timeline.delete_timeline_item(post_id)

    def test_put_reaction_to_timeline_item(self):
        """Post a reaction to a timeline item and update it"""

        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Put reaction to timeline item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Post the reaction to the test data
        timeline.put_reaction_to_timeline_item(
            post_id=post_id,
            reaction=Reaction(uuid=PYTEST_USER_UUID, type=1) # Like
        )

        # Check whether the reaction has been posted
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        reactions = timeline_item.get("reactions", [])
        assert len(reactions) == 1
        assert reactions[0].get("uuid") == PYTEST_USER_UUID
        assert reactions[0].get("type") == 1

        # Put the new reaction to the test data
        timeline.put_reaction_to_timeline_item(
            post_id=post_id,
            reaction=Reaction(uuid=PYTEST_USER_UUID, type=2) # Bad
        )

        # Check whether the reaction has been updated
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        reactions = timeline_item.get("reactions", [])
        assert len(reactions) == 1
        assert reactions[0].get("type") == 2

        # Clean up the test data
        # timeline.delete_timeline_item(post_id)

    def test_put_reaction_to_comment_item(self):
        """Post a reaction to a comment item and update it"""
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Put reaction to comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Post the comment to the test data
        comment_response = timeline.post_comment_item(
            post_id=post_id,
            comment=CommentItem(**{
                "post_id": post_id,
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Put reaction to comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"comment_response: {comment_response}")
        comment_id = comment_response.get("comment_id")
        assert comment_id is not None

        # Post the reaction to the test data
        timeline.put_reaction_to_comment_item(
            comment_id=comment_id,
            reaction=Reaction(uuid=PYTEST_USER_UUID, type=1) # Like
        )

        # Check whether the reaction has been posted
        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item is not None
        reactions = comment_item.get("reactions", [])
        assert len(reactions) == 1
        assert reactions[0].get("uuid") == PYTEST_USER_UUID
        assert reactions[0].get("type") == 1

        # Put the new reaction to the test data
        timeline.put_reaction_to_comment_item(
            comment_id=comment_id,
            reaction=Reaction(uuid=PYTEST_USER_UUID, type=2) # Bad
        )

        # Check whether the reaction has been updated
        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item is not None
        reactions = comment_item.get("reactions", [])
        assert len(reactions) == 1
        assert reactions[0].get("type") == 2

    def test_logical_delete_comment_item(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Post the comment to the test data
        comment_response = timeline.post_comment_item(
            post_id=post_id,
            comment=CommentItem(**{
                "post_id": post_id,
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post comment item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"comment_response: {comment_response}")
        comment_id = comment_response.get("comment_id")
        assert comment_id is not None

        # Check the comment count of the timeline item
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        assert timeline_item.get("comment_count") == 1

        timeline.delete_logical_comment_item(post_id=post_id, comment_id=comment_id)

        # Check whether the comment item is logically deleted
        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item is not None
        assert comment_item.get("comment_id") == comment_id
        assert comment_item.get("is_deleted") == Decimal(1)

        # Check whether the comment count of the timeline item is updated
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        assert timeline_item.get("comment_count") == 0

        # Clean up the test data
        # timeline.delete_timeline_item(post_id)

    def test_logical_delete_timeline_item(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Post timeline item\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        ) 
        print(f"post_response: {post_response}")

        response = timeline.fetch_timeline_list()
        print(f"response: {response}")
        
        assert response.get("items") is not None
        timeline_items: List = response.get("items", [])
        assert len(timeline_items) > 0 # At least one item is fetched

        target_timeline_item = timeline_items[0]
        post_id = target_timeline_item.get("post_id")

        timeline.delete_logical_timeline_item(post_id)

        # Check whether the timeline item is logically deleted
        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item is not None
        assert timeline_item.get("post_id") == post_id
        assert timeline_item.get("is_deleted") == Decimal(1)

        response = timeline.fetch_timeline_list()
        print(f"response: {response}")

        assert response.get("items") is not None
        timeline_items: List = response.get("items", [])
        if len(timeline_items) > 0: # At least one item is fetched
            post_ids = [timeline_item.get("post_id") for timeline_item in timeline_items]
            assert post_id not in post_ids

        # Clean up the test data
        # timeline.delete_timeline_item(post_id)


    def test_fetch_timeline_items(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Fetch timeline items\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Check whether the timeline item has been fetched
        response = timeline.fetch_timeline_list()
        print(f"response: {response}")
        assert response.get("items") is not None
        timeline_items: List = response.get("items", [])
        assert len(timeline_items) > 0 # At least one item is fetched

        # Check whether the last_post_id is returned if there are more than 20 items
        if len(timeline_items) == 20:
            last_post_id = response.get("last_evaluated_id")
            assert last_post_id is not None

            # Check whether the timeline item has been fetched with the last_post_id
            response = timeline.fetch_timeline_list(last_post_id=last_post_id)
            print(f"response: {response}")
            assert response.get("items") is not None
            timeline_items: List = response.get("items", [])
            assert len(timeline_items) > 0 # At least one item is fetched

            last_post_id = response.get("last_evaluated_id")
            if len(timeline_items) == 20:
                assert last_post_id is not None
            assert last_post_id is None

    def test_fetch_fetch_timeline_items_by_user(self):
        # Post the test data
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Fetch timeline items by user\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None

        # Check whether the timeline item has been fetched
        response = timeline.fetch_timeline_list_by_user(PYTEST_USER_UUID)
        print(f"response: {response}")
        assert response.get("items") is not None
        timeline_items: List = response.get("items", [])
        assert len(timeline_items) > 0

        # Check whether the last_post_id is returned if there are more than 20 items
        if len(timeline_items) == 20:
            last_post_id = response.get("last_evaluated_id")
            assert last_post_id is not None

            # Check whether the timeline item has been fetched with the last_post_id
            response = timeline.fetch_timeline_list_by_user(PYTEST_USER_UUID, last_post_id=last_post_id)
            print(f"response: {response}")
            assert response.get("items") is not None
            timeline_items: List = response.get("items", [])
            assert len(timeline_items) > 0

            last_post_id = response.get("last_evaluated_id")
            if len(timeline_items) == 20:
                assert last_post_id is not None
            assert last_post_id is None

    def test_fetch_comment_items(self):
        # Post the test data
        # post_response = timeline.post_timeline_item(
        #     post=PostItem(**{
        #         "uuid": PYTEST_USER_UUID,
        #         "user_name": PYTEST_USER_NAME,
        #         "texts": f"Fetch comment items\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
        #     })
        # )
        # print(f"post_response: {post_response}")
        # post_id = post_response.get("post_id")
        # assert post_id is not None

        # Post ID for testing
        post_id = "c15715affac84cc5afd0b85850c3ac5e"

        # Post the comment to the test data
        comment_response = timeline.post_comment_item(
            post_id=post_id,
            comment=CommentItem(**{
                "post_id": post_id,
                "uuid": PYTEST_USER_UUID,
                "user_name": PYTEST_USER_NAME,
                "texts": f"Fetch comment items\n{DT.CURRENT_JST_ISO_8601_DATETIME}",
            })
        )
        print(f"comment_response: {comment_response}")
        comment_id = comment_response.get("comment_id")
        assert comment_id is not None

        # Check whether the comment item has been fetched
        response = timeline.fetch_comment_list(post_id)
        print(f"response: {response}")
        assert response.get("items") is not None
        comment_items: List = response.get("items", [])
        assert len(comment_items) > 0

        # Check whether the last_comment_id is returned if there are more than 20 items
        if len(comment_items) == 20:
            last_comment_id = response.get("last_evaluated_id")
            assert last_comment_id is not None

            # Check whether the comment item has been fetched with the last_comment_id
            response = timeline.fetch_comment_list(post_id, last_comment_id=last_comment_id)
            print(f"response: {response}")
            assert response.get("items") is not None
            comment_items: List = response.get("items", [])
            assert len(comment_items) > 0

            last_comment_id = response.get("last_evaluated_id")
            if len(comment_items) == 20:
                assert last_comment_id is not None
            assert last_comment_id is None


class TestAPIGateway:
    def test_post_timeline_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", headers=headers, data=json.dumps(post_timeline_item_json)
        )
        assert response_post_timeline_item.status_code == 401

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        response_body_post_timeline_item = response_post_timeline_item.json()
        print(f"response_body_post_timeline_item: {response_body_post_timeline_item}")
        assert response_post_timeline_item.status_code == 200

        post_id = response_body_post_timeline_item.get("post_id")
        assert post_id is not None

        response_get_timeline_item = requests.get(f"{base_url}/timeline/{post_id}")
        response_body_get_timeline_item = response_get_timeline_item.json()
        print(f"response_body_get_timeline_item: {response_body_get_timeline_item}")
        assert response_get_timeline_item.status_code == 200
        assert response_body_get_timeline_item.get("post_id") == post_id

    def test_post_comment_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        response_body_post_timeline_item = response_post_timeline_item.json()
        assert response_post_timeline_item.status_code == 200

        post_id = response_body_post_timeline_item.get("post_id")
        assert post_id is not None

        response_post_comment_item = requests.post(
            f"{base_url}/timeline/{post_id}/comment", 
            headers=headers, 
            data=json.dumps(post_comment_item_json)
        )
        assert response_post_comment_item.status_code == 401

        response_post_comment_item = requests.post(
            f"{base_url}/timeline/{post_id}/comment", 
            headers=headers, 
            data=json.dumps({
                **post_comment_item_json,
                "post_id": post_id
            }),
            cookies=response_signin.cookies
        )
        response_body_post_comment_item = response_post_comment_item.json()
        print(f"response_body_post_comment_item: {response_body_post_comment_item}")
        assert response_post_comment_item.status_code == 200

        comment_id = response_body_post_comment_item.get("comment_id")
        assert comment_id is not None

        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item.get("comment_id") == comment_id

    def test_put_reaction_to_timeline_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        assert response_post_timeline_item.status_code == 200

        post_id = response_post_timeline_item.json().get("post_id")
        assert post_id is not None

        response_put_reaction_to_timeline_item = requests.put(
            f"{base_url}/timeline/{post_id}/reaction", 
            headers=headers, 
            data=json.dumps(put_reaction_json)
        )
        assert response_put_reaction_to_timeline_item.status_code == 401

        response_put_reaction_to_timeline_item = requests.put(
            f"{base_url}/timeline/{post_id}/reaction", 
            headers=headers, 
            data=json.dumps(put_reaction_json),
            cookies=response_signin.cookies
        )
        assert response_put_reaction_to_timeline_item.status_code == 200

        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item.get("reactions") is not None
        reactions: List = timeline_item.get("reactions", [])
        assert len(reactions) > 0
        assert reactions[0].get("uuid") == PYTEST_USER_UUID
        assert reactions[0].get("type") == TYPE_LIKE

    def test_put_reaction_to_comment_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        assert response_post_timeline_item.status_code == 200

        post_id = response_post_timeline_item.json().get("post_id")
        assert post_id is not None

        response_post_comment_item = requests.post(
            f"{base_url}/timeline/{post_id}/comment", 
            headers=headers, 
            data=json.dumps({
                **post_comment_item_json,
                "post_id": post_id
            }),
            cookies=response_signin.cookies
        )
        assert response_post_comment_item.status_code == 200

        comment_id = response_post_comment_item.json().get("comment_id")
        assert comment_id is not None

        response_put_reaction_to_comment_item = requests.put(
            f"{base_url}/timeline/comment/{comment_id}/reaction", 
            headers=headers, 
            data=json.dumps(put_reaction_json)
        )
        assert response_put_reaction_to_comment_item.status_code == 401

        response_put_reaction_to_comment_item = requests.put(
            f"{base_url}/timeline/comment/{comment_id}/reaction", 
            headers=headers, 
            data=json.dumps(put_reaction_json),
            cookies=response_signin.cookies
        )
        assert response_put_reaction_to_comment_item.status_code == 200

        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item.get("reactions") is not None
        reactions: List = comment_item.get("reactions", [])
        assert len(reactions) > 0
        assert reactions[0].get("uuid") == PYTEST_USER_UUID
        assert reactions[0].get("type") == TYPE_LIKE

    def test_fetch_timeline_list(self):
        # response_signin = requests.post(f"{base_url}/signin", headers=headers,
        #                                 data=json.dumps(pytest_user_account_request_body_json))
        # assert response_signin.status_code == 200

        # response_post_timeline_item = requests.post(
        #     f"{base_url}/timeline", 
        #     headers=headers, 
        #     data=json.dumps(post_timeline_item_json), 
        #     cookies=response_signin.cookies
        # )
        # assert response_post_timeline_item.status_code == 200

        response_fetch_timeline_list = requests.get(f"{base_url}/timeline/list", headers=headers)
        response_body_fetch_timeline_list = response_fetch_timeline_list.json()
        print(f"response_body_fetch_timeline_list: {response_body_fetch_timeline_list}")
        assert response_fetch_timeline_list.status_code == 200

        assert response_body_fetch_timeline_list.get("items") is not None
        timeline_items: List = response_body_fetch_timeline_list.get("items", [])
        assert len(timeline_items) > 0

    def test_fetch_timeline_list_by_user(self):
        # response_signin = requests.post(f"{base_url}/signin", headers=headers,
        #                                 data=json.dumps(pytest_user_account_request_body_json))
        # assert response_signin.status_code == 200

        # response_post_timeline_item = requests.post(
        #     f"{base_url}/timeline", 
        #     headers=headers, 
        #     data=json.dumps(post_timeline_item_json), 
        #     cookies=response_signin.cookies
        # )
        # assert response_post_timeline_item.status_code == 200

        response_fetch_timeline_list_by_user = requests.get(
            f"{base_url}/timeline/list?uuid={PYTEST_USER_UUID}", 
            headers=headers
        )
        response_body_fetch_timeline_list_by_user = response_fetch_timeline_list_by_user.json()
        print(f"response_body_fetch_timeline_list_by_user: {response_body_fetch_timeline_list_by_user}")
        assert response_fetch_timeline_list_by_user.status_code == 200

        assert response_body_fetch_timeline_list_by_user.get("items") is not None
        timeline_items: List = response_body_fetch_timeline_list_by_user.get("items", [])
        assert len(timeline_items) > 0

    def test_fetch_comment_list(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        assert response_post_timeline_item.status_code == 200

        post_id = response_post_timeline_item.json().get("post_id")
        assert post_id is not None

        response_post_comment_item = requests.post(
            f"{base_url}/timeline/{post_id}/comment",
            headers=headers,
            data=json.dumps({
                **post_comment_item_json,
                "post_id": post_id
            }),
            cookies=response_signin.cookies
        )
        assert response_post_comment_item.status_code == 200

        comment_id = response_post_comment_item.json().get("comment_id")
        assert comment_id is not None

        response_fetch_comment_list = requests.get(
            f"{base_url}/timeline/{post_id}/comment/list",
            headers=headers
        )
        response_body_fetch_comment_list = response_fetch_comment_list.json()
        print(f"response_body_fetch_comment_list: {response_body_fetch_comment_list}")
        assert response_fetch_comment_list.status_code == 200

        assert response_body_fetch_comment_list.get("items") is not None
        comment_items: List = response_body_fetch_comment_list.get("items", [])
        assert len(comment_items) > 0

    def test_delete_timeline_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        assert response_post_timeline_item.status_code == 200

        post_id = response_post_timeline_item.json().get("post_id")
        assert post_id is not None

        response_delete_timeline_item = requests.delete(
            f"{base_url}/timeline/{post_id}",
            headers=headers,
            cookies=response_signin.cookies
        )
        assert response_delete_timeline_item.status_code == 200

        timeline_item = timeline.fetch_timeline_item(post_id)
        print(f"timeline_item: {timeline_item}")
        assert timeline_item.get("is_deleted") == Decimal(1)

    def test_delete_comment_item(self):
        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(pytest_user_account_request_body_json))
        assert response_signin.status_code == 200

        response_post_timeline_item = requests.post(
            f"{base_url}/timeline", 
            headers=headers, 
            data=json.dumps(post_timeline_item_json), 
            cookies=response_signin.cookies
        )
        assert response_post_timeline_item.status_code == 200

        post_id = response_post_timeline_item.json().get("post_id")
        assert post_id is not None

        response_post_comment_item = requests.post(
            f"{base_url}/timeline/{post_id}/comment",
            headers=headers,
            data=json.dumps({
                **post_comment_item_json,
                "post_id": post_id
            }),
            cookies=response_signin.cookies
        )
        assert response_post_comment_item.status_code == 200

        comment_id = response_post_comment_item.json().get("comment_id")
        assert comment_id is not None

        response_delete_comment_item = requests.delete(
            f"{base_url}/timeline/{post_id}/comment/{comment_id}",
            headers=headers,
            cookies=response_signin.cookies
        )
        assert response_delete_comment_item.status_code == 200

        comment_item = timeline.fetch_comment_item(comment_id)
        print(f"comment_item: {comment_item}")
        assert comment_item.get("is_deleted") == Decimal(1)
