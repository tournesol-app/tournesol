# VideoRatingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**videoRatingStatistics**](VideoRatingsApi.md#videoRatingStatistics) | **GET** /api/v2/video_ratings/video_rating_statistics/ | 
[**videoRatingsList**](VideoRatingsApi.md#videoRatingsList) | **GET** /api/v2/video_ratings/ | 
[**videoRatingsRetrieve**](VideoRatingsApi.md#videoRatingsRetrieve) | **GET** /api/v2/video_ratings/{id}/ | 


<a name="videoRatingStatistics"></a>
# **videoRatingStatistics**
> PaginatedVideoRatingsStatisticsSerializerV2List videoRatingStatistics(backfireRisk, betterHabits, diversityInclusion, engaging, entertainingRelaxing, importance, laymanFriendly, limit, offset, pedagogy, reliability, video, videoVideoId)



    Get statistical data on video ratings.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfireRisk** | **Float**| Resilience to backfiring risks [preference override] | [optional] [default to null]
 **betterHabits** | **Float**| Encourages better habits [preference override] | [optional] [default to null]
 **diversityInclusion** | **Float**| Diversity and Inclusion [preference override] | [optional] [default to null]
 **engaging** | **Float**| Engaging and thought-provoking [preference override] | [optional] [default to null]
 **entertainingRelaxing** | **Float**| Entertaining and relaxing [preference override] | [optional] [default to null]
 **importance** | **Float**| Important and actionable [preference override] | [optional] [default to null]
 **laymanFriendly** | **Float**| Layman-friendly [preference override] | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **pedagogy** | **Float**| Clear and pedagogical [preference override] | [optional] [default to null]
 **reliability** | **Float**| Reliable and not misleading [preference override] | [optional] [default to null]
 **video** | **String**| video | [optional] [default to null]
 **videoVideoId** | **String**| video__video_id | [optional] [default to null]

### Return type

[**PaginatedVideoRatingsStatisticsSerializerV2List**](..//Models/PaginatedVideoRatingsStatisticsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoRatingsList"></a>
# **videoRatingsList**
> PaginatedVideoRatingsSerializerV2List videoRatingsList(limit, offset, video, videoVideoId)



    Get my video ratings (predictions of my algorithmic representative)

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **video** | **String**| video | [optional] [default to null]
 **videoVideoId** | **String**| video__video_id | [optional] [default to null]

### Return type

[**PaginatedVideoRatingsSerializerV2List**](..//Models/PaginatedVideoRatingsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoRatingsRetrieve"></a>
# **videoRatingsRetrieve**
> VideoRatingsSerializerV2 videoRatingsRetrieve(id)



    Get one video rating (predictions of my algorithmic representative)

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video rating. | [default to null]

### Return type

[**VideoRatingsSerializerV2**](..//Models/VideoRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

