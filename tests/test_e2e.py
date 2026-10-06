import pytest

# полный жизненный цикл пользователя
@pytest.mark.asyncio
async def test_user_full_lifecycle(client):
    create_payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000101",
        "age": 25,
    }

    # создать пользователя
    create_response = await client.post(
        "/api/users",
        json=create_payload,
    )

    assert create_response.status == 201

    create_data = await create_response.json()

    assert create_data["status"] == "ok"
    assert "id" in create_data["data"]
    assert create_data["data"]["name"] == "Ivan"
    assert create_data["data"]["surname"] == "Ivanov"
    assert create_data["data"]["phone"] == "+79000000101"
    assert create_data["data"]["age"] == 25

    user_id = create_data["data"]["id"]

    # получить пользователя по id
    get_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_response.status == 200

    get_data = await get_response.json()

    assert get_data["status"] == "ok"
    assert get_data["data"]["id"] == user_id
    assert get_data["data"]["name"] == "Ivan"
    assert get_data["data"]["surname"] == "Ivanov"
    assert get_data["data"]["phone"] == "+79000000101"
    assert get_data["data"]["age"] == 25

    # изменить имя пользователя
    update_payload = {
        "name": "Petr",
    }

    update_response = await client.patch(
        f"/api/users/{user_id}",
        json=update_payload,
    )

    assert update_response.status == 200

    update_data = await update_response.json()

    assert update_data["status"] == "ok"
    assert update_data["data"]["id"] == user_id
    assert update_data["data"]["name"] == "Petr"
    assert update_data["data"]["surname"] == "Ivanov"
    assert update_data["data"]["phone"] == "+79000000101"
    assert update_data["data"]["age"] == 25

    # получить пользователя повторно и проверить, что изменённое имя сохранилось
    get_updated_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_updated_response.status == 200

    get_updated_data = await get_updated_response.json()

    assert get_updated_data["status"] == "ok"
    assert get_updated_data["data"]["id"] == user_id
    assert get_updated_data["data"]["name"] == "Petr"
    assert get_updated_data["data"]["surname"] == "Ivanov"
    assert get_updated_data["data"]["phone"] == "+79000000101"
    assert get_updated_data["data"]["age"] == 25

    # удалить пользователя
    delete_response = await client.delete(
        f"/api/users/{user_id}"
    )

    assert delete_response.status == 200

    delete_data = await delete_response.json()

    assert delete_data["deleted_id"] == user_id

    # проверить, что пользователь больше не найден
    get_deleted_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_deleted_response.status == 404

    get_deleted_data = await get_deleted_response.json()

    assert get_deleted_data["status"] == "fail"
    assert get_deleted_data["reason"] == "User not found"


