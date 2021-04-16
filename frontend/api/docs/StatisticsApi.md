# TournesolApi.StatisticsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**view**](StatisticsApi.md#view) | **GET** /api/v2/statistics/view/ | 



## view

> StatisticsSerializerV2 view()



Get statistics for the website.

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

let apiInstance = new TournesolApi.StatisticsApi();
apiInstance.view((error, data, response) => {
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

[**StatisticsSerializerV2**](StatisticsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

