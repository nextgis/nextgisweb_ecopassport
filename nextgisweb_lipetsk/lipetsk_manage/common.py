# coding=utf-8
import uuid
from sqlalchemy import Column
import transaction
from nextgisweb import DBSession
from nextgisweb.feature_layer import FIELD_TYPE
from nextgisweb.vector_layer.model import VectorLayerField, VectorLayer, _FIELD_TYPE_2_DB

__author__ = 'yellow'


class VectorLayerUpdater(object):

    @staticmethod
    def change_field_display_name(resource, field_keyname, new_displayname, make_transaction=False):

        if not isinstance(resource, VectorLayer):
            raise Exception('Unsupported resource type!')

        if field_keyname not in [field.keyname for field in resource.fields]:
            raise Exception('Field does not exists in the table!')

        #start transaction
        if make_transaction:
            transaction.manager.begin()

        for field in resource.fields:
            if field.keyname == field_keyname:
                field.display_name = new_displayname

        #close transaction
        if make_transaction:
            transaction.manager.commit()
        else:
            db_session = DBSession()
            db_session.flush()


    @staticmethod
    def append_field(resource, field_keyname, field_type, field_display_name, field_grid_vis=True, make_transaction=False):

        if not isinstance(resource, VectorLayer):
            raise Exception('Unsupported resource type!')

        if field_type not in FIELD_TYPE.enum:
            raise Exception('Unsupported field type!')

        if field_keyname in [field.keyname for field in resource.fields]:
            raise Exception('Field already exists in the table!')

        #start transaction
        if make_transaction:
            transaction.manager.begin()

        #create uuid for field
        uid = str(uuid.uuid4().hex)

        #create column
        VectorLayerUpdater.__create_column(resource.tbl_uuid, uid, _FIELD_TYPE_2_DB[field_type])

        #add field to register
        vfl = VectorLayerField()
        vfl.keyname = field_keyname
        vfl.datatype = field_type
        vfl.display_name = field_display_name
        vfl.grid_visibility = field_grid_vis
        vfl.fld_uuid = uid

        resource.fields.append(vfl)

        #close transaction
        if make_transaction:
            transaction.manager.commit()
        else:
            db_session = DBSession()
            db_session.flush()

    @staticmethod
    def change_field_datatype(resource, field_keyname, new_field_type, make_transaction=False):

        if not isinstance(resource, VectorLayer):
            raise Exception('Unsupported resource type!')

        if new_field_type not in FIELD_TYPE.enum:
            raise Exception('Unsupported field type!')

        target_field = filter(lambda field: field.keyname == field_keyname, resource.fields)

        if not target_field:
            raise Exception('Field not found in the table!')
        else:
            target_field = target_field[0]

        if new_field_type == target_field.datatype:
            print 'Field already has such type!'
            return

        #start transaction
        if make_transaction:
            transaction.manager.begin()

        # change data type physic
        VectorLayerUpdater.__change_column_datatype(resource.tbl_uuid, target_field.fld_uuid, _FIELD_TYPE_2_DB[new_field_type])

        # set new type in field registry
        target_field.datatype = new_field_type
        target_field.persist()


        #close transaction
        if make_transaction:
            transaction.manager.commit()
        else:
            db_session = DBSession()
            db_session.flush()


    @staticmethod
    def __create_column(table_uid, field_uid, field_type):
        db_session = DBSession()
        engine = db_session.get_bind()

        column = Column('fld_%s' % field_uid, field_type)
        column_name = column.compile(dialect=engine.dialect)
        column_type = column.type.compile(engine.dialect)
        engine.execute('ALTER TABLE "vector_layer"."layer_%s" ADD COLUMN %s %s' % (table_uid, column_name, column_type))

    @staticmethod
    def __drop_column(table_uid, field_uid):
        # еще не юзал!
        db_session = DBSession()
        engine = db_session.get_bind()

        column = Column('fld_%s' % field_uid)
        column_name = column.compile(dialect=engine.dialect)
        engine.execute('ALTER TABLE "vector_layer"."layer_%s" DROP COLUMN %s' % (table_uid, column_name))

    @staticmethod
    def __change_column_datatype(table_uid, field_uid, new_column_type):
        db_session = DBSession()
        engine = db_session.get_bind()

        column = Column('fld_%s' % field_uid, new_column_type)
        column_name = column.compile(dialect=engine.dialect)
        column_type = column.type.compile(engine.dialect)
        engine.execute('ALTER TABLE "vector_layer"."layer_%s" ALTER COLUMN %s TYPE %s' % (table_uid, column_name, column_type))


    @staticmethod
    def drop_vector_layer_table(table_uid, make_transaction=False):
        db_session = DBSession()

        #start transaction
        if make_transaction:
            transaction.manager.begin()

        engine = db_session.get_bind()
        engine.execute('DROP TABLE "vector_layer"."layer_%s"' % table_uid)

        #close transaction
        if make_transaction:
            transaction.manager.commit()
        else:
            db_session.flush()


class StructUpdater:

    @classmethod
    def create_column(cls, table_object, field_name, field_type):
        db_session = DBSession()
        engine = db_session.get_bind()

        column = Column(field_name, field_type)
        column_name = column.compile(dialect=engine.dialect)
        column_type = column.type.compile(engine.dialect)
        engine.execute('ALTER TABLE "%s"."%s" ADD COLUMN %s %s' % (table_object.schema or 'public', table_object.name, column_name, column_type))