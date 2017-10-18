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
                data = self._context.callproc('get_post_for_thread_flat_desc_limit', [thread_id, desc, limit])

            elif limit is None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_flat', [thread_id])

        # TREE SORT
        elif sort == 'tree':
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_tree_limit', [thread_id, limit])

            elif limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_tree_desc_limit', [thread_id, desc, limit])

            # elif limit is None and since is None and desc is None:
            #     data = self._context.callproc('get_posts_for_thread_flat', [thread_id])

        # PARENT_TREE SORT
        elif sort == 'parent_tree':
            if limit is not None and since is None and desc is None:
                return self._get_posts_for_thread_limit(thread_id=thread_id, limit=limit)

            if limit is not None and since is None and desc is not None:
                return self._get_posts_for_thread_desc_limit(thread_id=thread_id, desc=desc, limit=limit)

            # elif limit is None and since is None and desc is None:
            #     data = self._context.callproc('get_posts_for_thread_flat', [thread_id])

        elif sort is None:
            if limit is not None and since is None and desc is None:
                data = self._context.callproc('get_posts_for_thread_limit', [thread_id, limit])

            if limit is not None and since is None and desc is not None:
                data = self._context.callproc('get_posts_for_thread_desc_limit', [thread_id, desc, limit])

        return create_many(PostDTO, data)

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

    def _get_posts_for_thread_limit(self, thread_id, limit: int) -> List[PostDTO]:
        data = self._context.callproc('get_posts_for_thread_limit', [thread_id, limit])
        parents = create_many(PostDTO, data)
        entities = []

        for parent in parents:

            data.clear()
            data = self._context.callproc('get_post_by_parent_id', [parent.uid])
            children = create_many(PostDTO, data)
            if len(children) == 0:
                continue

            logging.info(f"===================================================================================")
            logging.info(f"[PostRepository] parent: uid = {parent.uid}; parent_id = {parent.parent_id}")
            logging.info(f"[PostRepository] numb children = {len(children)}")
            entities.append(parent)
            for child in children:
                logging.info(f"[PostRepository] child: uid = {child.uid}; parent_id = {child.parent_id}")
                entities.append(child)

        logging.info(f"===================================================================================")
        logging.info(f"numb parents = {len(parents)}; numb entities = {len(entities)}")

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

                logging.info(f"===================================================================================")
                logging.info(f"[PostRepository] parent: uid = {parent.uid}; parent_id = {parent.parent_id}")
                logging.info(f"[PostRepository] numb children = {len(children)}")

                for child in reversed(children):
                    logging.info(f"[PostRepository] child: uid = {child.uid}; parent_id = {child.parent_id}")
                    entities.append(child)

                entities.append(parent)

            logging.info(f"===================================================================================")
            logging.info(f"numb parents = {len(parents)}; numb entities = {len(entities)}")

            return entities

    def _update_path(self, uid: int, path: List[int]):
        self._context.callproc('update_post_path_by_id', [uid, path])
