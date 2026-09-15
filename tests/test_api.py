import pytest

# ========================================================

# проверка что сервер доступен
@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")

    assert response.status == 200

    data = await response.json()

    assert data["status"] == "ok"

# проверка подключения к базе
@pytest.mark.asyncio
async def test_db_check(client):
    response = await client.get("/db-check")

    assert response.status == 200

    data = await response.json()

    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert data["check_value"] == 1

# ========================================================
# позитивные тесты

# создать успешно пользователя с параметризацией возраста
@pytest.mark.parametrize(
    "age",
    [0, 1, 50, 119, 120],
)
@pytest.mark.asyncio
async def test_create_user_with_valid_age(client, age):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000011",
        "age": age,
    }

    response = await client.post("/api/users", json=payload)

    assert response.status == 201

    data = await response.json()

    assert data["status"] == "ok"
    assert data["data"]["name"] == "Ivan"
    assert data["data"]["surname"] == "Ivanov"
    assert data["data"]["phone"] == "+79000000011"
    assert data["data"]["age"] == age
    assert "id" in data["data"]

# найти пользователя по id
@pytest.mark.asyncio
async def test_get_user(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000014",
        "age": 25,
    }

    create_response = await client.post("/api/users", json=payload)

    assert create_response.status == 201

    created_data = await create_response.json()
    user_id = created_data["data"]["id"]

    get_response = await client.get(f"/api/users/{user_id}")

    assert get_response.status == 200

    data = await get_response.json()

    assert data["data"]["id"] == user_id
    assert data["data"]["name"] == "Ivan"
    assert data["data"]["surname"] == "Ivanov"

# получить список пользователей
@pytest.mark.asyncio
async def test_list_users(client):
    response = await client.get("/api/users")

    assert response.status == 200

    data = await response.json()

    assert data["status"] == "ok"
    assert isinstance(data["data"], list)

# обновление данных пользователя
@pytest.mark.asyncio
async def test_update_user(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000015",
        "age": 25,
    }

    create_response = await client.post("/api/users", json=payload)

    assert create_response.status == 201

    created_data = await create_response.json()
    user_id = created_data["data"]["id"]

    update_payload = {
        "name": "Petr",
    }

    update_response = await client.patch(f"/api/users/{user_id}", json=update_payload)

    assert update_response.status == 200

    updated_data = await update_response.json()

    assert updated_data["data"]["name"] == "Petr"
    assert updated_data["data"]["surname"] == "Ivanov"
    assert updated_data["data"]["phone"] == "+79000000015"
    assert updated_data["data"]["age"] == 25

# удаление пользователя
@pytest.mark.asyncio
async def test_delete_user(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000016",
        "age": 25,
    }

    create_response = await client.post("/api/users", json=payload)

    assert create_response.status == 201

    created_data = await create_response.json()
    user_id = created_data["data"]["id"]

    delete_response = await client.delete(f"/api/users/{user_id}")

    assert delete_response.status == 200

    delete_data = await delete_response.json()

    assert delete_data["deleted_id"] == user_id

    get_response = await client.get(f"/api/users/{user_id}")

    assert get_response.status == 404

# ========================================================
# деструктивные тесты

# пользователь не найден
@pytest.mark.asyncio
async def test_get_user_not_found(client):
    response = await client.get("/api/users/999999")

    assert response.status == 404

    data = await response.json()

    assert data["reason"] == "User not found"

# создать пользователя с пропущеным обязательным полем
@pytest.mark.asyncio
async def test_create_user_missing_field(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000012",
    }

    response = await client.post("/api/users", json=payload)

    assert response.status == 400

    data = await response.json()

    assert "Missing field" in data["reason"]

# создать пользователя с повторябщимся номером телефона
@pytest.mark.asyncio
async def test_create_user_duplicate_phone(client):
    first_payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000013",
        "age": 25,
    }

    first_response = await client.post("/api/users", json=first_payload)

    assert first_response.status == 201

    second_payload = {
        "name": "Petr",
        "surname": "Petrov",
        "phone": "+79000000013",
        "age": 30,
    }

    second_response = await client.post("/api/users", json=second_payload)

    assert second_response.status == 409

    data = await second_response.json()

    assert data["reason"] == "Phone already exists"

# создать пользователя с текстовым значением возраста
@pytest.mark.asyncio
async def test_create_user_with_string_age(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000017",
        "age": "25",
    }

    response = await client.post("/api/users", json=payload)

    assert response.status == 400

    data = await response.json()

    assert data["reason"] == "age must be an integer"

# создать пользователя с неверным возрастом
@pytest.mark.asyncio
async def test_create_user_with_invalid_age(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000018",
        "age": 121,
    }

    response = await client.post("/api/users", json=payload)

    assert response.status == 400

    data = await response.json()

    assert data["reason"] == "age must be between 0 and 120"