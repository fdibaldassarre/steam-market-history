#!/usr/bin/env python3

from sqlalchemy.orm import exc
from sqlalchemy.sql.expression import func


class SessionDAO:
    _session = None
    _session_maker = None

    def __init__(self, session_maker):
        self._session_maker = session_maker

    def getSession(self):
        '''
            Get the current session.

            :return: Current session
            :rtype: sqlalchemy.orm.session ?
        '''
        return self._session

    def setSession(self, session):
        '''
            Set the current session.

            :param sqlalchemy.orm.session session: New session
        '''
        self._session = session

    def openSession(self):
        '''
            Open a new session.

            :return: The newly opened session
            :rtype: sqlalchemy.orm.sessionmaker
        '''
        self._session = self._session_maker()
        return self._session

    def commit(self):
        '''
            Commit the current session.
        '''
        self._session.commit()

    def closeSession(self, commit=False):
        '''
            Close the current session.

            :param bool commit: True if I should commit the session
        '''
        if commit:
            self._session.commit()
        self._session.close()
        self._session = None


def withSession(method):
    '''
        Decorator: open and close a session.
    '''

    def newMethod(self, *args, **kwargs):
        # Open session
        close_session = False
        if self._session is None:
            self.openSession()
            close_session = True
        # Execute method
        result = None
        try:
            result = method(self, *args, **kwargs)
        except Exception:
            # Rollback
            self._session.rollback()
            raise
        else:
            # Commit
            if close_session:
                self._session.commit()
        finally:
            # Close session
            if close_session:
                self.closeSession()
        return result
    return newMethod


def _returnNonPersistent(method, full):
    '''
        Decorator: return a non persistent entity

        :param bool full: True if I should load the entity relations
    '''

    def newMethod(self, *args, **kwargs):
        persistent = method(self, *args, **kwargs)
        transform = self._entity_lazy
        if full:
            transform = self._entity
        entity = None
        if type(persistent) == list:
            entity = list(map(lambda p_entity: transform(p_entity), persistent))
        elif persistent is not None:
            entity = transform(persistent)
        return entity
    return newMethod


def returnNonPersistentFull(method):
    return _returnNonPersistent(method, True)


def returnNonPersistent(method):
    return _returnNonPersistent(method, False)


class EntityDAO(SessionDAO):
    '''
        Generic DAO from an entity.
    '''
    _persistent_entity = None
    _entity = None
    _entity_lazy = None
    _options = None

    @withSession
    @returnNonPersistent
    def getBy(self, **filters):
        '''
            Get a list of entities with the given filters.

            :param dict filters: Filters on the result
            :return: List of non persistent entities
            :rtype: list of entities.Common
        '''
        return self._getBy(filters=filters)

    @withSession
    @returnNonPersistentFull
    def getByName(self, name):
        '''
            Get an entity by name.

            :param str name: Name of the entity
            :return: Entity or None
            :rtype: entities.Common
        '''
        entities = self._getBy(filters={'name': name})
        if len(entities) == 0:
            return None
        else:
            return entities[0]

    @withSession
    @returnNonPersistent
    def getAll(self):
        '''
            Get all the entities.

            :return: List of non persistent entities
            :rtype: list of entities.Common
        '''
        return self._getBy()

    @withSession
    @returnNonPersistent
    def getRandom(self, limit=1):
        '''
            Return a list of rows taken randomly.
            Works only on SQLite.

            :param int limit: Limit
            :return: List of non persistent entities
            :rtype: list of entities.Common
        '''
        '''return self._session.query(self._persistent_entity)
                                .order_by(func.random())
                                .limit(limit).all()
        '''
        return self._getBy(order=func.random(), limit=limit)

    def _getBy(self, filter=None, filters_by=None, order=None, offset=None, limit=None):
        '''
            Get list of entities with the given filters.

            :param dict filters_by: Filters on the result (e.g. name="Smtg")
            :param dict filter: Filter on the result (e.g. User.email == "Smtg")
            :param Persistent.Entity.key order: Key used to sort
            :param int offset: Offset
            :param int limit: Limit
            :return: List of persistent entities
            :rtype: list of entities.Persistent
        '''
        query = self._session.query(self._persistent_entity)
        if self._options is not None:
            query = query.options(self._options)
        if filters_by is not None:
            query = query.filter_by(**filters_by)
        if filter is not None:
            query = query.filter(filter)
        if order is not None:
            query = query.order_by(order)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @withSession
    @returnNonPersistentFull
    def getById(self, id):
        '''
            Get an entity by id.

            :param int id: Id
            :return: Non persistent entity with the given id or None
            :rtype: entities.Common
        '''
        return self._getById(id)

    def _getById(self, id):
        '''
            Get an entity by id.

            :param int id: Id
            :return: Persistent entity with the given id or None
            :rtype: entities.Persistent
        '''
        entity = None
        try:
            entity = self._session.query(self._persistent_entity).filter_by(id=id).one()
        except exc.NoResultFound:
            entity = None
        return entity

    @withSession
    @returnNonPersistentFull
    def insert(self, **values):
        '''
            Insert an entity in the database.

            :param dict: Values for the entity to be added
            :return: Non persistent entity added
            :rtype: entities.Common
        '''
        persistent = self._persistent_entity(**values)
        self._session.add(persistent)
        return persistent

    @withSession
    @returnNonPersistent
    def update(self, entity, **updates):
        '''
            Update an entity in the database.

            :param entities.Common or int: Entity to be updated
            :param dict update: Values to update
            :return: Non persistent entity updated
            :rtype: entities.Common
        '''
        if type(entity) == int:
            entity_id = entity
        else:
            entity_id = entity.id
        persistent = self._getById(entity_id)
        for key, value in updates.items():
            setattr(persistent, key, value)
        return persistent

    @withSession
    def delete(self, entity):
        '''
            Delete an entity from the database.

            :param entities.Common or int: Entity to be deleted
        '''
        if type(entity) == int:
            entity_id = entity
        else:
            entity_id = entity.id
        persistent = self._getById(entity_id)
        self._session.delete(persistent)
