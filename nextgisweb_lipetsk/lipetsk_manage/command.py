# -*- coding: utf-8 -*-
import csv
import subprocess
import tempfile
from datetime import datetime
from tempfile import NamedTemporaryFile

import os
import sys
from sqlalchemy.orm import joinedload_all
import transaction

from ..lipetsk_site.well_known_names import Layers, Fields

from nextgisweb.feature_layer import FIELD_TYPE
from nextgisweb.resource import Resource
from nextgisweb.vector_layer import VectorLayer
from nextgisweb import DBSession
from nextgisweb.command import Command
from .common import VectorLayerUpdater


@Command.registry.register
class ManageCommands:
    identity = 'lipetsk.manage'

    @classmethod
    def argparser_setup(cls, parser, env):
        parser.add_argument('--action',
                            required=True,
                            choices=[
                                'append_url_field',
                                'load_icons',
                                'import_values'
                            ])

    @classmethod
    def execute(cls, args, env):
        if args.action == 'append_url_field':
            cls.append_url_field()
        if args.action == 'load_icons':
            cls.load_icons(env)
        if args.action == 'import_values':
            cls.import_values(env)



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

    @classmethod
    def load_icons(cls, env):
        db_session = DBSession()

        transaction.manager.begin()
        print 'Loading style icons...'
        env.marker_library.load_collection('nextgisweb_lipetsk', '/lipetsk_manage/styles')
        transaction.manager.commit()

    @classmethod
    def import_values(cls, env):
        #create temp file
        with NamedTemporaryFile(delete=True) as temp_file:
            try:

                # open ftp
                sett = env.lipetsk_manage.settings

                #ftp_client = ftplib.FTP(sett['ftp_address'])
                #ftp_client.login(user=sett['ftp_login'], passwd=sett['ftp_pass'])
                #ftp_client.retrbinary('RETR ' + sett['ftp_file_name'], temp_file.write)
                #ftp_client.close()
                #temp_file.seek(0)

                temp_file_name = tempfile.mktemp()

                proc_exec = subprocess.check_call([
                    'wget',
                    'ftp://%s:%s@%s/%s' % (sett['ftp_login'], sett['ftp_pass'], sett['ftp_address'], sett['ftp_file_name']),
                    '-O',
                    temp_file_name
                ])

                temp_file = open(temp_file_name)

                # parse csv to list
                dialect = csv.Sniffer().sniff(temp_file.read(), delimiters=';')
                temp_file.seek(0)

                mon_values = dict()
                csv_reader = csv.DictReader(temp_file, dialect=dialect)
                for row in csv_reader:
                    code = int(row['PNZCode'])

                    date_mon = row['Date']
                    time_mon = row['Time']

                    component = unicode(row['Component'], 'cp1251')
                    emission = row['Emission']

                    new_val = {
                        'dt': datetime.strptime(u'%s %s' % (date_mon, time_mon), '%d.%m.%Y %H:%M:%S'),
                        'comp_text': u'%s - %s' % (component, emission)
                    }

                    if code in mon_values.keys():
                        total = mon_values[code]
                        total.append(new_val)
                        mon_values[code] = total
                    else:
                        mon_values[code] = [new_val]

                # close and remove
                temp_file.close()
                sys.path.remove(temp_file_name)

                # get last values for every code
                last_values = {}
                for code, values in mon_values.iteritems():
                    # get max dt
                    max_dt = values[0]['dt']
                    for val in values:
                        if val['dt'] > max_dt:
                            max_dt = val['dt']
                    # filter values by dt
                    filtered = filter(lambda x: x['dt'] == max_dt, values)
                    # generate str
                    result_str = ''
                    for val in filtered:
                        if result_str:
                            result_str = u'%s\n%s' % (result_str, val['comp_text'])
                        else:
                            result_str = val['comp_text']
                    # set
                    last_values[code] = {'comp_text': result_str, 'dt': max_dt}

                # save to layer
                db_session = DBSession()
                transaction.manager.begin()

                distr_res = db_session.query(Resource).filter(Resource.keyname == Layers.STATIONARY_POSTS, Resource.cls == VectorLayer.identity).one()
                query = distr_res.feature_query()
                features = query()
                for feature in features:
                    if feature.fields[Fields.STATIONARY_POSTS_ID] in last_values.keys():
                        feat_vals = last_values[feature.fields[Fields.STATIONARY_POSTS_ID]]
                        feature.fields[Fields.STATIONARY_POSTS_MONIT_DT] = datetime.strftime(feat_vals['dt'], '%d.%m.%Y %H:%M')
                        feature.fields[Fields.STATIONARY_POSTS_MONIT_RES] = feat_vals['comp_text']
                        distr_res.feature_put(feature)

                transaction.manager.commit()
            except:
                import traceback
                traceback.print_exc()

            finally:
                # try to remove temp file
                try:
                    sys.path.remove(temp_file_name)
                except:
                    pass

