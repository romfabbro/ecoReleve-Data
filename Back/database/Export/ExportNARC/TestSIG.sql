SELECT F.[indID]
     ,F.[staDate]
	  ,N.[staDate]
      ,F.[CurrentPTT]
	  ,N.[CurrentPTT]
      ,F.[PTT@Station]
	  ,N.[PTT@Station]
      --,F.[PTTModel@Station]
	 -- ,N.[PTTModel@Station]
     ,F.[MonitoringStatus@Station]
	 ,N.[MonitoringStatus@Station]
      ,F.[SurveyType@Station]
	  ,N.[SurveyType@Station]
      ,F.[Origin]
	  ,N.[Origin]
      ,F.[Sex]
	  ,N.[Sex]
      ,F.[Age]
	  ,N.[Age]
      --,F.[CurrentIndividualStatus]
      ,F.[CurrentSurveyType]
	  ,N.[CurrentSurveyType]
      ,F.[CurrentMonitoringStatus]
	  ,N.[CurrentMonitoringStatus]
      --,F.[staID]
      ,F.[staType]
	  ,N.[staType]
      ,F.[LAT]
	  ,N.[LAT]
      ,F.[LON]
	  ,N.[LON]
      ,F.[Precision]
	  ,N.[Precision]
      ,F.[ELE]
	  ,N.[ELE]
      --,F.[RelPlace]
      --,F.[RelCountry]
      ,F.[RelYear]
	  ,N.[RelYear]
      ,F.[RelDate]
	  ,N.[RelDate]
      ,F.[ReleaseRingCode]
	  ,N.[ReleaseRingCode]
      ,F.[SpecieName]
	  ,N.[SpecieName]
      ,F.[DeathDate]
	  ,N.DeathDate
	   from 
(SELECT [indID]
      ,convert(varchar,[CurrentPTT]) [CurrentPTT]
      ,convert(varchar,[PTT@Station]) [PTT@Station]
     -- ,[PTTModel@Station]
     ,[MonitoringStatus@Station]
      ,[SurveyType@Station]
      ,[Origin]
      ,[Sex]
      ,[Age]
      --,[CurrentIndividualStatus]
      ,[CurrentSurveyType]
      ,[CurrentMonitoringStatus]
      --,[staID]
      ,[staType]
      ,[staDate]
      ,[LAT]
      ,[LON]
      ,[Precision]
      ,[ELE]
      --,[RelPlace]
      --,[RelCountry]
      ,[RelYear]
      ,[RelDate]
      ,[ReleaseRingCode]
      ,[SpecieName]
      ,[DeathDate]
  FROM [GIS_AllStations_PTTBirds_With_FirstRelCapData_old]
  where indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
  EXCEPT
  SELECT 
   [indID]
      ,convert(varchar,[CurrentPTT]) [CurrentPTT]
      ,convert(varchar,[PTT@Station]) [PTT@Station]
      --,[PTTModel@Station]
     ,[MonitoringStatus@Station]
      ,[SurveyType@Station]
      ,[Origin]
      ,[Sex]
      ,[Age]
      --,[CurrentIndividualStatus]
      ,[CurrentSurveyType]
      ,[CurrentMonitoringStatus]
      --,[staID]
      ,[staType]
      ,[staDate]
      ,[LAT]
      ,[LON]
      ,[Precision]
      ,[ELE]
      --,[RelPlace]
      --,[RelCountry]
      ,[RelYear]
      ,[RelDate]
      ,[ReleaseRingCode]
      ,[SpecieName]
      ,[DeathDate]
  FROM [GIS_AllStations_PTTBirds_With_FirstRelCapData]
  where indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
 )
  F LEFT JOIN [EcoReleve_Export_NARC].[dbo].[GIS_AllStations_PTTBirds_With_FirstRelCapData] N ON F.[indID] = n.[indID] and F.staDate = n.StaDate
  where F.indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
  order by F.staDate





  

