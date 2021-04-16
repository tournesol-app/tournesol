# TournesolApi.RateLaterApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**rateLaterBulkDeletePartialUpdate**](RateLaterApi.md#rateLaterBulkDeletePartialUpdate) | **PATCH** /api/v2/rate_later/bulk_delete/ | 
[**rateLaterCreate**](RateLaterApi.md#rateLaterCreate) | **POST** /api/v2/rate_later/ | 
[**rateLaterDestroy**](RateLaterApi.md#rateLaterDestroy) | **DELETE** /api/v2/rate_later/{id}/ | 
[**rateLaterList**](RateLaterApi.md#rateLaterList) | **GET** /api/v2/rate_later/ | 
[**rateLaterRetrieve**](RateLaterApi.md#rateLaterRetrieve) | **GET** /api/v2/rate_later/{id}/ | 



## rateLaterBulkDeletePartialUpdate

> rateLaterBulkDeletePartialUpdate(patchedVideoRateLaterDelete)



Delete many videos from the list by IDs.

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

let apiInstance = new TournesolApi.RateLaterApi();
let patchedVideoRateLaterDelete = [new TournesolApi.PatchedVideoRateLaterDelete()]; // [PatchedVideoRateLaterDelete] | 
apiInstance.rateLaterBulkDeletePartialUpdate(patchedVideoRateLaterDelete, (error, data, response) => {
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
 **patchedVideoRateLaterDelete** | [**[PatchedVideoRateLaterDelete]**](PatchedVideoRateLaterDelete.md)|  | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined


## rateLaterCreate

> VideoRateLaterSerializerV2 rateLaterCreate(videoRateLaterSerializerV2)



Schedule a video to be rated later

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

let apiInstance = new TournesolApi.RateLaterApi();
let videoRateLaterSerializerV2 = new TournesolApi.VideoRateLaterSerializerV2(); // VideoRateLaterSerializerV2 | 
apiInstance.rateLaterCreate(videoRateLaterSerializerV2, (error, data, response) => {
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
 **videoRateLaterSerializerV2** | [**VideoRateLaterSerializerV2**](VideoRateLaterSerializerV2.md)|  | 

### Return type

[**VideoRateLaterSerializerV2**](VideoRateLaterSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## rateLaterDestroy

> rateLaterDestroy(id)



Remove a video from rate later list

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

let apiInstance = new TournesolApi.RateLaterApi();
let id = 56; // Number | A unique integer value identifying this video rate later.
apiInstance.rateLaterDestroy(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video rate later. | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## rateLaterList

> PaginatedVideoRateLaterSerializerV2List rateLaterList(opts)



Get videos queued to be rated later

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

let apiInstance = new TournesolApi.RateLaterApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'videoVideoId': "videoVideoId_example" // String | video__video_id
};
apiInstance.rateLaterList(opts, (error, data, response) => {
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
 **videoVideoId** | **String**| video__video_id | [optional] 

### Return type

[**PaginatedVideoRateLaterSerializerV2List**](PaginatedVideoRateLaterSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## rateLaterRetrieve

> VideoRateLaterSerializerV2 rateLaterRetrieve(id)



Get one video to be rated later (by object ID)

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

let apiInstance = new TournesolApi.RateLaterApi();
let id = 56; // Number | A unique integer value identifying this video rate later.
apiInstance.rateLaterRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video rate later. | 

### Return type

[**VideoRateLaterSerializerV2**](VideoRateLaterSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

