from sqlalchemy import select
import logging
from data.config import LOGING_LEVEL, ADMINS_ID

from database.models import *

'''Logging settings'''
logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGING_LEVEL)

ch = logging.StreamHandler()
ch.setLevel(LOGING_LEVEL)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(ch)


async def add_voice_actor(name, link):
    async with async_session() as session:
        try:
            result = await session.execute(select(Voice_actor).where(Voice_actor.name == name))
            actor = result.scalar()

            if actor:
                logging.warning(f"Voice Actor {name} already exists.")
                return False

            new_actor = Voice_actor(name=name, link=link)
            session.add(new_actor)
            await session.commit()
            logging.info(f"Added Voice Actor {name}")

            return True
        except Exception as e:
            logging.error(f"Error adding voice actor {name}: {e}")
            await session.rollback()
            raise


async def add_editor(name, link):
    async with async_session() as session:
        try:
            result = await session.execute(select(Editor).where(Editor.name == name))
            editor = result.scalar()

            if editor:
                logging.warning(f"Editor {name} already exists.")
                return False

            new_editor = Editor(name=name, link=link)
            session.add(new_editor)
            await session.commit()
            logging.info(f"Added Editor {name}")

            return True
        except Exception as e:
            logger.error(e)
            await session.rollback()
            raise



async def add_tag(name):
    async with async_session() as session:
        try:
            result = await session.execute(select(Tag).where(Tag.name == name))
            tag = result.scalar()
            if tag:
                logging.warning(f"Tag {name} already exists.")
                return False

            new_tag = Tag(name=name)
            session.add(new_tag)
            await session.commit()
            logging.info(f"Added Tag {name}")

            return True
        except Exception as e:
            logger.error(f"Error adding tag '{name}': {e}")
            await session.rollback()
            raise



async def add_user(tg_id, tg_username):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.id == tg_id))
            user = result.scalar()
            if user is None:
                user = User(tg_id=tg_id, tg_username=tg_username, role="User")
                session.add(user)
                await session.commit()
                logger.info(f"Added User: {tg_username} (ID: {tg_id}, Role: User)")
            else:
                logger.info(f"User {tg_username} already exists")
        except Exception as e:
            logger.error(f"Error adding user '{tg_username}': {e}")



async def add_moderator(tg_id):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).filter(User.tg_id == tg_id))
            user = result.scalar_one_or_none()  # Получаем единственного пользователя или None

            if not user:
                logger.warning(f"User with tg_id {tg_id} not found.")
                return False

            if user.role == "Moderator":
                logger.info(f"User with tg_id {tg_id} is already a moderator.")
                return False

            user.role = "Moderator"
            await session.commit()

            logger.info(f"User with tg_id {tg_id} promoted to moderator.")
            return True

        except Exception as e:
            logger.error(f"Error promoting user to moderator with tg_id: {tg_id}: {e}")
            return False


async def add_admin(tg_id: int):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalar()

            if user:
                if user.role != 'Admin':
                    user.role = 'Admin'
                    await session.commit()
                    logger.info(f"User with tg_id {tg_id} successfully promoted to admin.")
                    return True
                else:
                    logger.warning(f"User with tg_id {tg_id} is already an admin.")
                    return False
            else:
                logger.warning(f"User with tg_id {tg_id} not found.")
                return False

        except Exception as e:
            logger.error(f"Error promoting user to admin with tg_id: {tg_id}: {e}")
            return False


async def get_voice_actor_by_name(name):
    try:
        async with async_session() as session:
            result = await session.execute(select(Voice_actor).where(Voice_actor.name == name))
            user = result.scalar()

            if user:
                return user
            else:
                return None
    except Exception as e:
        logger.error(f"Error getting voice actor: {name}: {e}")
        return None


async def get_editor_by_name(name):
    try:
        async with async_session() as session:
            result = await session.execute(select(Editor).where(Editor.name == name))
            editor = result.scalar()

            if editor:
                return editor
            else:
                return None
    except Exception as e:
        logger.error(f"Error getting editor: {name}: {e}")
        return None



