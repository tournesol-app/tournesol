# TournesolApi.UserPreferencesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**userPreferencesList**](UserPreferencesApi.md#userPreferencesList) | **GET** /api/v2/user_preferences/ | 
[**userPreferencesMyPartialUpdate**](UserPreferencesApi.md#userPreferencesMyPartialUpdate) | **PATCH** /api/v2/user_preferences/my/ | 
[**userPreferencesMyRetrieve**](UserPreferencesApi.md#userPreferencesMyRetrieve) | **GET** /api/v2/user_preferences/my/ | 
[**userPreferencesPartialUpdate**](UserPreferencesApi.md#userPreferencesPartialUpdate) | **PATCH** /api/v2/user_preferences/{id}/ | 
[**userPreferencesRetrieve**](UserPreferencesApi.md#userPreferencesRetrieve) | **GET** /api/v2/user_preferences/{id}/ | 
[**userPreferencesUpdate**](UserPreferencesApi.md#userPreferencesUpdate) | **PUT** /api/v2/user_preferences/{id}/ | 



## userPreferencesList

> PaginatedUserPreferencesSerializerV2List userPreferencesList(opts)



Show my user preferences in a list

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

let apiInstance = new TournesolApi.UserPreferencesApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56 // Number | The initial index from which to return the results.
};
apiInstance.userPreferencesList(opts, (error, data, response) => {
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

### Return type

[**PaginatedUserPreferencesSerializerV2List**](PaginatedUserPreferencesSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userPreferencesMyPartialUpdate

> UserPreferencesSerializerV2 userPreferencesMyPartialUpdate(opts)



Get/set my own user preferences.

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

let apiInstance = new TournesolApi.UserPreferencesApi();
let opts = {
  'patchedUserPreferencesSerializerV2': new TournesolApi.PatchedUserPreferencesSerializerV2() // PatchedUserPreferencesSerializerV2 | 
};
apiInstance.userPreferencesMyPartialUpdate(opts, (error, data, response) => {
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
 **patchedUserPreferencesSerializerV2** | [**PatchedUserPreferencesSerializerV2**](PatchedUserPreferencesSerializerV2.md)|  | [optional] 

### Return type

[**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## userPreferencesMyRetrieve

> UserPreferencesSerializerV2 userPreferencesMyRetrieve()



Get/set my own user preferences.

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

let apiInstance = new TournesolApi.UserPreferencesApi();
apiInstance.userPreferencesMyRetrieve((error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userPreferencesPartialUpdate

> UserPreferencesSerializerV2 userPreferencesPartialUpdate(id, opts)



Change some fields in user preferences

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

let apiInstance = new TournesolApi.UserPreferencesApi();
let id = 56; // Number | A unique integer value identifying this user preferences.
let opts = {
  'patchedUserPreferencesSerializerV2': new TournesolApi.PatchedUserPreferencesSerializerV2() // PatchedUserPreferencesSerializerV2 | 
};
apiInstance.userPreferencesPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user preferences. | 
 **patchedUserPreferencesSerializerV2** | [**PatchedUserPreferencesSerializerV2**](PatchedUserPreferencesSerializerV2.md)|  | [optional] 

### Return type

[**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## userPreferencesRetrieve

> UserPreferencesSerializerV2 userPreferencesRetrieve(id)



Get user preferences

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

let apiInstance = new TournesolApi.UserPreferencesApi();
let id = 56; // Number | A unique integer value identifying this user preferences.
apiInstance.userPreferencesRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user preferences. | 

### Return type

[**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userPreferencesUpdate

> UserPreferencesSerializerV2 userPreferencesUpdate(id, opts)



Change all fields in user preferences

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

let apiInstance = new TournesolApi.UserPreferencesApi();
let id = 56; // Number | A unique integer value identifying this user preferences.
let opts = {
  'userPreferencesSerializerV2': new TournesolApi.UserPreferencesSerializerV2() // UserPreferencesSerializerV2 | 
};
apiInstance.userPreferencesUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user preferences. | 
 **userPreferencesSerializerV2** | [**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)|  | [optional] 

### Return type

[**UserPreferencesSerializerV2**](UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

