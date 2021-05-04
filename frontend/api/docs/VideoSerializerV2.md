# TournesolApi.VideoSerializerV2

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Number** |  | [readonly] 
**videoId** | **String** | Video ID from YouTube URL, matches ^[A-Za-z0-9-_]+$ | 
**score** | **Number** | Computed video score. | [readonly] [default to 0.0]
**name** | **String** | Video Title | [readonly] 
**duration** | **String** | Video Duration | [readonly] 
**language** | **String** | Language as str. | [readonly] 
**publicationDate** | **Date** | When the video was published | [readonly] 
**views** | **Number** | Number of views | [readonly] 
**uploader** | **String** | Name of the channel (uploader) | [readonly] 
**scorePreferencesTerm** | **Number** | Computed video score [preferences]. | [readonly] [default to 0.0]
**scoreSearchTerm** | **Number** | Computed video score [search]. | [readonly] [default to 0.0]
**ratingNExperts** | **Number** | Number of experts in ratings | [readonly] 
**ratingNRatings** | **Number** | Number of ratings | [readonly] 
**publicExperts** | [**[UserInformationSerializerNameOnly]**](UserInformationSerializerNameOnly.md) | First 10 public contributors | [readonly] 
**nPublicExperts** | **Number** | Number of public contributors | [readonly] 
**nPrivateExperts** | **Number** | Number private contributors | [readonly] 
**paretoOptimal** | **Boolean** | Is this video pareto-optimal? | [readonly] 
**tournesolScore** | **Number** | The total Tournesol score with uniform preferences (value&#x3D;50.0) | [readonly] [default to 0.0]
**reliability** | **Number** | Reliable and not misleading | [readonly] 
**importance** | **Number** | Important and actionable | [readonly] 
**engaging** | **Number** | Engaging and thought-provoking | [readonly] 
**pedagogy** | **Number** | Clear and pedagogical | [readonly] 
**laymanFriendly** | **Number** | Layman-friendly | [readonly] 
**diversityInclusion** | **Number** | Diversity and Inclusion | [readonly] 
**backfireRisk** | **Number** | Resilience to backfiring risks | [readonly] 
**betterHabits** | **Number** | Encourages better habits | [readonly] 
**entertainingRelaxing** | **Number** | Entertaining and relaxing | [readonly] 