async def delete_moderator_by_id(id):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.id == id))
            user = result.scalar()

            if user and user.role == 'Moderator':
                user.role = 'User'
                await session.commit()
                logger.info(f"User with id {id} demoted from moderator.")
            else:
                logger.warning(f"User with id {id} is not a moderator or not found.")
        except Exception as e:
            logger.error(f"Error demoting moderator with id: {id}: {e}")



async def delete_admin_by_id(id):
    async with async_session() as session:
        try:
            result = await session.execute(select(User).where(User.id == id))
            user = result.scalar()

            if user and user.role == 'Admin':
                user.role = 'User'
                await session.commit()
                logger.info(f"User with id {id} demoted from admin.")
            else:
                logger.warning(f"User with id {id} is not an admin or not found.")
        except Exception as e:
            logger.error(f"Error demoting admin id: {id}: {e}")



async def delete_tag_by_id(id):
    async with async_session() as session:
        try:
            result = await session.execute(select(Tag).where(Tag.id == id))
            tag = result.scalar()

            if tag:
                await session.delete(tag)
                await session.commit()
                logger.info(f"Deleted Tag with id: {id}")
            else:
                logger.warning(f"Tag with id: '{id}' not found.")
        except Exception as e:
            logger.error(f"Error deleting tag with id: '{id}': {e}")



async def delete_voice_actor_by_name(name):
    async with async_session() as session:
        try:
            result = await session.execute(select(Voice_actor).where(Voice_actor.name == name))
            actor = result.scalar()

            if actor:
                await session.delete(actor)
                await session.commit()
                logger.info(f"Deleted Voice Actor: {name}")
            else:
                logger.warning(f"Voice Actor '{name}' not found.")
        except Exception as e:
            logger.error(f"Error deleting voice actor '{name}': {e}")


async def delete_voice_actor_by_id(id):
    async with async_session() as session:
        try:
            result = await session.execute(select(Voice_actor).where(Voice_actor.id == id))
            actor = result.scalar()

            if actor:
                await session.delete(actor)
                await session.commit()
                logger.info(f"Deleted Voice Actor with id: {id}")
            else:
                logger.warning(f"Voice Actor with id: {id} not found.")
        except Exception as e:
            logger.error(f"Error deleting voice actor by id: '{id}': {e}")


async def delete_editor_by_id(id):
    async with async_session() as session:
        try:
            result = await session.execute(select(Editor).where(Editor.id == id))
            editor = result.scalar()

            if editor:
                await session.delete(editor)
                await session.commit()
                logger.info(f"Deleted editor with id: {id}")
            else:
                logger.warning(f"Editor with id: '{id}' not found.")
        except Exception as e:
            logger.error(f"Error deleting editor with id: '{id}': {e}")


async def get_all_voice_actors():
    try:
        async with async_session() as session:
            result = await session.execute(select(Voice_actor))
            return result.scalars().all()

    except Exception as e:
        logger.error(e)



async def get_all_editors():
    try:
        async with async_session() as session:
            result = await session.execute(select(Editor))
            return result.scalars().all()

    except Exception as e:
        logger.error(e)



async def get_all_tags():
    try:
        async with async_session() as session:
            result = await session.execute(select(Tag))
            tags = result.scalars().all()
            return tags

    except Exception as e:
        logger.error(e)


async def get_all_moderators():
    try:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.role == "Moderator"))
            moderators = result.scalars().all()
            return moderators

    except Exception as e:
        logger.error(e)


async def get_all_admins():
    try:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.role == "Admin"))
            admins = result.scalars().all()

            if not admins:
                return []

            return admins

    except Exception as e:
        logger.error(e)


async def is_admin(tg_id):
    try:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalar()

            if user or (tg_id in ADMINS_ID):
                if user.role == 'Admin' or (user.tg_id in ADMINS_ID):
                    return True
                else:
                    return False
            else:
                logger.warning(f"User with ID {tg_id} not found.")
                return False

    except Exception as e:
        logger.error(e)


async def is_moderator(tg_id):
    try:
        async with async_session() as session:
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalar()
            if user:
                if user.role == 'Moderator':
                    return True
                else:
                    return False
            else:
                logger.warning(f"User with ID {tg_id} not found.")
                return False

    except Exception as e:
        logger.error(e)