# создание двух пользователей и проверка списка
@pytest.mark.asyncio
async def test_create_two_users_and_get_list(client):
    first_payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000102",
        "age": 25,
    }

    second_payload = {
        "name": "Anna",
        "surname": "Petrova",
        "phone": "+79000000103",
        "age": 30,
    }

    # создать первого пользователя
    first_response = await client.post(
        "/api/users",
        json=first_payload,
    )

    assert first_response.status == 201

    first_data = await first_response.json()

    assert first_data["status"] == "ok"
    assert "id" in first_data["data"]
    assert first_data["data"]["name"] == "Ivan"
    assert first_data["data"]["surname"] == "Ivanov"
    assert first_data["data"]["phone"] == "+79000000102"
    assert first_data["data"]["age"] == 25

    first_id = first_data["data"]["id"]

    # создать второго пользователя
    second_response = await client.post(
        "/api/users",
        json=second_payload,
    )

    assert second_response.status == 201

    second_data = await second_response.json()

    assert second_data["status"] == "ok"
    assert "id" in second_data["data"]
    assert second_data["data"]["name"] == "Anna"
    assert second_data["data"]["surname"] == "Petrova"
    assert second_data["data"]["phone"] == "+79000000103"
    assert second_data["data"]["age"] == 30

    second_id = second_data["data"]["id"]

    # получить список пользователей
    list_response = await client.get("/api/users")

    assert list_response.status == 200

    list_data = await list_response.json()

    assert list_data["status"] == "ok"
    assert isinstance(list_data["data"], list)

    users = list_data["data"]

    # найти первого и второго пользователя в списке
    first_user_in_list = None
    second_user_in_list = None

    for user in users:
        if user["id"] == first_id:
            first_user_in_list = user

        if user["id"] == second_id:
            second_user_in_list = user

    # проверить, что оба пользователя найдены
    assert first_user_in_list is not None
    assert second_user_in_list is not None

    # проверить данные первого пользователя в списке
    assert first_user_in_list["id"] == first_id
    assert first_user_in_list["name"] == "Ivan"
    assert first_user_in_list["surname"] == "Ivanov"
    assert first_user_in_list["phone"] == "+79000000102"
    assert first_user_in_list["age"] == 25

    # проверить данные второго пользователя в списке
    assert second_user_in_list["id"] == second_id
    assert second_user_in_list["name"] == "Anna"
    assert second_user_in_list["surname"] == "Petrova"
    assert second_user_in_list["phone"] == "+79000000103"
    assert second_user_in_list["age"] == 30

    # удалить первого пользователя
    delete_first_response = await client.delete(
        f"/api/users/{first_id}"
    )

    assert delete_first_response.status == 200

    delete_first_data = await delete_first_response.json()

    assert delete_first_data["deleted_id"] == first_id

    # удалить второго пользователя
    delete_second_response = await client.delete(
        f"/api/users/{second_id}"
    )

    assert delete_second_response.status == 200

    delete_second_data = await delete_second_response.json()

    assert delete_second_data["deleted_id"] == second_id

    # проверить, что первый пользователь удалён
    get_first_deleted_response = await client.get(
        f"/api/users/{first_id}"
    )

    assert get_first_deleted_response.status == 404

    get_first_deleted_data = await get_first_deleted_response.json()

    assert get_first_deleted_data["status"] == "fail"
    assert get_first_deleted_data["reason"] == "User not found"

    # проверить, что второй пользователь удалён
    get_second_deleted_response = await client.get(
        f"/api/users/{second_id}"
    )

    assert get_second_deleted_response.status == 404

    get_second_deleted_data = await get_second_deleted_response.json()

    assert get_second_deleted_data["status"] == "fail"
    assert get_second_deleted_data["reason"] == "User not found"


# создание, получение и удаление пользователя с граничными значениями возраста
@pytest.mark.parametrize(
    "age",
    [0, 120],
)
@pytest.mark.asyncio
async def test_user_lifecycle_with_boundary_age(client, age):
    phone = f"+790000001{age:02d}"

    payload = {
        "name": "Boundary",
        "surname": "User",
        "phone": phone,
        "age": age,
    }

    # создать пользователя
    create_response = await client.post(
        "/api/users",
        json=payload,
    )

    assert create_response.status == 201

    create_data = await create_response.json()

    assert create_data["status"] == "ok"
    assert "id" in create_data["data"]
    assert create_data["data"]["name"] == "Boundary"
    assert create_data["data"]["surname"] == "User"
    assert create_data["data"]["phone"] == phone
    assert create_data["data"]["age"] == age

    user_id = create_data["data"]["id"]

    # получить пользователя по id
    get_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_response.status == 200

    get_data = await get_response.json()

    assert get_data["status"] == "ok"
    assert get_data["data"]["id"] == user_id
    assert get_data["data"]["name"] == "Boundary"
    assert get_data["data"]["surname"] == "User"
    assert get_data["data"]["phone"] == phone
    assert get_data["data"]["age"] == age

    # удалить пользователя
    delete_response = await client.delete(
        f"/api/users/{user_id}"
    )

    assert delete_response.status == 200

    delete_data = await delete_response.json()

    assert delete_data["deleted_id"] == user_id

    # проверить, что пользователь удалён
    get_deleted_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_deleted_response.status == 404

    get_deleted_data = await get_deleted_response.json()

    assert get_deleted_data["status"] == "fail"
    assert get_deleted_data["reason"] == "User not found"

# негативные сценарии

