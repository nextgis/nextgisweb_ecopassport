# -*- coding: utf-8 -*-
from sqlalchemy.orm import joinedload_all
import transaction

from nextgisweb.feature_layer import FIELD_TYPE
from nextgisweb.vector_layer import VectorLayer
from nextgisweb import DBSession, db
from nextgisweb.command import Command
from .common import VectorLayerUpdater


@Command.registry.register
class ManageCommands:
    identity = 'lipetsk.commands'

    @classmethod
    def argparser_setup(cls, parser, env):
        parser.add_argument('--action',
                            required=True,
                            choices=[
                                'append_url_field',
                            ])

    @classmethod
    def execute(cls, args, env):
        if args.migration == 'append_url_field':
            cls.append_url_field()



    @classmethod
    def append_url_field(cls):
        db_session = DBSession()

        transaction.manager.begin()

        resources = db_session.query(VectorLayer).options(joinedload_all('fields')).all()

        for vec_layer in resources:
            try:
                VectorLayerUpdater.append_field(vec_layer, 'url', FIELD_TYPE.STRING, 'Ссылка')
                print "Fields of %s was updated!" % vec_layer.keyname

            except Exception, ex:
                print "Error on update fields struct %s: %s" % (vec_layer.keyname, ex.message)

        transaction.manager.commit()
        db_session.close()
