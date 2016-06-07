from pyramid.view import view_config
from ..Models import (
    Station,
    MonitoredSite,
    MonitoredSiteType,
    MonitoredSiteDynPropValue,
    MonitoredSiteDynProp,
    MonitoredSitePosition,
    Equipment,
    Sensor,
    SensorType,
    Base,
    fieldActivity,
    MonitoredSiteList
    )
from ..GenericObjets.FrontModules import FrontModules
from ..GenericObjets import ListObjectWithDynProp
import json, itertools
from datetime import datetime
import datetime as dt
import pandas as pd
import numpy as np
from sqlalchemy import select, and_,cast, DATE,func,desc,join,asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.response import Response
from traceback import print_exc
from collections import OrderedDict
import io
from pyramid.response import Response ,FileResponse

prefix = 'monitoredSites'

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/action', renderer='json', request_method = 'GET')
@view_config(route_name= prefix+'/id/history/action', renderer='json', request_method = 'GET')
@view_config(route_name= prefix+'/id/equipment/action', renderer='json', request_method = 'GET')
def actionOnMonitoredSite(request):
    print ('\n*********************** Action **********************\n')
    dictActionFunc = {
    'count' : count_,
    'forms' : getForms,
    '0' : getForms,
    'getFields': getFields,
    'getFilters': getFilters,
    'getType':getMonitoredSiteType
    }
    actionName = request.matchdict['action']
    return dictActionFunc[actionName](request)

def count_ (request = None,listObj = None) :
    session = request.dbsession
    if request is not None : 
        data = request.params
        if 'criteria' in data: 
            data['criteria'] = json.loads(data['criteria'])
            if data['criteria'] != {} :
                searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]

        listObj = ListObjectWithDynProp(MonitoredSite)
        count = listObj.count(searchInfo = searchInfo)
    else : 
        count = listObj.count()
    return count 

def getFilters (request):
    session = request.dbsession
    ModuleType = 'MonitoredSiteGrid'
    filtersList = MonitoredSite().GetFilters(ModuleType)
    filters = {}
    for i in range(len(filtersList)) :
        filters[str(i)] = filtersList[i]

    return filters

def getForms(request) :
    session = request.dbsession

    typeMonitoredSite = request.params['ObjectType']
    ModuleName = 'MonitoredSiteForm'
    Conf = session.query(FrontModules).filter(FrontModules.Name==ModuleName ).first()
    newMonitoredSite = MonitoredSite(FK_MonitoredSiteType = typeMonitoredSite)
    newMonitoredSite.init_on_load()
    schema = newMonitoredSite.GetDTOWithSchema(Conf,'edit')

    return schema

def getFields(request) :
    session = request.dbsession
    ModuleType = request.params['name']
    if ModuleType == 'default' :
        ModuleType = 'MonitoredSiteGrid'
    cols = MonitoredSite().GetGridFields(ModuleType)

    return cols

def getMonitoredSiteType(request):
    session = request.dbsession
    query = select([MonitoredSiteType.ID.label('val'), MonitoredSiteType.Name.label('label')])
    response = [ OrderedDict(row) for row in session.execute(query).fetchall()]
    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'GET')
def getMonitoredSite(request):
    session = request.dbsession

    id = request.matchdict['id']
    curMonitoredSite = session.query(MonitoredSite).get(id)
    curMonitoredSite.LoadNowValues()

    # if Form value exists in request --> return data with schema else return only data
    if 'FormName' in request.params :
        ModuleName = request.params['FormName']
        try :
            DisplayMode = request.params['DisplayMode']
        except : 
            DisplayMode = 'display'
        Conf = session.query(FrontModules).filter(FrontModules.Name=='MonitoredSiteForm').first()
        response = curMonitoredSite.GetDTOWithSchema(Conf,DisplayMode)
    else : 
        response  = curMonitoredSite.GetFlatObject()
    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id/history', renderer='json', request_method = 'GET')
def getMonitoredSiteHistory(request):
    session = request.dbsession

    id = request.matchdict['id']
    data = request.params.mixed()
    searchInfo = {}
    searchInfo['criteria'] = [{'Column': 'ID', 'Operator':'Is', 'Value':int(id)}]
    try:
        searchInfo['order_by'] = json.loads(data['order_by'])
    except:
        searchInfo['order_by'] = []
    # searchInfo['offset'] = json.loads(data['offset'])
    # searchInfo['per_page'] = json.loads(data['per_page'])

    ModuleType = 'MonitoredSiteGridHistory'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()
    view = Base.metadata.tables['MonitoredSitePosition']
    listObj = ListObjectWithDynProp(MonitoredSite,moduleFront,View=view)
    dataResult = listObj.GetFlatDataList(searchInfo)

    if 'geo' in request.params :
        geoJson=[]
        for row in dataResult:
            geoJson.append({'type':'Feature', 'properties':{'Date':row['StartDate']}, 'geometry':{'type':'Point', 'coordinates':[row['LAT'],row['LON']]}})
        result = {'type':'FeatureCollection', 'features':geoJson}
    else : 
        countResult = listObj.count(searchInfo)
        result = [{'total_entries':countResult}]
        result.append(dataResult)
    return result

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id/equipment', renderer='json', request_method = 'GET')
def getMonitoredSiteEquipment(request):
    session = request.dbsession
    table = Base.metadata.tables['MonitoredSiteEquipment']
    id_site = request.matchdict['id']

    joinTable = join(table,Sensor, table.c['FK_Sensor'] == Sensor.ID)
    joinTable = join(joinTable,SensorType, Sensor.FK_SensorType == SensorType.ID)
    query = select([table.c['StartDate'],table.c['EndDate'],Sensor.UnicIdentifier,table.c['FK_MonitoredSite'],SensorType.Name.label('Type')]
        ).select_from(joinTable
        ).where(table.c['FK_MonitoredSite'] == id_site
        ).order_by(desc(table.c['StartDate']))
    
    result = session.execute(query).fetchall()
    response = []
    for row in result:
        curRow = OrderedDict(row)
        curRow['StartDate'] = curRow['StartDate'].strftime('%Y-%m-%d %H:%M:%S')
        if curRow['EndDate'] is not None :
            curRow['EndDate'] = curRow['EndDate'].strftime('%Y-%m-%d %H:%M:%S')
        else:
             curRow['EndDate'] = ''
        response.append(curRow)

    return response
# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'DELETE')
def deleteMonitoredSite(request):
    session = request.dbsession
    id_ = request.matchdict['id']
    curMonitoredSite = session.query(MonitoredSite).get(id_)
    session.delete(curMonitoredSite)
    return True

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/id', renderer='json', request_method = 'PUT')
def updateMonitoredSite(request):
    session = request.dbsession
    try:
        data = request.json_body
        id = request.matchdict['id']
        curMonitoredSite = session.query(MonitoredSite).get(id)
        curMonitoredSite.LoadNowValues()
        curMonitoredSite.UpdateFromJson(data)
        response = {}

    except IntegrityError as e:
        print('\n\n\n *****IntegrityError errrroorr') 
        session.rollback()
        response = request.response
        response.status_code = 510
        response.text = "IntegrityError"
    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix+'/', renderer='json', request_method = 'POST')
def insertMonitoredSite(request):
    data = request.json_body
    if not isinstance(data,list):
        return insertOneNewMonitoredSite(request)
    else :
        print('_______INsert LIST')

# ------------------------------------------------------------------------------------------------------------------------- #
def insertOneNewMonitoredSite (request) :
    session = request.dbsession

    data = {}
    for items , value in request.json_body.items() :
        data[items] = value
    try:        
        newMonitoredSite = MonitoredSite(FK_MonitoredSiteType = data['FK_MonitoredSiteType'], Creator = request.authenticated_userid['iss'] )
        newMonitoredSite.MonitoredSiteType = session.query(MonitoredSiteType).filter(MonitoredSiteType.ID==data['FK_MonitoredSiteType']).first()
        newMonitoredSite.init_on_load()
        newMonitoredSite.UpdateFromJson(data)
        session.add(newMonitoredSite)
        session.flush()
        response = {'ID': newMonitoredSite.ID}

    except IntegrityError as e:
        session.rollback()
        request.response.status_code = 520
        response = request.response
        response.text = "This name is already used for another monitored site"
        pass

    return response

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name= prefix, renderer='json', request_method = 'GET')
def searchMonitoredSite(request):
    session = request.dbsession
    data = request.params.mixed()
    searchInfo = {}
    searchInfo['criteria'] = []

    if 'criteria' in data: 
        data['criteria'] = json.loads(data['criteria'])
        if data['criteria'] != {} :
            searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]

    searchInfo['order_by'] = json.loads(data['order_by'])
    searchInfo['offset'] = json.loads(data['offset'])
    searchInfo['per_page'] = json.loads(data['per_page'])

    ModuleType = 'MonitoredSiteGrid'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()

    start = datetime.now()
    # listObj = ListObjectWithDynProp(MonitoredSite,moduleFront,View=Base.metadata.tables['MonitoredSitePositionsNow'])
    listObj = MonitoredSiteList(moduleFront,View=Base.metadata.tables['MonitoredSitePositionsNow'])
    
    dataResult = listObj.GetFlatDataList(searchInfo)
    countResult = listObj.count(searchInfo)

    result = [{'total_entries':countResult}]
    result.append(dataResult)

    return result

# ------------------------------------------------------------------------------------------------------------------------- #
@view_config(route_name=prefix + '/export', renderer='json', request_method='GET')
def sensors_export(request):
    session = request.dbsession
    data = request.params.mixed()
    searchInfo = {}
    searchInfo['criteria'] = []
    if 'criteria' in data: 
        data['criteria'] = json.loads(data['criteria'])
        if data['criteria'] != {} :
            searchInfo['criteria'] = [obj for obj in data['criteria'] if obj['Value'] != str(-1) ]

    searchInfo['order_by'] = []

    ModuleType = 'MonitoredSiteGrid'
    moduleFront  = session.query(FrontModules).filter(FrontModules.Name == ModuleType).one()

    listObj = ListObjectWithDynProp(MonitoredSite,moduleFront,View=Base.metadata.tables['MonitoredSitePositionsNow'])
    dataResult = listObj.GetFlatDataList(searchInfo)

    df = pd.DataFrame.from_records(dataResult, columns=dataResult[0].keys(), coerce_float=True)

    fout = io.BytesIO()
    writer = pd.ExcelWriter(fout)
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    file = fout.getvalue()

    dt = datetime.now().strftime('%d-%m-%Y')
    return Response(file,content_disposition= "attachment; filename=monitoredSites_export_"+dt+".xlsx",content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@view_config(route_name= prefix+'/id/station', renderer='json', request_method = 'GET')
def getStationHistory (request):
    session = request.dbsession
    id_site = request.matchdict['id']
    joinTable = join(Station,fieldActivity,Station.fieldActivityId == fieldActivity.ID)
    query = select([Station.StationDate, Station.LAT,Station.LON,Station.ID,Station.Name
        ,fieldActivity.Name.label('fieldActivity_Name')]).select_from(joinTable).where(Station.FK_MonitoredSite == id_site)

    result = session.execute(query).fetchall()
    response = []
    for row in result :
        row = dict(row)
        row['StationDate'] = row['StationDate'].strftime('%Y-%m-%d %H:%M:%S')
        print(row)
        response.append(row)

    return response