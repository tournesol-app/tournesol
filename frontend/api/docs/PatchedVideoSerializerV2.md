# TournesolApi.PatchedVideoSerializerV2

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Number** |  | [optional] [readonly] 
**videoId** | **String** | Video ID from YouTube URL | [optional] 
**score** | **Number** | Computed video score. | [optional] [readonly] [default to 0.0]
**name** | **String** | Video Title | [optional] [readonly] 
**duration** | **String** | Video Duration | [optional] [readonly] 
**language** | **String** | Language as str. | [optional] [readonly] 
**publicationDate** | **Date** | When the video was published | [optional] [readonly] 
**views** | **Number** | Number of views | [optional] [readonly] 
**uploader** | **String** | Name of the channel (uploader) | [optional] [readonly] 
**scorePreferencesTerm** | **Number** | Computed video score [preferences]. | [optional] [readonly] [default to 0.0]
**scoreSearchTerm** | **Number** | Computed video score [search]. | [optional] [readonly] [default to 0.0]
**ratingNExperts** | **Number** | Number of experts in ratings | [optional] [readonly] 
**ratingNRatings** | **Number** | Number of ratings | [optional] [readonly] 
**nReports** | **Number** | Number of times video was reported | [optional] [readonly] 
**publicExperts** | [**[UserInformationSerializerNameOnly]**](UserInformationSerializerNameOnly.md) | First 10 public contributors | [optional] [readonly] 
**nPublicExperts** | **Number** | Number of public contributors | [optional] [readonly] 
**nPrivateExperts** | **Number** | Number private contributors | [optional] [readonly] 
**paretoOptimal** | **Boolean** | Is this video pareto-optimal? | [optional] [readonly] 
**reliability** | **Number** | Reliability | [optional] [readonly] 
**importance** | **Number** | Importance | [optional] [readonly] 
**engaging** | **Number** | Engaging | [optional] [readonly] 
**pedagogy** | **Number** | Pedagogy | [optional] [readonly] 
**laymanFriendly** | **Number** | Layman-friendly | [optional] [readonly] 
**diversityInclusion** | **Number** | Diversity and Inclusion | [optional] [readonly] 
**backfireRisk** | **Number** | Resilience to backfiring risks | [optional] [readonly] 


