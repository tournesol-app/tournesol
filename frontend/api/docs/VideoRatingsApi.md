# TournesolApi.VideoRatingsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**videoRatingStatistics**](VideoRatingsApi.md#videoRatingStatistics) | **GET** /api/v2/video_ratings/video_rating_statistics/ | 
[**videoRatingsList**](VideoRatingsApi.md#videoRatingsList) | **GET** /api/v2/video_ratings/ | 
[**videoRatingsRetrieve**](VideoRatingsApi.md#videoRatingsRetrieve) | **GET** /api/v2/video_ratings/{id}/ | 



## videoRatingStatistics

> PaginatedVideoRatingsStatisticsSerializerV2List videoRatingStatistics(opts)



Get statistical data on video ratings.

### Example

```javascript
import TournesolApi from 'tournesol_api';
let defaultClient = TournesolApi.ApiClient.instance;
// Configure API key authorization: cookieAuth
let cookieAuth = defaultClient.authentications['cookieAuth'];
cookieAuth.apiKey = 'YOUR API KEY';
// Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
//cookieAuth.apiKeyPrefix = 'Token';
// Configure Bearer (Token) access token for authorization: tokenAuth
let tokenAuth = defaultClient.authentications['tokenAuth'];
tokenAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new TournesolApi.VideoRatingsApi();
let opts = {
  'backfireRisk': 3.4, // Number | Resilience to backfiring risks [preference override]
  'betterHabits': 3.4, // Number | Encourages better habits [preference override]
  'diversityInclusion': 3.4, // Number | Diversity and Inclusion [preference override]
  'engaging': 3.4, // Number | Engaging and thought-provoking [preference override]
  'entertainingRelaxing': 3.4, // Number | Entertaining and relaxing [preference override]
  'importance': 3.4, // Number | Important and actionable [preference override]
  'largelyRecommended': 3.4, // Number | Should be largely recommended [preference override]
  'laymanFriendly': 3.4, // Number | Layman-friendly [preference override]
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'pedagogy': 3.4, // Number | Clear and pedagogical [preference override]
  'reliability': 3.4, // Number | Reliable and not misleading [preference override]
  'video': "video_example", // String | video
  'videoVideoId': "videoVideoId_example" // String | video__video_id
};
apiInstance.videoRatingStatistics(opts, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfireRisk** | **Number**| Resilience to backfiring risks [preference override] | [optional] 
 **betterHabits** | **Number**| Encourages better habits [preference override] | [optional] 
 **diversityInclusion** | **Number**| Diversity and Inclusion [preference override] | [optional] 
 **engaging** | **Number**| Engaging and thought-provoking [preference override] | [optional] 
 **entertainingRelaxing** | **Number**| Entertaining and relaxing [preference override] | [optional] 
 **importance** | **Number**| Important and actionable [preference override] | [optional] 
 **largelyRecommended** | **Number**| Should be largely recommended [preference override] | [optional] 
 **laymanFriendly** | **Number**| Layman-friendly [preference override] | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **pedagogy** | **Number**| Clear and pedagogical [preference override] | [optional] 
 **reliability** | **Number**| Reliable and not misleading [preference override] | [optional] 
 **video** | **String**| video | [optional] 
 **videoVideoId** | **String**| video__video_id | [optional] 

### Return type

[**PaginatedVideoRatingsStatisticsSerializerV2List**](PaginatedVideoRatingsStatisticsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoRatingsList

> PaginatedVideoRatingsSerializerV2List videoRatingsList(opts)



Get my video ratings (predictions of my algorithmic representative)

### Example

```javascript
import TournesolApi from 'tournesol_api';
let defaultClient = TournesolApi.ApiClient.instance;
// Configure API key authorization: cookieAuth
let cookieAuth = defaultClient.authentications['cookieAuth'];
cookieAuth.apiKey = 'YOUR API KEY';
// Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
//cookieAuth.apiKeyPrefix = 'Token';
// Configure Bearer (Token) access token for authorization: tokenAuth
let tokenAuth = defaultClient.authentications['tokenAuth'];
tokenAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new TournesolApi.VideoRatingsApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'video': "video_example", // String | video
  'videoVideoId': "videoVideoId_example" // String | video__video_id
};
apiInstance.videoRatingsList(opts, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **video** | **String**| video | [optional] 
 **videoVideoId** | **String**| video__video_id | [optional] 

### Return type

[**PaginatedVideoRatingsSerializerV2List**](PaginatedVideoRatingsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoRatingsRetrieve

> VideoRatingsSerializerV2 videoRatingsRetrieve(id)



Get one video rating (predictions of my algorithmic representative)

### Example

```javascript
import TournesolApi from 'tournesol_api';
let defaultClient = TournesolApi.ApiClient.instance;
// Configure API key authorization: cookieAuth
let cookieAuth = defaultClient.authentications['cookieAuth'];
cookieAuth.apiKey = 'YOUR API KEY';
// Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
//cookieAuth.apiKeyPrefix = 'Token';
// Configure Bearer (Token) access token for authorization: tokenAuth
let tokenAuth = defaultClient.authentications['tokenAuth'];
tokenAuth.accessToken = "YOUR ACCESS TOKEN"

let apiInstance = new TournesolApi.VideoRatingsApi();
let id = 56; // Number | A unique integer value identifying this video rating.
apiInstance.videoRatingsRetrieve(id, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Number**| A unique integer value identifying this video rating. | 

### Return type

[**VideoRatingsSerializerV2**](VideoRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

