# TournesolApi.VideoReportsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**videoReportsCreate**](VideoReportsApi.md#videoReportsCreate) | **POST** /api/v2/video_reports/ | 
[**videoReportsList**](VideoReportsApi.md#videoReportsList) | **GET** /api/v2/video_reports/ | 
[**videoReportsPartialUpdate**](VideoReportsApi.md#videoReportsPartialUpdate) | **PATCH** /api/v2/video_reports/{id}/ | 
[**videoReportsRetrieve**](VideoReportsApi.md#videoReportsRetrieve) | **GET** /api/v2/video_reports/{id}/ | 
[**videoReportsUpdate**](VideoReportsApi.md#videoReportsUpdate) | **PUT** /api/v2/video_reports/{id}/ | 



## videoReportsCreate

> VideoReportsSerializerV2 videoReportsCreate(videoReportsSerializerV2)



Report a video

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

let apiInstance = new TournesolApi.VideoReportsApi();
let videoReportsSerializerV2 = new TournesolApi.VideoReportsSerializerV2(); // VideoReportsSerializerV2 | 
apiInstance.videoReportsCreate(videoReportsSerializerV2, (error, data, response) => {
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
 **videoReportsSerializerV2** | [**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)|  | 

### Return type

[**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## videoReportsList

> PaginatedVideoReportsSerializerV2List videoReportsList(opts)



Show all anonymized video reports

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

let apiInstance = new TournesolApi.VideoReportsApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'onlyMine': "onlyMine_example", // String | only_mine
  'videoVideoId': "videoVideoId_example" // String | video__video_id
};
apiInstance.videoReportsList(opts, (error, data, response) => {
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
 **onlyMine** | **String**| only_mine | [optional] 
 **videoVideoId** | **String**| video__video_id | [optional] 

### Return type

[**PaginatedVideoReportsSerializerV2List**](PaginatedVideoReportsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoReportsPartialUpdate

> VideoReportsSerializerV2 videoReportsPartialUpdate(id, opts)



Change some fields in a video report

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

let apiInstance = new TournesolApi.VideoReportsApi();
let id = 56; // Number | A unique integer value identifying this video reports.
let opts = {
  'patchedVideoReportsSerializerV2': new TournesolApi.PatchedVideoReportsSerializerV2() // PatchedVideoReportsSerializerV2 | 
};
apiInstance.videoReportsPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video reports. | 
 **patchedVideoReportsSerializerV2** | [**PatchedVideoReportsSerializerV2**](PatchedVideoReportsSerializerV2.md)|  | [optional] 

### Return type

[**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## videoReportsRetrieve

> VideoReportsSerializerV2 videoReportsRetrieve(id)



Get one video report

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

let apiInstance = new TournesolApi.VideoReportsApi();
let id = 56; // Number | A unique integer value identifying this video reports.
apiInstance.videoReportsRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video reports. | 

### Return type

[**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videoReportsUpdate

> VideoReportsSerializerV2 videoReportsUpdate(id, videoReportsSerializerV2)



Change all fields in a video report

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

let apiInstance = new TournesolApi.VideoReportsApi();
let id = 56; // Number | A unique integer value identifying this video reports.
let videoReportsSerializerV2 = new TournesolApi.VideoReportsSerializerV2(); // VideoReportsSerializerV2 | 
apiInstance.videoReportsUpdate(id, videoReportsSerializerV2, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video reports. | 
 **videoReportsSerializerV2** | [**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)|  | 

### Return type

[**VideoReportsSerializerV2**](VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

