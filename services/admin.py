from repositories import users
from services import user as user_services
from services import registration
from helpers.password_hasher import create_new_hash

RECORDS_ON_PAGE = 5
DEFAULT_PASSWORD = '********'

async def get_users(page, name):
    page -= 1
    if page < 0:
        page = 0

    user_list = await users.get_users(RECORDS_ON_PAGE, page, name)

    for i in range(len(user_list)):
        user_list[i].password = DEFAULT_PASSWORD

    return user_list

async def activate_deactivate_user(user, is_active):
    return await users.activate_deactivate_user(user, is_active)

async def delete_user(user):
    return await user_services.delete_account(user)

async def create_user(new_user):
    return await registration.create_user(new_user, change_role=True)

async def update_user(user):
    update_password = False
    salt = ''

    if user.password != DEFAULT_PASSWORD:
        update_password = True
        password, salt = create_new_hash(user.password)
        user.password = password

    return await users.update_full_user(user, salt, update_password)