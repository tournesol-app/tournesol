# TournesolApi.UserInformationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**userInformationAddVerifyEmailPartialUpdate**](UserInformationApi.md#userInformationAddVerifyEmailPartialUpdate) | **PATCH** /api/v2/user_information/{id}/add_verify_email/ | 
[**userInformationList**](UserInformationApi.md#userInformationList) | **GET** /api/v2/user_information/ | 
[**userInformationPartialUpdate**](UserInformationApi.md#userInformationPartialUpdate) | **PATCH** /api/v2/user_information/{id}/ | 
[**userInformationPublicModelsList**](UserInformationApi.md#userInformationPublicModelsList) | **GET** /api/v2/user_information/public_models/ | 
[**userInformationRetrieve**](UserInformationApi.md#userInformationRetrieve) | **GET** /api/v2/user_information/{id}/ | 
[**userInformationSearchExpertiseList**](UserInformationApi.md#userInformationSearchExpertiseList) | **GET** /api/v2/user_information/search_expertise/ | 
[**userInformationSearchUsernameList**](UserInformationApi.md#userInformationSearchUsernameList) | **GET** /api/v2/user_information/search_username/ | 
[**userInformationUpdate**](UserInformationApi.md#userInformationUpdate) | **PUT** /api/v2/user_information/{id}/ | 
[**userInformationVerifyAllEmailsPartialUpdate**](UserInformationApi.md#userInformationVerifyAllEmailsPartialUpdate) | **PATCH** /api/v2/user_information/{id}/verify_all_emails/ | 
[**userInformationVerifyEmailPartialUpdate**](UserInformationApi.md#userInformationVerifyEmailPartialUpdate) | **PATCH** /api/v2/user_information/{id}/verify_email/ | 



## userInformationAddVerifyEmailPartialUpdate

> VerifiableEmail userInformationAddVerifyEmailPartialUpdate(email, id)



Add an address and ask for verification.

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

let apiInstance = new TournesolApi.UserInformationApi();
let email = "email_example"; // String | E-mail to add and ask to verify
let id = 56; // Number | A unique integer value identifying this user information.
apiInstance.userInformationAddVerifyEmailPartialUpdate(email, id, (error, data, response) => {
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
 **email** | **String**| E-mail to add and ask to verify | 
 **id** | **Number**| A unique integer value identifying this user information. | 

### Return type

[**VerifiableEmail**](VerifiableEmail.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationList

> PaginatedUserInformationPublicSerializerV2List userInformationList(opts)



List and filter user information

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

let apiInstance = new TournesolApi.UserInformationApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'userUsername': "userUsername_example" // String | user__username
};
apiInstance.userInformationList(opts, (error, data, response) => {
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
 **userUsername** | **String**| user__username | [optional] 

### Return type

[**PaginatedUserInformationPublicSerializerV2List**](PaginatedUserInformationPublicSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationPartialUpdate

> UserInformationPublicSerializerV2 userInformationPartialUpdate(id, opts)



Partially update my user information

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

let apiInstance = new TournesolApi.UserInformationApi();
let id = 56; // Number | A unique integer value identifying this user information.
let opts = {
  'patchedUserInformationPublicSerializerV2': new TournesolApi.PatchedUserInformationPublicSerializerV2() // PatchedUserInformationPublicSerializerV2 | 
};
apiInstance.userInformationPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user information. | 
 **patchedUserInformationPublicSerializerV2** | [**PatchedUserInformationPublicSerializerV2**](PatchedUserInformationPublicSerializerV2.md)|  | [optional] 

### Return type

[**UserInformationPublicSerializerV2**](UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## userInformationPublicModelsList

> PaginatedOnlyUsernameList userInformationPublicModelsList(opts)



Ask for e-mail verification for all unverified e-mails.

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

let apiInstance = new TournesolApi.UserInformationApi();
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'userUsername': "userUsername_example" // String | user__username
};
apiInstance.userInformationPublicModelsList(opts, (error, data, response) => {
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
 **userUsername** | **String**| user__username | [optional] 

### Return type

[**PaginatedOnlyUsernameList**](PaginatedOnlyUsernameList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationRetrieve

> UserInformationPublicSerializerV2 userInformationRetrieve(id)



Get information about one user

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

let apiInstance = new TournesolApi.UserInformationApi();
let id = 56; // Number | A unique integer value identifying this user information.
apiInstance.userInformationRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user information. | 

### Return type

[**UserInformationPublicSerializerV2**](UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationSearchExpertiseList

> PaginatedExpertiseList userInformationSearchExpertiseList(searchQuery, opts)



Get and set my UserInformation.

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

let apiInstance = new TournesolApi.UserInformationApi();
let searchQuery = "searchQuery_example"; // String | Search for this string in expertises
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'userUsername': "userUsername_example" // String | user__username
};
apiInstance.userInformationSearchExpertiseList(searchQuery, opts, (error, data, response) => {
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
 **searchQuery** | **String**| Search for this string in expertises | 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **userUsername** | **String**| user__username | [optional] 

### Return type

[**PaginatedExpertiseList**](PaginatedExpertiseList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationSearchUsernameList

> PaginatedOnlyUsernameList userInformationSearchUsernameList(searchQuery, opts)



Get and set my UserInformation.

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

let apiInstance = new TournesolApi.UserInformationApi();
let searchQuery = "searchQuery_example"; // String | Search for this string in user names
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'userUsername': "userUsername_example" // String | user__username
};
apiInstance.userInformationSearchUsernameList(searchQuery, opts, (error, data, response) => {
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
 **searchQuery** | **String**| Search for this string in user names | 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **userUsername** | **String**| user__username | [optional] 

### Return type

[**PaginatedOnlyUsernameList**](PaginatedOnlyUsernameList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationUpdate

> UserInformationPublicSerializerV2 userInformationUpdate(id, userInformationPublicSerializerV2)



Replace my user information

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

let apiInstance = new TournesolApi.UserInformationApi();
let id = 56; // Number | A unique integer value identifying this user information.
let userInformationPublicSerializerV2 = new TournesolApi.UserInformationPublicSerializerV2(); // UserInformationPublicSerializerV2 | 
apiInstance.userInformationUpdate(id, userInformationPublicSerializerV2, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user information. | 
 **userInformationPublicSerializerV2** | [**UserInformationPublicSerializerV2**](UserInformationPublicSerializerV2.md)|  | 

### Return type

[**UserInformationPublicSerializerV2**](UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## userInformationVerifyAllEmailsPartialUpdate

> PaginatedVerifiableEmailList userInformationVerifyAllEmailsPartialUpdate(id, opts)



Ask for e-mail verification for all unverified e-mails.

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

let apiInstance = new TournesolApi.UserInformationApi();
let id = 56; // Number | A unique integer value identifying this user information.
let opts = {
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'userUsername': "userUsername_example" // String | user__username
};
apiInstance.userInformationVerifyAllEmailsPartialUpdate(id, opts, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this user information. | 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **userUsername** | **String**| user__username | [optional] 

### Return type

[**PaginatedVerifiableEmailList**](PaginatedVerifiableEmailList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## userInformationVerifyEmailPartialUpdate

> VerifiableEmail userInformationVerifyEmailPartialUpdate(email, id)



Ask for e-mail verification.

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

let apiInstance = new TournesolApi.UserInformationApi();
let email = "email_example"; // String | E-mail to verify
let id = 56; // Number | A unique integer value identifying this user information.
apiInstance.userInformationVerifyEmailPartialUpdate(email, id, (error, data, response) => {
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
 **email** | **String**| E-mail to verify | 
 **id** | **Number**| A unique integer value identifying this user information. | 

### Return type

[**VerifiableEmail**](VerifiableEmail.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

