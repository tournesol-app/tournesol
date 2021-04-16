# UserInformationApi

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


<a name="userInformationAddVerifyEmailPartialUpdate"></a>
# **userInformationAddVerifyEmailPartialUpdate**
> VerifiableEmail userInformationAddVerifyEmailPartialUpdate(email, id)



    Add an address and ask for verification.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **String**| E-mail to add and ask to verify | [default to null]
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]

### Return type

[**VerifiableEmail**](..//Models/VerifiableEmail.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationList"></a>
# **userInformationList**
> PaginatedUserInformationPublicSerializerV2List userInformationList(limit, offset, userUsername)



    List and filter user information

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **userUsername** | **String**| user__username | [optional] [default to null]

### Return type

[**PaginatedUserInformationPublicSerializerV2List**](..//Models/PaginatedUserInformationPublicSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationPartialUpdate"></a>
# **userInformationPartialUpdate**
> UserInformationPublicSerializerV2 userInformationPartialUpdate(id, patchedUserInformationPublicSerializerV2)



    Partially update my user information

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]
 **patchedUserInformationPublicSerializerV2** | [**PatchedUserInformationPublicSerializerV2**](..//Models/PatchedUserInformationPublicSerializerV2.md)|  | [optional]

### Return type

[**UserInformationPublicSerializerV2**](..//Models/UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="userInformationPublicModelsList"></a>
# **userInformationPublicModelsList**
> PaginatedOnlyUsernameList userInformationPublicModelsList(limit, offset, userUsername)



    Ask for e-mail verification for all unverified e-mails.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **userUsername** | **String**| user__username | [optional] [default to null]

### Return type

[**PaginatedOnlyUsernameList**](..//Models/PaginatedOnlyUsernameList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationRetrieve"></a>
# **userInformationRetrieve**
> UserInformationPublicSerializerV2 userInformationRetrieve(id)



    Get information about one user

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]

### Return type

[**UserInformationPublicSerializerV2**](..//Models/UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationSearchExpertiseList"></a>
# **userInformationSearchExpertiseList**
> PaginatedExpertiseList userInformationSearchExpertiseList(searchQuery, limit, offset, userUsername)



    Get and set my UserInformation.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **searchQuery** | **String**| Search for this string in expertises | [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **userUsername** | **String**| user__username | [optional] [default to null]

### Return type

[**PaginatedExpertiseList**](..//Models/PaginatedExpertiseList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationSearchUsernameList"></a>
# **userInformationSearchUsernameList**
> PaginatedOnlyUsernameList userInformationSearchUsernameList(searchQuery, limit, offset, userUsername)



    Get and set my UserInformation.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **searchQuery** | **String**| Search for this string in user names | [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **userUsername** | **String**| user__username | [optional] [default to null]

### Return type

[**PaginatedOnlyUsernameList**](..//Models/PaginatedOnlyUsernameList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationUpdate"></a>
# **userInformationUpdate**
> UserInformationPublicSerializerV2 userInformationUpdate(id, userInformationPublicSerializerV2)



    Replace my user information

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]
 **userInformationPublicSerializerV2** | [**UserInformationPublicSerializerV2**](..//Models/UserInformationPublicSerializerV2.md)|  |

### Return type

[**UserInformationPublicSerializerV2**](..//Models/UserInformationPublicSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="userInformationVerifyAllEmailsPartialUpdate"></a>
# **userInformationVerifyAllEmailsPartialUpdate**
> PaginatedVerifiableEmailList userInformationVerifyAllEmailsPartialUpdate(id, limit, offset, userUsername)



    Ask for e-mail verification for all unverified e-mails.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **userUsername** | **String**| user__username | [optional] [default to null]

### Return type

[**PaginatedVerifiableEmailList**](..//Models/PaginatedVerifiableEmailList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="userInformationVerifyEmailPartialUpdate"></a>
# **userInformationVerifyEmailPartialUpdate**
> VerifiableEmail userInformationVerifyEmailPartialUpdate(email, id)



    Ask for e-mail verification.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **String**| E-mail to verify | [default to null]
 **id** | **Integer**| A unique integer value identifying this user information. | [default to null]

### Return type

[**VerifiableEmail**](..//Models/VerifiableEmail.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

