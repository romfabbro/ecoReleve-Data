/****** Script de la commande SelectTopNRows à partir de SSMS  ******/
DELETE Region 

DBCC CHECKIDENT ('[Region]', RESEED, 0);

INSERT INTO [EcoReleve_ECWP].[dbo].[Region]
( [Country]
      ,[Region]
      ,[valid_geom]
      ,[max_lat]
      ,[min_lat]
      ,[max_lon]
      ,[min_lon]
      ,[Reneco_Country]
      ,[SHAPE_Leng]
      ,[SHAPE_Area]
      ,[geom])
select 
      [Country]
      ,Place
      ,[valid_geom]
      ,[maxlat]
      ,[minlat]
      ,[maxlon]
      ,[minlon]
      ,[Reneco_Country]
      ,[SHAPE_Leng]
      ,[SHAPE_Area]
      ,[geom]
  FROM [ECWP-eReleveData].[dbo].geo_CNTRIES_and_RENECO_MGMTAreas