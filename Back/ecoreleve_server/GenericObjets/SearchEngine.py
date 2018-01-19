from ..Models import Base, thesaurusDictTraduction
from sqlalchemy import (
    select,
    and_,
    or_,
    exists,
    func,
    join,
    outerjoin,
    not_)
from sqlalchemy.sql import elements
from sqlalchemy.orm import aliased
from .FrontModules import ModuleGrids
from ..utils import Eval
import pandas as pd
from pyramid import threadlocal
from ..utils.datetime import parse


eval_ = Eval()


class QueryEngine(object):
    ''' This class is used to filter Object
        all properties
    '''

    def __init__(self, session, model):
        self.session = session
        self.model = model

    def initQueryStatement(self, selectable):
        table = self.model
        if selectable:
            query = select(selectable).select_from(table)
            
        else :
            query = select([table])
        return query

    def search(self, filters, selectable=[], order_by=None, limit=None, offset=None):
        query = self.initQueryStatement(selectable)
        query = self.applyFilters(query, filters)
        query = self._order_by(query, order_by)
        query = self._limit(query, limit)
        query = self._offset(query, offset)
        
        print(query)
        # queryResult = self.session.execute(query).fetchall()
    
        # return [dict(row) for row in queryResult]

    def applyFilters(self, query, filters):

        for criteria in filters:
            query = self._where(query, criteria)
        return query

    def _limit(self, query, param):
        ''' apply limit of returning rows
            @params is a dictionnary expected "limit" key containing integer value
        '''
        if param:
            query = query.limit(param)
        return query

    def _order_by(self, query, param):
        ''' apply order_by clause on @@ColmunName@@
            @params is a dictionnary expected "order_by" key 
            containing list of string value formatting as below:
                "@@ColumnName@@:asc" or "@@ColumnName@@:desc"
        '''
        if param and type(param) is list:
            orders_by_clause = []
            for order_clause in param:
                column_name, order_type = order_clause.split(':')
                column = self.getColumnByName(column_name)
                print(column_name, order_type, column)
                if not column:
                    continue

                if order_type == 'asc':
                   orders_by_clause.append(column.asc())
                elif order_type == 'desc':
                   orders_by_clause.append(column.desc())
                else:
                    continue
            print(orders_by_clause)
            if len(orders_by_clause) > 0:
                query = query.order_by(*orders_by_clause)
       
        return query

    def _offset(self, query, param):
        ''' apply offset of returning rows
            @params is a dictionnary expected "offset" key containing integer value
        '''
        if param:
            query = query.offset(param)
        
        return query

    def _where(self, query, criteria):
        ''' apply WHERE clause
            @criteria is a dictionnary expected "Colmun", "Operator" and "Value" keys
        '''
        column = self.getColumnByName(criteria['Column'])
        print(column)
        query = query.where(
                eval_.eval_binary_expr(
                    column, criteria['Operator'], criteria['Value']
                    )
                )
        return query

    def filer_(self, params):
        pass

    def getColumnByName(self, column_name):
        column = getattr(self.model, column_name, None)
        if not column:
            raise Exception('Column '+column_name+' not exists !')
        return column
