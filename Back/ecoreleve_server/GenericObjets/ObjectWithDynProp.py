from ecoreleve_server.Models import Base,DBSession
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, Numeric, String, Text, Unicode, text,Sequence,select, and_, or_,distinct
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.orm import relationship
from collections import OrderedDict
from datetime import datetime
from .FrontModules import FrontModules,ModuleForms, ModuleGrids
import transaction
from operator import itemgetter
from collections import OrderedDict
from traceback import print_exc


Cle = {'String':'ValueString','Float':'ValueFloat','Date':'ValueDate','Integer':'ValueInt'}

class ObjectWithDynProp:

    ObjContext = DBSession
    PropDynValuesOfNow = {}

    def __init__(self,ObjContext):
        self.ObjContext = DBSession
        self.PropDynValuesOfNow = {}

    def GetAllProp (self) :
        try :
            type_ = self.GetType()
        except :
            type_ = None
        dynPropTable = Base.metadata.tables[self.GetDynPropTable()]

        if type_ :
            result = type_.GetDynProps()
        else :
            result = DBSession.execute(select([dynPropTable])).fetchall()

        statProps = [{'name': statProp.key, 'type': statProp.type} for statProp in self.__table__.columns ]

        dynProps = [{'name':dynProp.Name,'type':dynProp.TypeProp}for dynProp in result]

        statProps.extend(dynProps)
        return statProps

    def GetFrontModulesID (self,ModuleType) :
        if not hasattr(self,'FrontModules') :
            self.FrontModules = DBSession.query(FrontModules).filter(FrontModules.Name==ModuleType).one()
        return self.FrontModules.ID

    def GetGridFields (self,ModuleType):
        try:
            typeID = self.GetType().ID
            gridFields = DBSession.query(ModuleGrids
            ).filter(and_(ModuleGrids.Module_ID == self.GetFrontModulesID(ModuleType),
                or_(ModuleGrids.FK_TypeObj == typeID ,ModuleGrids.FK_TypeObj ==None ))).all()
        except:
            gridFields = DBSession.query(ModuleGrids).filter(
                ModuleGrids.Module_ID == self.GetFrontModulesID(ModuleType) ).all()

        gridFields.sort(key=lambda x: str(x.GridOrder))
        cols = []

        for curConf in gridFields:
            curConfName = curConf.Name
            gridField = list(filter(lambda x : x['name'] == curConfName,self.GetAllProp()))
            if len(gridField)>0 :
                cols.append(curConf.GenerateColumn())
            elif curConf.QueryName is not None:
                cols.append(curConf.GenerateColumn())
        # for curProp in self.GetAllProp():
        #     curPropName = curProp['name']
        #     gridField = list(filter(lambda x : x.Name == curPropName,gridFields))
        #     if len(gridField)>0 :
        #         cols.append(gridField[0].GenerateColumn())
        return cols

    def GetFilters (self,ModuleType) :

        filters = []
        defaultFilters = []
        try:
            typeID = self.GetType().ID
            filterFields = DBSession.query(ModuleGrids).filter(
                and_(
                    ModuleGrids.Module_ID == self.GetFrontModulesID(ModuleType)
                    , or_( ModuleGrids.TypeObj == typeID,ModuleGrids.TypeObj == None)
                    )).all()
        except :
            filterFields = DBSession.query(ModuleGrids).filter(ModuleGrids.Module_ID == self.GetFrontModulesID(ModuleType)).all()


        # for curProp in self.GetAllProp():
        #     curPropName = curProp['name']
        #     filterField = list(filter(lambda x : x.Name == curPropName
        #         and x.IsSearchable == 1 ,filterFields))

        #     if len(filterField)>0 :
        #         filters.append(filterField[0].GenerateFilter())

            # elif len(list(filter(lambda x : x.Name == curPropName, filterFields))) == 0:
            #     filter_ = {
            #     'name' : curPropName,
            #     'label' : curPropName,
            #     'type' : 'Text'
            #     }
        for curConf in filterFields:
            curConfName = curConf.Name
            filterField = list(filter(lambda x : x['name'] == curConfName
                and curConf.IsSearchable == 1 ,self.GetAllProp()))

            if len(filterField)>0 :
                filters.append(curConf.GenerateFilter())
            elif curConf.QueryName is not None:
                filters.append(curConf.GenerateFilter())


        return filters

    def GetType(self):
        raise Exception("GetType not implemented in children")

    def GetDynPropValuesTable(self):
        return self.__tablename__ + 'DynPropValue'

    def GetDynPropValuesTableID(self):
        return 'ID'

    def GetMyIDName(self):
        return 'ID'

    def GetDynPropTable(self):
        return self.__tablename__ + 'DynProp'

    def GetDynPropFKName(self):
        return 'FK_' + self.__tablename__ + 'DynProp'

    # def GetSelfFKName(self):
    #     return 'FK_' + self.__tablename__ + 'DynProp'  ###### ====> Not used , the same thing as GetDynPropFKName Why ??

    def GetSelfFKNameInValueTable(self):
        return 'FK_' + self.__tablename__

    def GetpkValue(self) :
        return self.ID

    def GetProperty(self,nameProp) :
        try :
            return getattr(self,nameProp)
        except :
            return self.PropDynValuesOfNow[nameProp]

    def SetProperty(self,nameProp,valeur) :
        if hasattr(self,nameProp):
            try :
                curTypeAttr = str(self.__table__.c[nameProp].type).split('(')[0]
                if 'Date' in curTypeAttr :
                    try : 
                        valeur = nameProp.strftime('%d/%m/%Y %H:%M:%S')
                    except :
                        valeur = nameProp.strftime('%d/%m/%Y')
            except :
                print(nameProp+' is not a column')
                pass
            setattr(self,nameProp,valeur)
        else:
            if (nameProp in self.GetType().DynPropNames):
                if (nameProp not in self.PropDynValuesOfNow) or (str(self.PropDynValuesOfNow[nameProp]) != str(valeur)):
                    # on affecte si il y a une valeur et si elle est différente de la valeur existante
                    print('valeur modifiée pour ' + nameProp)
                    NouvelleValeur = self.GetNewValue(nameProp)
                    NouvelleValeur.StartDate = datetime.today()
                    setattr(NouvelleValeur,Cle[self.GetDynProps(nameProp).TypeProp],valeur)
                    self.PropDynValuesOfNow[nameProp] = valeur
                    self.GetDynPropValues().append(NouvelleValeur)
                else:
                    print('valeur non modifiée pour ' + nameProp)
                    return
            else :
                print('propriété inconnue ' + nameProp)
                # si la propriété dynamique existe déjà et que la valeur à affectée est identique à la valeur existente
                # => alors on insére pas d'historique car pas de chanegement

    def GetNewValue(self):
        raise Exception("GetNewValue not implemented in children")

    def LoadNowValues(self):
        curQuery = 'select V.*, P.Name,P.TypeProp from ' + self.GetDynPropValuesTable() + ' V JOIN ' + self.GetDynPropTable() + ' P ON P.' + self.GetDynPropValuesTableID() + '= V.' + self.GetDynPropFKName() + ' where '
        curQuery += 'not exists (select * from ' + self.GetDynPropValuesTable() + ' V2 '
        curQuery += 'where V2.' + self.GetDynPropFKName() + ' = V.' + self.GetDynPropFKName() + ' and V2.' + self.GetSelfFKNameInValueTable() + ' = V.' + self.GetSelfFKNameInValueTable() + ' '
        curQuery += 'AND V2.startdate > V.startdate)'
        curQuery +=  'and v.' + self.GetSelfFKNameInValueTable() + ' =  ' + str(self.GetpkValue() )

        Values = self.ObjContext.execute(curQuery).fetchall()
        for curValue in Values :
            row = OrderedDict(curValue)
            self.PropDynValuesOfNow[row['Name']] = self.GetRealValue(row)

    def GetRealValue(self,row):
        return row[Cle[row['TypeProp']]]

    def UpdateFromJson(self,DTOObject):
        for curProp in DTOObject:
            #print('Affectation propriété ' + curProp)
            if (curProp.lower() != 'id'):
                self.SetProperty(curProp,DTOObject[curProp])

    def GetFlatObject(self,schema=None):
        resultat = {}

        if self.ID is not None : 
            max_iter = max(len( self.__table__.columns),len(self.PropDynValuesOfNow))
            for i in range(max_iter) :
                # Get static Properties #
                try :
                    curStatProp = list(self.__table__.columns)[i]
                    resultat[curStatProp.key] = self.GetProperty(curStatProp.key)
                except :
                    pass
                # Get dynamic Properties #
                try :
                    curDynPropName = list(self.PropDynValuesOfNow)[i]
                    resultat[curDynPropName] = self.GetProperty(curDynPropName)
                except Exception as e :
                    pass
        else : 
            max_iter = len( self.__table__.columns)
            for i in range(max_iter) :
                # Get static Properties #
                try :
                    curStatProp = list(self.__table__.columns)[i]
                    curVal = self.GetProperty(curStatProp.key)
                    if curVal is not None :
                        resultat[curStatProp.key] = self.GetProperty(curStatProp.key)
                except :
                    pass
        # Add TypeName in JSON
        # resultat['TypeName'] = self.GetType().Name
        return resultat

    def GetSchemaFromStaticProps(self,FrontModules,DisplayMode):
        Editable = (DisplayMode.lower()  == 'edit')
        resultat = {}
        type_ = self.GetType().ID
        Fields = self.ObjContext.query(ModuleForms).filter(ModuleForms.Module_ID == FrontModules.ID).order_by(ModuleForms.FormOrder).all()
        curEditable = Editable

        for curStatProp in self.__table__.columns:

            CurModuleForms = list(filter(lambda x : x.Name == curStatProp.key and (x.TypeObj== str(type_) or x.TypeObj == None) , Fields))
            if (len(CurModuleForms)> 0 ):
                # Conf définie dans FrontModules
                CurModuleForms = CurModuleForms[0]
                curSize = CurModuleForms.FieldSizeDisplay
                if curEditable:
                    curSize = CurModuleForms.FieldSizeEdit

                if (CurModuleForms.FormRender & 2) == 0:
                    curEditable = False

                if CurModuleForms.FormRender > 2 :
                    curEditable = True

                resultat[CurModuleForms.Name] = CurModuleForms.GetDTOFromConf(curEditable,str(ModuleForms.GetClassFromSize(curSize)))
        return resultat

    def GetDTOWithSchema(self,FrontModules,DisplayMode):

        schema = self.GetSchemaFromStaticProps(FrontModules,DisplayMode)
        ObjType = self.GetType()
        ObjType.AddDynamicPropInSchemaDTO(schema,FrontModules,DisplayMode)

        if (DisplayMode.lower() != 'edit'):
            for curName in schema:
                schema[curName]['editorAttrs'] = { 'disabled' : True }

        resultat = {
            'schema':schema,
            'fieldsets' : ObjType.GetFieldSets(FrontModules,schema)
            }

        ''' IF ID is send from front --> get data of this object in order to display value into form which will be sent'''
        data = self.GetFlatObject(schema)
        resultat['data'] = data
        if self.ID :
            resultat['data']['id'] = self.ID
        else :
            resultat['data']['id'] = 0
        return resultat