# пользователь с дублирующимся телефоном не создаётся, а данные первого пользователя не меняются
@pytest.mark.asyncio
async def test_duplicate_phone_does_not_change_existing_user(client):
    first_payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000104",
        "age": 25,
    }

    duplicate_payload = {
        "name": "Petr",
        "surname": "Petrov",
        "phone": "+79000000104",
        "age": 30,
    }

    # создать первого пользователя
    first_response = await client.post(
        "/api/users",
        json=first_payload,
    )

    assert first_response.status == 201

    first_data = await first_response.json()

    assert first_data["status"] == "ok"
    assert "id" in first_data["data"]
    assert first_data["data"]["name"] == "Ivan"
    assert first_data["data"]["surname"] == "Ivanov"
    assert first_data["data"]["phone"] == "+79000000104"
    assert first_data["data"]["age"] == 25

    first_id = first_data["data"]["id"]

    # попытаться создать второго пользователя с таким же номером телефона
    duplicate_response = await client.post(
        "/api/users",
        json=duplicate_payload,
    )

    assert duplicate_response.status == 409

    duplicate_data = await duplicate_response.json()

    assert duplicate_data["status"] == "fail"
    assert duplicate_data["reason"] == "Phone already exists"

    # получить первого пользователя и убедиться, что его данные не изменились
    get_response = await client.get(
        f"/api/users/{first_id}"
    )

    assert get_response.status == 200

    get_data = await get_response.json()

    assert get_data["status"] == "ok"
    assert get_data["data"]["id"] == first_id
    assert get_data["data"]["name"] == "Ivan"
    assert get_data["data"]["surname"] == "Ivanov"
    assert get_data["data"]["phone"] == "+79000000104"
    assert get_data["data"]["age"] == 25

    # удалить первого пользователя
    delete_response = await client.delete(
        f"/api/users/{first_id}"
    )

    assert delete_response.status == 200

    delete_data = await delete_response.json()

    assert delete_data["deleted_id"] == first_id

    # проверить, что первый пользователь удалён
    get_deleted_response = await client.get(
        f"/api/users/{first_id}"
    )

    assert get_deleted_response.status == 404

    get_deleted_data = await get_deleted_response.json()

    assert get_deleted_data["status"] == "fail"
    assert get_deleted_data["reason"] == "User not found"


# пользователь без обязательного поля age не создаётся
@pytest.mark.asyncio
async def test_user_without_age_is_not_created(client):
    payload_without_age = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000105",
    }

    # попытаться создать пользователя без поля age
    create_response = await client.post(
        "/api/users",
        json=payload_without_age,
    )

    assert create_response.status == 400

    create_data = await create_response.json()

    assert create_data["status"] == "fail"
    assert "Missing field" in create_data["reason"]

    # получить список пользователей
    list_response = await client.get("/api/users")

    assert list_response.status == 200

    list_data = await list_response.json()

    assert list_data["status"] == "ok"
    assert isinstance(list_data["data"], list)

    users = list_data["data"]

    # проверить, что пользователь с таким телефоном не создан
    user_with_phone = None

    for user in users:
        if user["phone"] == "+79000000105":
            user_with_phone = user

    assert user_with_phone is None


# после удаления пользователь недоступен
@pytest.mark.asyncio
async def test_deleted_user_cannot_be_read_updated_or_deleted_again(client):
    payload = {
        "name": "Ivan",
        "surname": "Ivanov",
        "phone": "+79000000106",
        "age": 25,
    }

    # создать пользователя
    create_response = await client.post(
        "/api/users",
        json=payload,
    )

    assert create_response.status == 201

    create_data = await create_response.json()

    assert create_data["status"] == "ok"
    assert "id" in create_data["data"]
    assert create_data["data"]["name"] == "Ivan"
    assert create_data["data"]["surname"] == "Ivanov"
    assert create_data["data"]["phone"] == "+79000000106"
    assert create_data["data"]["age"] == 25

    user_id = create_data["data"]["id"]

    # удалить пользователя
    delete_response = await client.delete(
        f"/api/users/{user_id}"
    )

    assert delete_response.status == 200

    delete_data = await delete_response.json()

    assert delete_data["deleted_id"] == user_id

    # попытаться получить удалённого пользователя
    get_response = await client.get(
        f"/api/users/{user_id}"
    )

    assert get_response.status == 404

    get_data = await get_response.json()

    assert get_data["status"] == "fail"
    assert get_data["reason"] == "User not found"

    # попытаться изменить удалённого пользователя
    update_response = await client.patch(
        f"/api/users/{user_id}",
        json={"name": "Petr"},
    )

    assert update_response.status == 404

    update_data = await update_response.json()

    assert update_data["status"] == "fail"
    assert update_data["reason"] == "User not found"

    # попытаться удалить пользователя повторно
    second_delete_response = await client.delete(
        f"/api/users/{user_id}"
    )

    assert second_delete_response.status == 404

    second_delete_data = await second_delete_response.json()

    assert second_delete_data["status"] == "fail"
    assert second_delete_data["reason"] == "User not found"