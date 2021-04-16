# TournesolApi.ExpertRatingsApi

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



## apiV2ExpertRatingsDoubleDown

> ExpertRatingsSerializerV2 apiV2ExpertRatingsDoubleDown(feature, videoLeft, videoRight)



Double the weight of one of the ratings on one of the features.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let feature = "feature_example"; // String | The feature to double down the weight on
let videoLeft = "videoLeft_example"; // String | Left video (can be either v1 or v2)
let videoRight = "videoRight_example"; // String | Right video (can be either v1 or v2)
apiInstance.apiV2ExpertRatingsDoubleDown(feature, videoLeft, videoRight, (error, data, response) => {
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
 **feature** | **String**| The feature to double down the weight on | 
 **videoLeft** | **String**| Left video (can be either v1 or v2) | 
 **videoRight** | **String**| Right video (can be either v1 or v2) | 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## apiV2ExpertRatingsSampleVideo

> VideoSerializerV2 apiV2ExpertRatingsSampleVideo(opts)



Sample a video to rate.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'onlyRated': true // Boolean | Only sample videos already rated by the expert
};
apiInstance.apiV2ExpertRatingsSampleVideo(opts, (error, data, response) => {
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
 **onlyRated** | **Boolean**| Only sample videos already rated by the expert | [optional] 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## apiV2ExpertRatingsShowInconsistencies

> PaginatedInconsistenciesList apiV2ExpertRatingsShowInconsistencies(opts)



Get inconsistencies in Expert Ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'video1': "video1_example", // String | First video in the rating (fixed order)
  'video2': "video2_example", // String | Second video in the rating (fixed order)
  'videoVideoId': "videoVideoId_example" // String | Any video ID (first or second)
};
apiInstance.apiV2ExpertRatingsShowInconsistencies(opts, (error, data, response) => {
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
 **video1** | **String**| First video in the rating (fixed order) | [optional] 
 **video2** | **String**| Second video in the rating (fixed order) | [optional] 
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] 

### Return type

[**PaginatedInconsistenciesList**](PaginatedInconsistenciesList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## disagreements

> PaginatedDisagreementList disagreements(opts)



Get disagreements in Expert Ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'video1': "video1_example", // String | First video in the rating (fixed order)
  'video2': "video2_example", // String | Second video in the rating (fixed order)
  'videoVideoId': "videoVideoId_example" // String | Any video ID (first or second)
};
apiInstance.disagreements(opts, (error, data, response) => {
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
 **video1** | **String**| First video in the rating (fixed order) | [optional] 
 **video2** | **String**| Second video in the rating (fixed order) | [optional] 
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] 

### Return type

[**PaginatedDisagreementList**](PaginatedDisagreementList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsByVideoIdsPartialUpdate

> ExpertRatingsSerializerV2 expertRatingsByVideoIdsPartialUpdate(videoLeft, videoRight, opts)



Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let videoLeft = "videoLeft_example"; // String | Left video (can be either v1 or v2)
let videoRight = "videoRight_example"; // String | Right video (can be either v1 or v2)
let opts = {
  'forceSetIds': true, // Boolean | Force set video_1 and video_2 (in DB order -- confusing, disabled by-default)
  'patchedExpertRatingsSerializerV2': new TournesolApi.PatchedExpertRatingsSerializerV2() // PatchedExpertRatingsSerializerV2 | 
};
apiInstance.expertRatingsByVideoIdsPartialUpdate(videoLeft, videoRight, opts, (error, data, response) => {
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
 **videoLeft** | **String**| Left video (can be either v1 or v2) | 
 **videoRight** | **String**| Right video (can be either v1 or v2) | 
 **forceSetIds** | **Boolean**| Force set video_1 and video_2 (in DB order -- confusing, disabled by-default) | [optional] 
 **patchedExpertRatingsSerializerV2** | [**PatchedExpertRatingsSerializerV2**](PatchedExpertRatingsSerializerV2.md)|  | [optional] 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## expertRatingsByVideoIdsRetrieve

> ExpertRatingsSerializerV2 expertRatingsByVideoIdsRetrieve(videoLeft, videoRight, opts)



Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let videoLeft = "videoLeft_example"; // String | Left video (can be either v1 or v2)
let videoRight = "videoRight_example"; // String | Right video (can be either v1 or v2)
let opts = {
  'forceSetIds': true // Boolean | Force set video_1 and video_2 (in DB order -- confusing, disabled by-default)
};
apiInstance.expertRatingsByVideoIdsRetrieve(videoLeft, videoRight, opts, (error, data, response) => {
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
 **videoLeft** | **String**| Left video (can be either v1 or v2) | 
 **videoRight** | **String**| Right video (can be either v1 or v2) | 
 **forceSetIds** | **Boolean**| Force set video_1 and video_2 (in DB order -- confusing, disabled by-default) | [optional] 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsCreate

> ExpertRatingsSerializerV2 expertRatingsCreate(expertRatingsSerializerV2)



Rate two videos

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let expertRatingsSerializerV2 = new TournesolApi.ExpertRatingsSerializerV2(); // ExpertRatingsSerializerV2 | 
apiInstance.expertRatingsCreate(expertRatingsSerializerV2, (error, data, response) => {
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
 **expertRatingsSerializerV2** | [**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)|  | 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## expertRatingsList

> PaginatedExpertRatingsSerializerV2List expertRatingsList(opts)



List my own expert ratings

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'video1': "video1_example", // String | First video in the rating (fixed order)
  'video2': "video2_example", // String | Second video in the rating (fixed order)
  'videoVideoId': "videoVideoId_example" // String | Any video ID (first or second)
};
apiInstance.expertRatingsList(opts, (error, data, response) => {
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
 **video1** | **String**| First video in the rating (fixed order) | [optional] 
 **video2** | **String**| Second video in the rating (fixed order) | [optional] 
 **videoVideoId** | **String**| Any video ID (first or second) | [optional] 

### Return type

[**PaginatedExpertRatingsSerializerV2List**](PaginatedExpertRatingsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsOnlineByVideoIdsPartialUpdate

> OnlineResponse expertRatingsOnlineByVideoIdsPartialUpdate(feature, newValue, videoLeft, videoRight, opts)



Do online updates on ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let feature = "feature_example"; // String | The feature to update
let newValue = 3.4; // Number | New value for the feature in 0..100.0
let videoLeft = "videoLeft_example"; // String | Left video (can be either v1 or v2)
let videoRight = "videoRight_example"; // String | Right video (can be either v1 or v2)
let opts = {
  'addDebugInfo': true // Boolean | Return also a dict with information
};
apiInstance.expertRatingsOnlineByVideoIdsPartialUpdate(feature, newValue, videoLeft, videoRight, opts, (error, data, response) => {
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
 **feature** | **String**| The feature to update | 
 **newValue** | **Number**| New value for the feature in 0..100.0 | 
 **videoLeft** | **String**| Left video (can be either v1 or v2) | 
 **videoRight** | **String**| Right video (can be either v1 or v2) | 
 **addDebugInfo** | **Boolean**| Return also a dict with information | [optional] 

### Return type

[**OnlineResponse**](OnlineResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsOnlineByVideoIdsRetrieve

> OnlineResponse expertRatingsOnlineByVideoIdsRetrieve(feature, newValue, videoLeft, videoRight, opts)



Do online updates on ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let feature = "feature_example"; // String | The feature to update
let newValue = 3.4; // Number | New value for the feature in 0..100.0
let videoLeft = "videoLeft_example"; // String | Left video (can be either v1 or v2)
let videoRight = "videoRight_example"; // String | Right video (can be either v1 or v2)
let opts = {
  'addDebugInfo': true // Boolean | Return also a dict with information
};
apiInstance.expertRatingsOnlineByVideoIdsRetrieve(feature, newValue, videoLeft, videoRight, opts, (error, data, response) => {
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
 **feature** | **String**| The feature to update | 
 **newValue** | **Number**| New value for the feature in 0..100.0 | 
 **videoLeft** | **String**| Left video (can be either v1 or v2) | 
 **videoRight** | **String**| Right video (can be either v1 or v2) | 
 **addDebugInfo** | **Boolean**| Return also a dict with information | [optional] 

### Return type

[**OnlineResponse**](OnlineResponse.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsPartialUpdate

> ExpertRatingsSerializerV2 expertRatingsPartialUpdate(id, opts)



Change some fields in a rating

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let id = 56; // Number | A unique integer value identifying this expert rating.
let opts = {
  'patchedExpertRatingsSerializerV2': new TournesolApi.PatchedExpertRatingsSerializerV2() // PatchedExpertRatingsSerializerV2 | 
};
apiInstance.expertRatingsPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this expert rating. | 
 **patchedExpertRatingsSerializerV2** | [**PatchedExpertRatingsSerializerV2**](PatchedExpertRatingsSerializerV2.md)|  | [optional] 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## expertRatingsRetrieve

> ExpertRatingsSerializerV2 expertRatingsRetrieve(id)



Set and get expert ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let id = 56; // Number | A unique integer value identifying this expert rating.
apiInstance.expertRatingsRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this expert rating. | 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsSampleFirstVideoRetrieve

> VideoSerializerV2 expertRatingsSampleFirstVideoRetrieve(opts)



Sample a video to rate.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'videoExclude': "videoExclude_example" // String | Exclude a video ID from consideration
};
apiInstance.expertRatingsSampleFirstVideoRetrieve(opts, (error, data, response) => {
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
 **videoExclude** | **String**| Exclude a video ID from consideration | [optional] 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsSamplePopularVideoRetrieve

> VideoSerializerV2 expertRatingsSamplePopularVideoRetrieve(opts)



Sample a popular video.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let opts = {
  'noRateLater': true // Boolean | Do not show videos in rate later list
};
apiInstance.expertRatingsSamplePopularVideoRetrieve(opts, (error, data, response) => {
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
 **noRateLater** | **Boolean**| Do not show videos in rate later list | [optional] 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsSampleVideoWithOtherRetrieve

> VideoSerializerV2 expertRatingsSampleVideoWithOtherRetrieve(videoOther)



Sample a video to rate.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let videoOther = "videoOther_example"; // String | Other video_id being rated
apiInstance.expertRatingsSampleVideoWithOtherRetrieve(videoOther, (error, data, response) => {
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
 **videoOther** | **String**| Other video_id being rated | 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## expertRatingsSkipVideoPartialUpdate

> expertRatingsSkipVideoPartialUpdate(patchedVideo)



Set and get expert ratings.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let patchedVideo = [new TournesolApi.PatchedVideo()]; // [PatchedVideo] | 
apiInstance.expertRatingsSkipVideoPartialUpdate(patchedVideo, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully.');
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedVideo** | [**[PatchedVideo]**](PatchedVideo.md)|  | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined


## expertRatingsUpdate

> ExpertRatingsSerializerV2 expertRatingsUpdate(id, expertRatingsSerializerV2)



Change all fields in a rating

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let id = 56; // Number | A unique integer value identifying this expert rating.
let expertRatingsSerializerV2 = new TournesolApi.ExpertRatingsSerializerV2(); // ExpertRatingsSerializerV2 | 
apiInstance.expertRatingsUpdate(id, expertRatingsSerializerV2, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this expert rating. | 
 **expertRatingsSerializerV2** | [**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)|  | 

### Return type

[**ExpertRatingsSerializerV2**](ExpertRatingsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## registerSliderChange

> SliderChangeSerializerV2 registerSliderChange(sliderChangeSerializerV2)



Register any change in slider values on the rating page.

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

let apiInstance = new TournesolApi.ExpertRatingsApi();
let sliderChangeSerializerV2 = new TournesolApi.SliderChangeSerializerV2(); // SliderChangeSerializerV2 | 
apiInstance.registerSliderChange(sliderChangeSerializerV2, (error, data, response) => {
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
 **sliderChangeSerializerV2** | [**SliderChangeSerializerV2**](SliderChangeSerializerV2.md)|  | 

### Return type

[**SliderChangeSerializerV2**](SliderChangeSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

