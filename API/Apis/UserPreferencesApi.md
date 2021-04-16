# UserPreferencesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**userPreferencesList**](UserPreferencesApi.md#userPreferencesList) | **GET** /api/v2/user_preferences/ | 
[**userPreferencesMyPartialUpdate**](UserPreferencesApi.md#userPreferencesMyPartialUpdate) | **PATCH** /api/v2/user_preferences/my/ | 
[**userPreferencesMyRetrieve**](UserPreferencesApi.md#userPreferencesMyRetrieve) | **GET** /api/v2/user_preferences/my/ | 
[**userPreferencesPartialUpdate**](UserPreferencesApi.md#userPreferencesPartialUpdate) | **PATCH** /api/v2/user_preferences/{id}/ | 
[**userPreferencesRetrieve**](UserPreferencesApi.md#userPreferencesRetrieve) | **GET** /api/v2/user_preferences/{id}/ | 
[**userPreferencesUpdate**](UserPreferencesApi.md#userPreferencesUpdate) | **PUT** /api/v2/user_preferences/{id}/ | 


<a name="userPreferencesList"></a>
# **userPreferencesList**
> PaginatedUserPreferencesSerializerV2List userPreferencesList(limit, offset)



    Show my user preferences in a list

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]

### Return type

[**PaginatedUserPreferencesSerializerV2List**](..//Models/PaginatedUserPreferencesSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userPreferencesMyPartialUpdate"></a>
# **userPreferencesMyPartialUpdate**
> UserPreferencesSerializerV2 userPreferencesMyPartialUpdate(patchedUserPreferencesSerializerV2)



    Get/set my own user preferences.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedUserPreferencesSerializerV2** | [**PatchedUserPreferencesSerializerV2**](..//Models/PatchedUserPreferencesSerializerV2.md)|  | [optional]

### Return type

[**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="userPreferencesMyRetrieve"></a>
# **userPreferencesMyRetrieve**
> UserPreferencesSerializerV2 userPreferencesMyRetrieve()



    Get/set my own user preferences.

### Parameters
This endpoint does not need any parameter.

### Return type

[**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userPreferencesPartialUpdate"></a>
# **userPreferencesPartialUpdate**
> UserPreferencesSerializerV2 userPreferencesPartialUpdate(id, patchedUserPreferencesSerializerV2)



    Change some fields in user preferences

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user preferences. | [default to null]
 **patchedUserPreferencesSerializerV2** | [**PatchedUserPreferencesSerializerV2**](..//Models/PatchedUserPreferencesSerializerV2.md)|  | [optional]

### Return type

[**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="userPreferencesRetrieve"></a>
# **userPreferencesRetrieve**
> UserPreferencesSerializerV2 userPreferencesRetrieve(id)



    Get user preferences

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user preferences. | [default to null]

### Return type

[**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userPreferencesUpdate"></a>
# **userPreferencesUpdate**
> UserPreferencesSerializerV2 userPreferencesUpdate(id, userPreferencesSerializerV2)



    Change all fields in user preferences

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user preferences. | [default to null]
 **userPreferencesSerializerV2** | [**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)|  | [optional]

### Return type

[**UserPreferencesSerializerV2**](..//Models/UserPreferencesSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

