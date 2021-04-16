# ExpertRatingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiV2ExpertRatingsDoubleDown**](ExpertRatingsApi.md#apiV2ExpertRatingsDoubleDown) | **PATCH** /api/v2/expert_ratings/double_down/ | 
[**apiV2ExpertRatingsSampleVideo**](ExpertRatingsApi.md#apiV2ExpertRatingsSampleVideo) | **GET** /api/v2/expert_ratings/sample_video/ | 
[**apiV2ExpertRatingsShowInconsistencies**](ExpertRatingsApi.md#apiV2ExpertRatingsShowInconsistencies) | **GET** /api/v2/expert_ratings/inconsistencies/ | 
[**disagreements**](ExpertRatingsApi.md#disagreements) | **GET** /api/v2/expert_ratings/disagreements/ | 
[**expertRatingsByVideoIdsPartialUpdate**](ExpertRatingsApi.md#expertRatingsByVideoIdsPartialUpdate) | **PATCH** /api/v2/expert_ratings/by_video_ids/ | 
[**expertRatingsByVideoIdsRetrieve**](ExpertRatingsApi.md#expertRatingsByVideoIdsRetrieve) | **GET** /api/v2/expert_ratings/by_video_ids/ | 
[**expertRatingsCreate**](ExpertRatingsApi.md#expertRatingsCreate) | **POST** /api/v2/expert_ratings/ | 
[**expertRatingsList**](ExpertRatingsApi.md#expertRatingsList) | **GET** /api/v2/expert_ratings/ | 
[**expertRatingsOnlineByVideoIdsPartialUpdate**](ExpertRatingsApi.md#expertRatingsOnlineByVideoIdsPartialUpdate) | **PATCH** /api/v2/expert_ratings/online_by_video_ids/ | 
[**expertRatingsOnlineByVideoIdsRetrieve**](ExpertRatingsApi.md#expertRatingsOnlineByVideoIdsRetrieve) | **GET** /api/v2/expert_ratings/online_by_video_ids/ | 
[**expertRatingsPartialUpdate**](ExpertRatingsApi.md#expertRatingsPartialUpdate) | **PATCH** /api/v2/expert_ratings/{id}/ | 
[**expertRatingsRetrieve**](ExpertRatingsApi.md#expertRatingsRetrieve) | **GET** /api/v2/expert_ratings/{id}/ | 
[**expertRatingsSampleFirstVideoRetrieve**](ExpertRatingsApi.md#expertRatingsSampleFirstVideoRetrieve) | **GET** /api/v2/expert_ratings/sample_first_video/ | 
[**expertRatingsSamplePopularVideoRetrieve**](ExpertRatingsApi.md#expertRatingsSamplePopularVideoRetrieve) | **GET** /api/v2/expert_ratings/sample_popular_video/ | 
[**expertRatingsSampleVideoWithOtherRetrieve**](ExpertRatingsApi.md#expertRatingsSampleVideoWithOtherRetrieve) | **GET** /api/v2/expert_ratings/sample_video_with_other/ | 
[**expertRatingsSkipVideoPartialUpdate**](ExpertRatingsApi.md#expertRatingsSkipVideoPartialUpdate) | **PATCH** /api/v2/expert_ratings/skip_video/ | 
[**expertRatingsUpdate**](ExpertRatingsApi.md#expertRatingsUpdate) | **PUT** /api/v2/expert_ratings/{id}/ | 
[**registerSliderChange**](ExpertRatingsApi.md#registerSliderChange) | **POST** /api/v2/expert_ratings/register_slider_change/ | 


<a name="apiV2ExpertRatingsDoubleDown"></a>
# **apiV2ExpertRatingsDoubleDown**
> ExpertRatingsSerializerV2 apiV2ExpertRatingsDoubleDown(feature, videoLeft, videoRight)



    Double the weight of one of the ratings on one of the features.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature** | **String**| The feature to double down the weight on | [default to null]
 **videoLeft** | **String**| Left video (can be either v1 or v2) | [default to null]
 **videoRight** | **String**| Right video (can be either v1 or v2) | [default to null]

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="apiV2ExpertRatingsSampleVideo"></a>
# **apiV2ExpertRatingsSampleVideo**
> VideoSerializerV2 apiV2ExpertRatingsSampleVideo(onlyRated)



    Sample a video to rate.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **onlyRated** | **Boolean**| Only sample videos already rated by the expert | [optional] [default to null]

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="apiV2ExpertRatingsShowInconsistencies"></a>
# **apiV2ExpertRatingsShowInconsistencies**
> PaginatedInconsistenciesList apiV2ExpertRatingsShowInconsistencies(limit, offset, video1, video2, videoVideoId)



    Get inconsistencies in Expert Ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **video1** | **String**| First video in the rating (fixed order) | [optional] [default to null]
 **video2** | **String**| Second video in the rating (fixed order) | [optional] [default to null]
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] [default to null]

### Return type

[**PaginatedInconsistenciesList**](..//Models/PaginatedInconsistenciesList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="disagreements"></a>
# **disagreements**
> PaginatedDisagreementList disagreements(limit, offset, video1, video2, videoVideoId)



    Get disagreements in Expert Ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **video1** | **String**| First video in the rating (fixed order) | [optional] [default to null]
 **video2** | **String**| Second video in the rating (fixed order) | [optional] [default to null]
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] [default to null]

### Return type

[**PaginatedDisagreementList**](..//Models/PaginatedDisagreementList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsByVideoIdsPartialUpdate"></a>
# **expertRatingsByVideoIdsPartialUpdate**
> ExpertRatingsSerializerV2 expertRatingsByVideoIdsPartialUpdate(videoLeft, videoRight, forceSetIds, patchedExpertRatingsSerializerV2)



    Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoLeft** | **String**| Left video (can be either v1 or v2) | [default to null]
 **videoRight** | **String**| Right video (can be either v1 or v2) | [default to null]
 **forceSetIds** | **Boolean**| Force set video_1 and video_2 (in DB order -- confusing, disabled by-default) | [optional] [default to null]
 **patchedExpertRatingsSerializerV2** | [**PatchedExpertRatingsSerializerV2**](..//Models/PatchedExpertRatingsSerializerV2.md)|  | [optional]

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="expertRatingsByVideoIdsRetrieve"></a>
# **expertRatingsByVideoIdsRetrieve**
> ExpertRatingsSerializerV2 expertRatingsByVideoIdsRetrieve(videoLeft, videoRight, forceSetIds)



    Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoLeft** | **String**| Left video (can be either v1 or v2) | [default to null]
 **videoRight** | **String**| Right video (can be either v1 or v2) | [default to null]
 **forceSetIds** | **Boolean**| Force set video_1 and video_2 (in DB order -- confusing, disabled by-default) | [optional] [default to null]

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsCreate"></a>
# **expertRatingsCreate**
> ExpertRatingsSerializerV2 expertRatingsCreate(expertRatingsSerializerV2)



    Rate two videos

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **expertRatingsSerializerV2** | [**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)|  |

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="expertRatingsList"></a>
# **expertRatingsList**
> PaginatedExpertRatingsSerializerV2List expertRatingsList(limit, offset, video1, video2, videoVideoId)



    List my own expert ratings

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **video1** | **String**| First video in the rating (fixed order) | [optional] [default to null]
 **video2** | **String**| Second video in the rating (fixed order) | [optional] [default to null]
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] [default to null]

### Return type

[**PaginatedExpertRatingsSerializerV2List**](..//Models/PaginatedExpertRatingsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsOnlineByVideoIdsPartialUpdate"></a>
# **expertRatingsOnlineByVideoIdsPartialUpdate**
> OnlineResponse expertRatingsOnlineByVideoIdsPartialUpdate(feature, newValue, videoLeft, videoRight, addDebugInfo)



    Do online updates on ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature** | **String**| The feature to update | [default to null]
 **newValue** | **Float**| New value for the feature in 0..100.0 | [default to null]
 **videoLeft** | **String**| Left video (can be either v1 or v2) | [default to null]
 **videoRight** | **String**| Right video (can be either v1 or v2) | [default to null]
 **addDebugInfo** | **Boolean**| Return also a dict with information | [optional] [default to null]

### Return type

[**OnlineResponse**](..//Models/OnlineResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsOnlineByVideoIdsRetrieve"></a>
# **expertRatingsOnlineByVideoIdsRetrieve**
> OnlineResponse expertRatingsOnlineByVideoIdsRetrieve(feature, newValue, videoLeft, videoRight, addDebugInfo)



    Do online updates on ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **feature** | **String**| The feature to update | [default to null]
 **newValue** | **Float**| New value for the feature in 0..100.0 | [default to null]
 **videoLeft** | **String**| Left video (can be either v1 or v2) | [default to null]
 **videoRight** | **String**| Right video (can be either v1 or v2) | [default to null]
 **addDebugInfo** | **Boolean**| Return also a dict with information | [optional] [default to null]

### Return type

[**OnlineResponse**](..//Models/OnlineResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsPartialUpdate"></a>
# **expertRatingsPartialUpdate**
> ExpertRatingsSerializerV2 expertRatingsPartialUpdate(id, patchedExpertRatingsSerializerV2)



    Change some fields in a rating

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this expert rating. | [default to null]
 **patchedExpertRatingsSerializerV2** | [**PatchedExpertRatingsSerializerV2**](..//Models/PatchedExpertRatingsSerializerV2.md)|  | [optional]

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="expertRatingsRetrieve"></a>
# **expertRatingsRetrieve**
> ExpertRatingsSerializerV2 expertRatingsRetrieve(id)



    Set and get expert ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this expert rating. | [default to null]

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsSampleFirstVideoRetrieve"></a>
# **expertRatingsSampleFirstVideoRetrieve**
> VideoSerializerV2 expertRatingsSampleFirstVideoRetrieve(videoExclude)



    Sample a video to rate.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoExclude** | **String**| Exclude a video ID from consideration | [optional] [default to null]

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsSamplePopularVideoRetrieve"></a>
# **expertRatingsSamplePopularVideoRetrieve**
> VideoSerializerV2 expertRatingsSamplePopularVideoRetrieve(noRateLater)



    Sample a popular video.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **noRateLater** | **Boolean**| Do not show videos in rate later list | [optional] [default to null]

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsSampleVideoWithOtherRetrieve"></a>
# **expertRatingsSampleVideoWithOtherRetrieve**
> VideoSerializerV2 expertRatingsSampleVideoWithOtherRetrieve(videoOther)



    Sample a video to rate.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoOther** | **String**| Other video_id being rated | [default to null]

### Return type

[**VideoSerializerV2**](..//Models/VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="expertRatingsSkipVideoPartialUpdate"></a>
# **expertRatingsSkipVideoPartialUpdate**
> expertRatingsSkipVideoPartialUpdate(patchedVideo)



    Set and get expert ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedVideo** | [**List**](..//Models/PatchedVideo.md)|  |

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined

<a name="expertRatingsUpdate"></a>
# **expertRatingsUpdate**
> ExpertRatingsSerializerV2 expertRatingsUpdate(id, expertRatingsSerializerV2)



    Change all fields in a rating

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this expert rating. | [default to null]
 **expertRatingsSerializerV2** | [**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)|  |

### Return type

[**ExpertRatingsSerializerV2**](..//Models/ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="registerSliderChange"></a>
# **registerSliderChange**
> SliderChangeSerializerV2 registerSliderChange(sliderChangeSerializerV2)



    Register any change in slider values on the rating page.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sliderChangeSerializerV2** | [**SliderChangeSerializerV2**](..//Models/SliderChangeSerializerV2.md)|  |

### Return type

[**SliderChangeSerializerV2**](..//Models/SliderChangeSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

