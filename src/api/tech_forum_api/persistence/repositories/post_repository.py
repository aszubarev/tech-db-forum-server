import logging
from typing import Optional, List

from injector import inject
from sqlutils import DataContext, Repository, create_one, create_many, NoDataFoundError

from tech_forum_api.persistence.dto.post_dto import PostDTO


class PostRepository(Repository[PostDTO]):

    @inject
    def __init__(self, context: DataContext) -> None:
        self._context = context

    def get_by_id(self, uid: int) -> Optional[PostDTO]:
        data = self._context.callproc('get_post_by_id', [uid])
        return create_one(PostDTO, data)

    def get_posts_for_thread(self, thread_id: int, **kwargs) -> List[PostDTO]:
        sort = kwargs.get('sort')
        limit = kwargs.get('limit')
        since = kwargs.get('since')
        desc = kwargs.get('desc')

        data = None

        # FLAT SORT
        if sort == 'flat':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_limit_desc', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_flat_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat_all', [thread_id])

        # TREE SORT
        elif sort == 'tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_limit_desc', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_three_since_limit', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_all', [thread_id])

        # PARENT_TREE SORT
        elif sort == 'parent_tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_limit_desc', [thread_id, limit, desc])

            elif limit is not None and since is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit', [thread_id, since, limit])

            elif limit is not None and since is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_since_limit_desc',
                                              [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_desc', [thread_id, desc])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_parent_tree_all', [thread_id])

        elif sort is None:
            if since is None and limit is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_limit', [thread_id, limit])

            elif since is None and limit is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_limit_desc', [thread_id, desc, limit])

            elif since is not None and limit is not None and desc is None:
                data = self._context.callproc('get_posts_for_thread_since_limit', [thread_id, since, limit])

            elif since is not None and limit is not None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_since_limit_desc', [thread_id, since, limit, desc])

            elif limit is None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_desc', [thread_id, desc])

            elif since is None and limit is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_all', [thread_id])

        return create_many(PostDTO, data)

    def get_number_posts_for_forum(self, forum_id: int) -> int:
        data = self._context.callproc('get_number_posts_for_forum', [forum_id])
        if data is None or len(data) == 0:
            return 0
        result_dict = data[0]
        return result_dict.get('number_posts')

    def get_all(self) -> List[PostDTO]:
        raise NotImplementedError

    def add(self, entity: PostDTO) -> Optional[PostDTO]:
        data = self._context.callproc('add_post', [entity.thread_id, entity.forum_id, entity.user_id,
                                                   entity.parent_id, entity.message, entity.created, False])
        entity = create_one(PostDTO, data)
        if entity.parent_id == 0:
            path = [entity.uid]
            self._update_path(uid=entity.uid, path=path)
            entity.path = path

        else:
            parent = self.get_by_id(entity.parent_id)
            if not parent:
                raise NoDataFoundError(f"Can't find parent by parent_id = {entity.parent_id}")

            path = parent.path
            path.append(entity.uid)
            self._update_path(uid=entity.uid, path=path)
            entity.path = path

        return entity

    def update(self, entity: PostDTO):
        raise NotImplementedError

    def delete(self, uid: int) -> None:
        raise NotImplementedError

    def _get_parent_posts_for_thread(self, thread_id, desc=None, limit=None, since=None) -> List[PostDTO]:

        data = None

        if desc is None and limit is not None and since is None:
            data = self._context.callproc('get_posts_for_thread_limit', [thread_id, limit])

        elif desc is not None and limit is not None and since is None:
            data = self._context.callproc('get_posts_for_thread_desc_limit', [thread_id, desc, limit])

        elif desc is None and limit is not None and since is not None:
            data = self._context.callproc('get_posts_for_thread_limit_since', [thread_id, limit, since])

        return create_many(PostDTO, data)

    def _get_posts_for_thread_limit(self, thread_id, limit: int) -> List[PostDTO]:
        # parents = self._get_parent_posts_for_thread(thread_id=thread_id, desc=None, limit=limit, since=None)
        data = self._context.callproc('get_posts_for_thread_limit', [thread_id, limit])
        parents = create_many(PostDTO, data)

        entities = []
        for parent in parents:

            data.clear()
            data = self._context.callproc('get_post_by_parent_id', [parent.uid])
            children = create_many(PostDTO, data)

            logging.info(f"===================================================================================")
            logging.info(f"[PostRepository] parent: uid = {parent.uid}; parent_id = {parent.parent_id}")
            logging.info(f"[PostRepository] numb children = {len(children)}")

            if len(children) == 0:
                continue

            entities.append(parent)
            for child in children:
                logging.info(f"[PostRepository] child: uid = {child.uid}; parent_id = {child.parent_id}")
                entities.append(child)

        logging.info(f"===================================================================================")
        logging.info(f"numb entities = {len(entities)}")

        return entities

    def _get_posts_for_thread_desc_limit(self, thread_id: int, desc: bool, limit: int) -> List[PostDTO]:

        if desc == 'false':
            return self._get_posts_for_thread_limit(thread_id=thread_id, limit=limit)

        else:
            data = self._context.callproc('get_posts_for_thread_desc_limit', [thread_id, desc, limit])
            parents = create_many(PostDTO, data)
            entities = []

            for parent in parents:

                data.clear()
                data = self._context.callproc('get_post_by_parent_id', [parent.uid])
                children = create_many(PostDTO, data)
                if len(children) == 0:
                    continue

                for child in reversed(children):
                    entities.append(child)

                entities.append(parent)

            return entities

    def _get_posts_for_thread_parent_tree_limit_since(self, thread_id: int, limit: int, since: int):
        # parents = self._get_parent_posts_for_thread(thread_id=thread_id, desc=None, limit=limit, since=since)
        data = self._context.callproc('get_posts_for_thread_limit_since', [thread_id, limit, since])
        parents = create_many(PostDTO, data)
        entities = []
        data = None
        for parent in parents:

            data.clear()
            data = self._context.callproc('get_post_by_parent_id', [parent.uid])
            children = create_many(PostDTO, data)
            if len(children) == 0:
                continue

            entities.append(parent)
            for child in children:
                entities.append(child)

        return entities

    def _update_path(self, uid: int, path: List[int]):
        self._context.callproc('update_post_path_by_id', [uid, path])
