# VideosApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiV2VideoSearchTournesol**](VideosApi.md#apiV2VideoSearchTournesol) | **GET** /api/v2/videos/search_tournesol/ | 
[**apiV2VideoSearchYoutube**](VideosApi.md#apiV2VideoSearchYoutube) | **GET** /api/v2/videos/search_youtube/ | 
[**myRatingsArePrivate**](VideosApi.md#myRatingsArePrivate) | **GET** /api/v2/videos/my_ratings_are_private/ | 
[**nThanks**](VideosApi.md#nThanks) | **GET** /api/v2/videos/n_thanks/ | 
[**setAllRatingPrivacy**](VideosApi.md#setAllRatingPrivacy) | **PATCH** /api/v2/videos/set_all_rating_privacy/ | 
[**setRatingPrivacy**](VideosApi.md#setRatingPrivacy) | **PATCH** /api/v2/videos/set_rating_privacy/ | 
[**thankContributors**](VideosApi.md#thankContributors) | **PATCH** /api/v2/videos/thank_contributors/ | 
[**videosCreate**](VideosApi.md#videosCreate) | **POST** /api/v2/videos/ | 
[**videosList**](VideosApi.md#videosList) | **GET** /api/v2/videos/ | 
[**videosRatedVideosList**](VideosApi.md#videosRatedVideosList) | **GET** /api/v2/videos/rated_videos/ | 
[**videosRetrieve**](VideosApi.md#videosRetrieve) | **GET** /api/v2/videos/{id}/ | 


<a name="apiV2VideoSearchTournesol"></a>
# **apiV2VideoSearchTournesol**
> PaginatedVideoSerializerV2List apiV2VideoSearchTournesol(backfireRisk, betterHabits, daysAgoGte, daysAgoLte, diversityInclusion, durationGte, durationLte, engaging, entertainingRelaxing, importance, language, laymanFriendly, limit, offset, ordering, pedagogy, reliability, search, searchModel, showAllMyVideos, videoId, viewsGte, viewsLte)



    Search videos using the Tournesol algorithm.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfireRisk** | **Float**| Resilience to backfiring risks [preference override] | [optional] [default to null]
 **betterHabits** | **Float**| Encourages better habits [preference override] | [optional] [default to null]
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] [default to null]
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] [default to null]
 **diversityInclusion** | **Float**| Diversity and Inclusion [preference override] | [optional] [default to null]
 **durationGte** | **String**| duration_gte | [optional] [default to null]
 **durationLte** | **String**| duration_lte | [optional] [default to null]
 **engaging** | **Float**| Engaging and thought-provoking [preference override] | [optional] [default to null]
 **entertainingRelaxing** | **Float**| Entertaining and relaxing [preference override] | [optional] [default to null]
 **importance** | **Float**| Important and actionable [preference override] | [optional] [default to null]
 **language** | **String**| language | [optional] [default to null]
 **laymanFriendly** | **Float**| Layman-friendly [preference override] | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **ordering** | **String**| Which field to use when ordering the results. | [optional] [default to null]
 **pedagogy** | **Float**| Clear and pedagogical [preference override] | [optional] [default to null]
 **reliability** | **Float**| Reliable and not misleading [preference override] | [optional] [default to null]
 **search** | **String**| Search string | [optional] [default to null]
 **searchModel** | **String**| Use this user&#39;s algorithmic representative | [optional] [default to null]
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] [default to null]
 **videoId** | **String**| video_id | [optional] [default to null]
 **viewsGte** | **String**| views_gte | [optional] [default to null]
 **viewsLte** | **String**| views_lte | [optional] [default to null]

### Return type

[**PaginatedVideoSerializerV2List**](..//Models/PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="apiV2VideoSearchYoutube"></a>
# **apiV2VideoSearchYoutube**
> PaginatedVideoSerializerV2List apiV2VideoSearchYoutube(search, daysAgoGte, daysAgoLte, durationGte, durationLte, language, limit, offset, ordering, showAllMyVideos, videoId, viewsGte, viewsLte)



    Search videos using the YouTube algorithm.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search** | **String**| Youtube search phrase | [default to null]
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] [default to null]
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] [default to null]
 **durationGte** | **String**| duration_gte | [optional] [default to null]
 **durationLte** | **String**| duration_lte | [optional] [default to null]
 **language** | **String**| language | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **ordering** | **String**| Which field to use when ordering the results. | [optional] [default to null]
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] [default to null]
 **videoId** | **String**| video_id | [optional] [default to null]
 **viewsGte** | **String**| views_gte | [optional] [default to null]
 **viewsLte** | **String**| views_lte | [optional] [default to null]

### Return type

[**PaginatedVideoSerializerV2List**](..//Models/PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="myRatingsArePrivate"></a>
# **myRatingsArePrivate**
> PrivateOrPublic myRatingsArePrivate(videoId)



    Are my ratings private?

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoId** | **String**| Youtube Video ID | [default to null]

### Return type

[**PrivateOrPublic**](..//Models/PrivateOrPublic.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="nThanks"></a>
# **nThanks**
> NumberOfThanks nThanks(videoId)



    Get number of people I thanked for a video.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoId** | **String**| Youtube Video ID | [default to null]

### Return type

[**NumberOfThanks**](..//Models/NumberOfThanks.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="setAllRatingPrivacy"></a>
# **setAllRatingPrivacy**
> setAllRatingPrivacy(isPublic)



    Set all video rating privacy.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **isPublic** | **Boolean**| Should all ratings be public | [default to null]

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="setRatingPrivacy"></a>
# **setRatingPrivacy**
> setRatingPrivacy(isPublic, videoId)



    Set video rating privacy.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **isPublic** | **Boolean**| Should the rating be public | [default to null]
 **videoId** | **String**| Youtube Video ID | [default to null]

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="thankContributors"></a>
# **thankContributors**
> thankContributors(action, videoId)



    Thank contributors for the video.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **action** | **String**| Set/unset | [default to null] [enum: thank, unthank]
 **videoId** | **String**| Youtube Video ID | [default to null]

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="videosCreate"></a>
# **videosCreate**
> VideoSerializerV2 videosCreate(videoSerializerV2)



    Add a video to the database (without filling the fields) from Youtube

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoSerializerV2** | [**VideoSerializerV2**](..//Models/VideoSerializerV2.md)|  |

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="videosList"></a>
# **videosList**
> PaginatedVideoSerializerV2List videosList(daysAgoGte, daysAgoLte, durationGte, durationLte, language, limit, offset, ordering, search, showAllMyVideos, videoId, viewsGte, viewsLte)



    List all videos with search/filter capability

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] [default to null]
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] [default to null]
 **durationGte** | **String**| duration_gte | [optional] [default to null]
 **durationLte** | **String**| duration_lte | [optional] [default to null]
 **language** | **String**| language | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **ordering** | **String**| Which field to use when ordering the results. | [optional] [default to null]
 **search** | **String**| Search string | [optional] [default to null]
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] [default to null]
 **videoId** | **String**| video_id | [optional] [default to null]
 **viewsGte** | **String**| views_gte | [optional] [default to null]
 **viewsLte** | **String**| views_lte | [optional] [default to null]

### Return type

[**PaginatedVideoSerializerV2List**](..//Models/PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videosRatedVideosList"></a>
# **videosRatedVideosList**
> PaginatedVideoSerializerV2List videosRatedVideosList(daysAgoGte, daysAgoLte, durationGte, durationLte, language, limit, offset, ordering, search, showAllMyVideos, videoId, viewsGte, viewsLte)



    Get videos and search results.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] [default to null]
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] [default to null]
 **durationGte** | **String**| duration_gte | [optional] [default to null]
 **durationLte** | **String**| duration_lte | [optional] [default to null]
 **language** | **String**| language | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **ordering** | **String**| Which field to use when ordering the results. | [optional] [default to null]
 **search** | **String**| Search string | [optional] [default to null]
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] [default to null]
 **videoId** | **String**| video_id | [optional] [default to null]
 **viewsGte** | **String**| views_gte | [optional] [default to null]
 **viewsLte** | **String**| views_lte | [optional] [default to null]

### Return type

[**PaginatedVideoSerializerV2List**](..//Models/PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videosRetrieve"></a>
# **videosRetrieve**
> VideoSerializerV2 videosRetrieve(id)



    Get one video by internal ID

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video. | [default to null]

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

