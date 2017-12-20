from sqlalchemy.ext.declarative import declarative_base
import configparser
from sqlalchemy import select
from sqlalchemy.exc import TimeoutError
import pandas as pd
from traceback import print_exc
import requests
from multiprocessing.dummy import Pool as ThreadPool
import copy
import time
import redis


AppConfig = configparser.ConfigParser()
AppConfig.read('././development.ini')
print(AppConfig['app:main']['sensor_schema'])

pendingSensorData = []
indivLocationData = []
stationData = []
graphDataDate = {'indivLocationData': None, 'pendingSensorData': None}
DBSession = None


class myBase(object):

    __table_args__ = {'implicit_returning': False}


Base = declarative_base(cls=myBase)
BaseExport = declarative_base()
dbConfig = {
    'data_schema': AppConfig['app:main']['data_schema'],
    'sensor_schema': AppConfig['app:main']['sensor_schema'],
    'cn.dialect': AppConfig['app:main']['cn.dialect'],
}

try:
    dbConfig['dbLog.schema'] = AppConfig['app:main']['dbLog.schema']
    dbConfig['dbLog.url'] = AppConfig['app:main']['dbLog.url']
except:
    print_exc()
    pass

DynPropNames = {
    'ProtocoleType': {
        'DynPropContextTable': 'ProtocoleType_ObservationDynProp',
        'DynPropTable': 'ObservationDynProp',
        'FKToDynPropTable': 'FK_ObservationDynProp'
    }
}


thesaurusDictTraduction = {}
invertedThesaurusDict = {'en': {}, 'fr': {}}
userOAuthDict = {}


def loadUserRole(session):
    global userOAuthDict
    # session = config.registry.dbmaker()
    VuserRole = Base.metadata.tables['VUser_Role']
    query = select(VuserRole.c)

    results = session.execute(query).fetchall()
    userOAuthDict = pd.DataFrame.from_records(
        results, columns=['user_id', 'role_id'])


USERS = {2: 'superUser',
         3: 'user',
         1: 'admin'}

GROUPS = {'superUser': ['group:superUsers'],
          'user': ['group:users'],
          'admin': ['group:admins']}


def groupfinder(userid, request):
    session = request.dbsession
    Tuser_role = Base.metadata.tables['VUser_Role']
    query_check_role = select([Tuser_role.c['role']]).where(
        Tuser_role.c['userID'] == int(userid))
    currentUserRoleID = session.execute(query_check_role).scalar()

    if currentUserRoleID in USERS:
        currentUserRole = USERS[currentUserRoleID]
        return GROUPS.get(currentUserRole, [])


def cache_callback(request, session):
    if isinstance(request.exception, TimeoutError):
        session.get_bind().dispose()


from ..GenericObjets.Business import *
import json


def db(request):
    makerDefault = request.registry.dbmaker
    session = makerDefault()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
            cache_callback(request, session)
            session.close()
            makerDefault.remove()
        else:
            try:
                session.commit()
            except BusinessRuleError as e:
                session.rollback()
                request.response.status_code = 409
                request.response.text = e.value
            except Exception as e:
                session.rollback()
                request.response.status_code = 500
            finally:
                session.close()
                makerDefault.remove()

    request.add_finished_callback(cleanup)
    return session


from ..GenericObjets.FrontModules import *
from .CustomTypes import *
from .Protocoles import *
from .User import User
from .Station import *
from .Region import *
from .FieldActivity import *
from .Individual import *
from .Sensor import *
from .MonitoredSite import *
from .Equipment import *
from .Import import *
from .SensorData import *
from .List import *
from .Log import sendLog
from .Project import *

# LinkedTables['Individual'] = Individual
# LinkedTables['Station'] = Station
# LinkedTables['Protocoles'] = Protocoles
# LinkedTables['Sensor'] = Sensor
# LinkedTables['MonitoredSite'] = MonitoredSite


from sqlalchemy import (Column,
                        ForeignKey,
                        String,
                        Integer,
                        Float,
                        DateTime,
                        select,
                        join,
                        func,
                        not_,
                        exists,
                        event,
                        Table,
                        Index,
                        UniqueConstraint,
                        Table)
from sqlalchemy.orm import relationship, aliased, class_mapper, mapper
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr


def test(config):
    from ..controllers import ModelFactory
    session = config.registry.dbmaker()
    alllModel = ModelFactory.Tropdelaballe
    o = alllModel(session=session)
    # o = session.query(alllModel).get(1016)
    # print(o._Alleluhia.values)
    # print(o)
    # print(o.type_id)
    # print(o._type)
    o.values = {
        'NEWdyn1': 'SDJNDSKJFBDSKFBDSGKJBchamps lié amettre a jour',
        'dyn2': 888,
        'dyn5': 'vallalalal',
        'toto': 87.93,
        'type_id': 1
        # 'FK_alleeelaaaa': 5
    }
    session.add(o)
    # o = session.query(alllModel).get(3)
    # print(o.type)
    # print(o._type._type_properties[0].linkedTable)
    # print(o.properties)
    # print(o.values)
    print(o.getHistory())
    # print(o.getLinkedField())
    # values = {'FK_MyObjectType':1,
    #            'toto':'blelelelqsdqsddqsdfelele',
    #            'test1':'newsdsdccwxcx   xcwxcsdfwx  <dssss'}

    # o.updateValues(values, '02/08/2016')
    # o2 = MyObject(session=session)
    # o2.values={'FK_MyObjectType':1,
    #            'toto':'newtotoVal',
    #            'test1':'test rockssssssssss'}
    # print(o2.type)
    # print(o2.properties)
    # session.add(o2)
    # # print(MyObject.lastValueView())*
    # print(OHMyObject.TypeClass.PropertiesClass.__tablename__)
    # print(MyObject.TypeClass.PropertiesClass.__tablename__)
    # print(MyObject.LastDynamicValueViewClass.select())
    session.commit()
    pass