SELECT F.[indID]
	 ,F.[staDate]
	  ,N.[staDate]
      ,F.[CurrentPTT]
	  ,N.[CurrentPTT]
      ,F.[PTT@Station]
	  ,N.[PTT@Station]
      --,F.[PTTModel@Station]
	 -- ,N.[PTTModel@Station]
     ,F.[MonitoringStatus@Station]
	 ,N.[MonitoringStatus@Station]
      ,F.[SurveyType@Station]
	  ,N.[SurveyType@Station]
      ,F.[Origin]
	  ,N.[Origin]
      ,F.[Sex]
	  ,N.[Sex]
      ,F.[Age]
	  ,N.[Age]
      --,F.[CurrentIndividualStatus]
      ,F.[CurrentSurveyType]
	  ,N.[CurrentSurveyType]
      ,F.[CurrentMonitoringStatus]
	  ,N.[CurrentMonitoringStatus]
      --,F.[staID]
      ,F.[staType]
	  ,N.[staType]
      ,F.[staDate]
	  ,N.[staDate]
      ,F.[LAT]
	  ,N.[LAT]
      ,F.[LON]
	  ,N.[LON]
      ,F.[Precision]
	  ,N.[Precision]
      ,F.[ELE]
	  ,N.[ELE]
      --,F.[RelPlace]
      --,F.[RelCountry]
      ,F.[RelYear]
	  ,N.[RelYear]
      ,F.[RelDate]
	  ,N.[RelDate]
      ,F.[ReleaseRingCode]
	  ,N.[ReleaseRingCode]
      ,F.[SpecieName]
	  ,N.[SpecieName]
      ,F.[DeathDate]
	  ,N.DeathDate
	   from 
(SELECT [indID]
      ,convert(varchar,[CurrentPTT]) [CurrentPTT]
      ,convert(varchar,[PTT@Station]) [PTT@Station]
     -- ,[PTTModel@Station]
     ,[MonitoringStatus@Station]
      ,[SurveyType@Station]
      ,[Origin]
      ,[Sex]
      ,[Age]
      --,[CurrentIndividualStatus]
      ,[CurrentSurveyType]
      ,[CurrentMonitoringStatus]
      --,[staID]
      ,[staType]
      ,[staDate]
      ,[LAT]
      ,[LON]
      ,[Precision]
      ,[ELE]
      --,[RelPlace]
      --,[RelCountry]
      ,[RelYear]
      ,[RelDate]
      ,[ReleaseRingCode]
      ,[SpecieName]
      ,[DeathDate]
  FROM [GIS_AllStations_PTTBirds_With_FirstRelCapData]
  where indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
  EXCEPT
  SELECT 
   [indID]
      ,convert(varchar,[CurrentPTT]) [CurrentPTT]
      ,convert(varchar,[PTT@Station]) [PTT@Station]
      --,[PTTModel@Station]
     ,[MonitoringStatus@Station]
      ,[SurveyType@Station]
      ,[Origin]
      ,[Sex]
      ,[Age]
      --,[CurrentIndividualStatus]
      ,[CurrentSurveyType]
      ,[CurrentMonitoringStatus]
      --,[staID]
      ,[staType]
      ,[staDate]
      ,[LAT]
      ,[LON]
      ,[Precision]
      ,[ELE]
      --,[RelPlace]
      --,[RelCountry]
      ,[RelYear]
      ,[RelDate]
      ,[ReleaseRingCode]
      ,[SpecieName]
      ,[DeathDate]
  FROM [GIS_AllStations_PTTBirds_With_FirstRelCapData_old]
  where indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
 )
  F LEFT JOIN [EcoReleve_Export_NARC].[dbo].[GIS_AllStations_PTTBirds_With_FirstRelCapData_old] N ON F.[indID] = n.[indID] and F.staDate = n.StaDate
  where F.indid in (1,2,3,4,4631118,4631119,4631120,4631121,4631122,5459,33,81)
  order by F.indID,F.staDate

