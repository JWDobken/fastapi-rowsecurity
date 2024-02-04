def test_read_items(client):
    # User can select all items
    headers = {"Authorization": "Bearer user1"}
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_post_user1_items(client):
    # user 1 can post an item
    headers = {"Authorization": "Bearer user1"}
    title = "hbshsfbhfbhgjfb"
    response = client.post("/items", json={"title": title}, headers=headers)
    assert response.status_code == 200


def test_get_user1_items(client):
    # user 1 can GET all items
    headers = {"Authorization": "Bearer user1"}
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user2_items(client):
    # user 2 can GET all items
    headers = {"Authorization": "Bearer user2"}
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_user2_items(client):
    # user 2 cannot UPDATE items owned by user 1
    headers = {"Authorization": "Bearer user2"}
    title = "hbshsfbhfbhgjfb"
    response = client.post("/items/1", json={"title": title}, headers=headers)
    assert response.status_code == 200


def test_delete_user2_items(client):
    # user 2 cannot DELETE items owned by user 1
    headers = {"Authorization": "Bearer user2"}
    response = client.delete("/items/1", headers=headers)
    assert response.status_code == 200
