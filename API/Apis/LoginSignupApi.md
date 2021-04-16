# LoginSignupApi

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


<a name="loginSignupChangePasswordPartialUpdate"></a>
# **loginSignupChangePasswordPartialUpdate**
> OnlyUsernameAndID loginSignupChangePasswordPartialUpdate(patchedChangePassword)



    Change password

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedChangePassword** | [**PatchedChangePassword**](..//Models/PatchedChangePassword.md)|  | [optional]

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="loginSignupList"></a>
# **loginSignupList**
> PaginatedOnlyUsernameAndIDList loginSignupList(limit, offset)



    Get my username in a list

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]

### Return type

[**PaginatedOnlyUsernameAndIDList**](..//Models/PaginatedOnlyUsernameAndIDList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="loginSignupLoginPartialUpdate"></a>
# **loginSignupLoginPartialUpdate**
> OnlyUsernameAndID loginSignupLoginPartialUpdate(patchedLogin)



    Register a user.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedLogin** | [**PatchedLogin**](..//Models/PatchedLogin.md)|  | [optional]

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="loginSignupLogoutPartialUpdate"></a>
# **loginSignupLogoutPartialUpdate**
> loginSignupLogoutPartialUpdate()



    Log out.

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="loginSignupPartialUpdate"></a>
# **loginSignupPartialUpdate**
> OnlyUsernameAndID loginSignupPartialUpdate(id, patchedOnlyUsernameAndID)



    Update my username

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**|  | [default to null]
 **patchedOnlyUsernameAndID** | [**PatchedOnlyUsernameAndID**](..//Models/PatchedOnlyUsernameAndID.md)|  | [optional]

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="loginSignupRegisterCreate"></a>
# **loginSignupRegisterCreate**
> OnlyUsernameAndID loginSignupRegisterCreate(register)



    Register a user.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **register** | [**Register**](..//Models/Register.md)|  |

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="loginSignupResetPasswordPartialUpdate"></a>
# **loginSignupResetPasswordPartialUpdate**
> loginSignupResetPasswordPartialUpdate(patchedResetPassword)



    Reset password.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedResetPassword** | [**PatchedResetPassword**](..//Models/PatchedResetPassword.md)|  | [optional]

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined

<a name="loginSignupRetrieve"></a>
# **loginSignupRetrieve**
> OnlyUsernameAndID loginSignupRetrieve(id)



    Get my username by my user preferences id

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**|  | [default to null]

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="loginSignupUpdate"></a>
# **loginSignupUpdate**
> OnlyUsernameAndID loginSignupUpdate(id, onlyUsernameAndID)



    Update my username

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **String**|  | [default to null]
 **onlyUsernameAndID** | [**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)|  |

### Return type

[**OnlyUsernameAndID**](..//Models/OnlyUsernameAndID.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

