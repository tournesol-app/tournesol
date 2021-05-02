# TournesolApi.LoginSignupApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**loginSignupChangePasswordPartialUpdate**](LoginSignupApi.md#loginSignupChangePasswordPartialUpdate) | **PATCH** /api/v2/login_signup/change_password/ | 
[**loginSignupList**](LoginSignupApi.md#loginSignupList) | **GET** /api/v2/login_signup/ | 
[**loginSignupLoginPartialUpdate**](LoginSignupApi.md#loginSignupLoginPartialUpdate) | **PATCH** /api/v2/login_signup/login/ | 
[**loginSignupLogoutPartialUpdate**](LoginSignupApi.md#loginSignupLogoutPartialUpdate) | **PATCH** /api/v2/login_signup/logout/ | 
[**loginSignupPartialUpdate**](LoginSignupApi.md#loginSignupPartialUpdate) | **PATCH** /api/v2/login_signup/{id}/ | 
[**loginSignupRegisterCreate**](LoginSignupApi.md#loginSignupRegisterCreate) | **POST** /api/v2/login_signup/register/ | 
[**loginSignupResetPasswordPartialUpdate**](LoginSignupApi.md#loginSignupResetPasswordPartialUpdate) | **PATCH** /api/v2/login_signup/reset_password/ | 
[**loginSignupRetrieve**](LoginSignupApi.md#loginSignupRetrieve) | **GET** /api/v2/login_signup/{id}/ | 
[**loginSignupUpdate**](LoginSignupApi.md#loginSignupUpdate) | **PUT** /api/v2/login_signup/{id}/ | 



## loginSignupChangePasswordPartialUpdate

> OnlyUsernameAndID loginSignupChangePasswordPartialUpdate(opts)



Change password

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

let apiInstance = new TournesolApi.LoginSignupApi();
let opts = {
  'patchedChangePassword': new TournesolApi.PatchedChangePassword() // PatchedChangePassword | 
};
apiInstance.loginSignupChangePasswordPartialUpdate(opts, (error, data, response) => {
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
 **patchedChangePassword** | [**PatchedChangePassword**](PatchedChangePassword.md)|  | [optional] 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## loginSignupList

> PaginatedOnlyUsernameAndIDList loginSignupList(opts)



Get my username in a list

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

let apiInstance = new TournesolApi.LoginSignupApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56 // Number | The initial index from which to return the results.
};
apiInstance.loginSignupList(opts, (error, data, response) => {
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

[**PaginatedOnlyUsernameAndIDList**](PaginatedOnlyUsernameAndIDList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## loginSignupLoginPartialUpdate

> OnlyUsernameAndID loginSignupLoginPartialUpdate(opts)



Log in to Tournesol.

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

let apiInstance = new TournesolApi.LoginSignupApi();
let opts = {
  'patchedLogin': new TournesolApi.PatchedLogin() // PatchedLogin | 
};
apiInstance.loginSignupLoginPartialUpdate(opts, (error, data, response) => {
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
 **patchedLogin** | [**PatchedLogin**](PatchedLogin.md)|  | [optional] 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## loginSignupLogoutPartialUpdate

> loginSignupLogoutPartialUpdate()



Log out.

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

let apiInstance = new TournesolApi.LoginSignupApi();
apiInstance.loginSignupLogoutPartialUpdate((error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully.');
  }
});
```

### Parameters

This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## loginSignupPartialUpdate

> OnlyUsernameAndID loginSignupPartialUpdate(id, opts)



Update my username

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

let apiInstance = new TournesolApi.LoginSignupApi();
let id = "id_example"; // String | 
let opts = {
  'patchedOnlyUsernameAndID': new TournesolApi.PatchedOnlyUsernameAndID() // PatchedOnlyUsernameAndID | 
};
apiInstance.loginSignupPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **String**|  | 
 **patchedOnlyUsernameAndID** | [**PatchedOnlyUsernameAndID**](PatchedOnlyUsernameAndID.md)|  | [optional] 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## loginSignupRegisterCreate

> OnlyUsernameAndID loginSignupRegisterCreate(register)



Register a user.

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

let apiInstance = new TournesolApi.LoginSignupApi();
let register = new TournesolApi.Register(); // Register | 
apiInstance.loginSignupRegisterCreate(register, (error, data, response) => {
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
 **register** | [**Register**](Register.md)|  | 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## loginSignupResetPasswordPartialUpdate

> loginSignupResetPasswordPartialUpdate(opts)



Reset password.

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

let apiInstance = new TournesolApi.LoginSignupApi();
let opts = {
  'patchedResetPassword': new TournesolApi.PatchedResetPassword() // PatchedResetPassword | 
};
apiInstance.loginSignupResetPasswordPartialUpdate(opts, (error, data, response) => {
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
 **patchedResetPassword** | [**PatchedResetPassword**](PatchedResetPassword.md)|  | [optional] 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined


## loginSignupRetrieve

> OnlyUsernameAndID loginSignupRetrieve(id)



Get my username by my user preferences id

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

let apiInstance = new TournesolApi.LoginSignupApi();
let id = "id_example"; // String | 
apiInstance.loginSignupRetrieve(id, (error, data, response) => {
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
 **id** | **String**|  | 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## loginSignupUpdate

> OnlyUsernameAndID loginSignupUpdate(id, onlyUsernameAndID)



Update my username

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

let apiInstance = new TournesolApi.LoginSignupApi();
let id = "id_example"; // String | 
let onlyUsernameAndID = new TournesolApi.OnlyUsernameAndID(); // OnlyUsernameAndID | 
apiInstance.loginSignupUpdate(id, onlyUsernameAndID, (error, data, response) => {
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
 **id** | **String**|  | 
 **onlyUsernameAndID** | [**OnlyUsernameAndID**](OnlyUsernameAndID.md)|  | 

### Return type

[**OnlyUsernameAndID**](OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

