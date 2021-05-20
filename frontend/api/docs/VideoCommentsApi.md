# TournesolApi.VideoCommentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiV2VideoCommentsSetMark**](VideoCommentsApi.md#apiV2VideoCommentsSetMark) | **POST** /api/v2/video_comments/{id}/set_mark/ | 
[**videoCommentsCreate**](VideoCommentsApi.md#videoCommentsCreate) | **POST** /api/v2/video_comments/ | 
[**videoCommentsList**](VideoCommentsApi.md#videoCommentsList) | **GET** /api/v2/video_comments/ | 
[**videoCommentsPartialUpdate**](VideoCommentsApi.md#videoCommentsPartialUpdate) | **PATCH** /api/v2/video_comments/{id}/ | 
[**videoCommentsRetrieve**](VideoCommentsApi.md#videoCommentsRetrieve) | **GET** /api/v2/video_comments/{id}/ | 
[**videoCommentsUpdate**](VideoCommentsApi.md#videoCommentsUpdate) | **PUT** /api/v2/video_comments/{id}/ | 



## apiV2VideoCommentsSetMark

> VideoCommentsSerializerV2 apiV2VideoCommentsSetMark(action, id, marker)



Mark a comment with a flag (like/dislike/red flag).

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let action = "action_example"; // String | Delete or add the marker, one of ['add', 'delete', 'toggle']
let id = 56; // Number | A unique integer value identifying this video comment.
let marker = "marker_example"; // String | The marker to set, one of ['votes_plus', 'votes_minus', 'red_flags']
apiInstance.apiV2VideoCommentsSetMark(action, id, marker, (error, data, response) => {
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
 **action** | **String**| Delete or add the marker, one of [&#39;add&#39;, &#39;delete&#39;, &#39;toggle&#39;] | 
 **id** | **Number**| A unique integer value identifying this video comment. | 
 **marker** | **String**| The marker to set, one of [&#39;votes_plus&#39;, &#39;votes_minus&#39;, &#39;red_flags&#39;] | 

### Return type

[**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoCommentsCreate

> VideoCommentsSerializerV2 videoCommentsCreate(videoCommentsSerializerV2)



Comment on a video

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let videoCommentsSerializerV2 = new TournesolApi.VideoCommentsSerializerV2(); // VideoCommentsSerializerV2 | 
apiInstance.videoCommentsCreate(videoCommentsSerializerV2, (error, data, response) => {
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
 **videoCommentsSerializerV2** | [**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)|  | 

### Return type

[**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## videoCommentsList

> PaginatedVideoCommentsSerializerV2List videoCommentsList(opts)



List and filter comments

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let opts = {
  'backfireRisk': "backfireRisk_example", // String | backfire_risk
  'betterHabits': "betterHabits_example", // String | better_habits
  'comment': "comment_example", // String | comment
  'diversityInclusion': "diversityInclusion_example", // String | diversity_inclusion
  'engaging': "engaging_example", // String | engaging
  'entertainingRelaxing': "entertainingRelaxing_example", // String | entertaining_relaxing
  'importance': "importance_example", // String | importance
  'largelyRecommended': "largelyRecommended_example", // String | largely_recommended
  'laymanFriendly': "laymanFriendly_example", // String | layman_friendly
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'parentComment': "parentComment_example", // String | parent_comment
  'pedagogy': "pedagogy_example", // String | pedagogy
  'reliability': "reliability_example", // String | reliability
  'userUserUsername': "userUserUsername_example", // String | user__user__username
  'videoVideoId': "videoVideoId_example" // String | video__video_id
};
apiInstance.videoCommentsList(opts, (error, data, response) => {
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
 **backfireRisk** | **String**| backfire_risk | [optional] 
 **betterHabits** | **String**| better_habits | [optional] 
 **comment** | **String**| comment | [optional] 
 **diversityInclusion** | **String**| diversity_inclusion | [optional] 
 **engaging** | **String**| engaging | [optional] 
 **entertainingRelaxing** | **String**| entertaining_relaxing | [optional] 
 **importance** | **String**| importance | [optional] 
 **largelyRecommended** | **String**| largely_recommended | [optional] 
 **laymanFriendly** | **String**| layman_friendly | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **parentComment** | **String**| parent_comment | [optional] 
 **pedagogy** | **String**| pedagogy | [optional] 
 **reliability** | **String**| reliability | [optional] 
 **userUserUsername** | **String**| user__user__username | [optional] 
 **videoVideoId** | **String**| video__video_id | [optional] 

### Return type

[**PaginatedVideoCommentsSerializerV2List**](PaginatedVideoCommentsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoCommentsPartialUpdate

> VideoCommentsSerializerV2 videoCommentsPartialUpdate(id, opts)



Change some fields in a comment

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let id = 56; // Number | A unique integer value identifying this video comment.
let opts = {
  'patchedVideoCommentsSerializerV2': new TournesolApi.PatchedVideoCommentsSerializerV2() // PatchedVideoCommentsSerializerV2 | 
};
apiInstance.videoCommentsPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video comment. | 
 **patchedVideoCommentsSerializerV2** | [**PatchedVideoCommentsSerializerV2**](PatchedVideoCommentsSerializerV2.md)|  | [optional] 

### Return type

[**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## videoCommentsRetrieve

> VideoCommentsSerializerV2 videoCommentsRetrieve(id)



Get one comment

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let id = 56; // Number | A unique integer value identifying this video comment.
apiInstance.videoCommentsRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video comment. | 

### Return type

[**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoCommentsUpdate

> VideoCommentsSerializerV2 videoCommentsUpdate(id, videoCommentsSerializerV2)



Change all fields in a comment

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

let apiInstance = new TournesolApi.VideoCommentsApi();
let id = 56; // Number | A unique integer value identifying this video comment.
let videoCommentsSerializerV2 = new TournesolApi.VideoCommentsSerializerV2(); // VideoCommentsSerializerV2 | 
apiInstance.videoCommentsUpdate(id, videoCommentsSerializerV2, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video comment. | 
 **videoCommentsSerializerV2** | [**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)|  | 

### Return type

[**VideoCommentsSerializerV2**](VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

