# EmailDomainApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**emailDomainList**](EmailDomainApi.md#emailDomainList) | **GET** /api/v2/email_domain/ | 
[**emailDomainRetrieve**](EmailDomainApi.md#emailDomainRetrieve) | **GET** /api/v2/email_domain/{id}/ | 


<a name="emailDomainList"></a>
# **emailDomainList**
> PaginatedEmailDomainList emailDomainList(limit, offset, status)



    List e-mail domains

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **status** | **String**| status | [optional] [default to null] [enum: RJ, ACK, PD]

### Return type

[**PaginatedEmailDomainList**](..//Models/PaginatedEmailDomainList.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="emailDomainRetrieve"></a>
# **emailDomainRetrieve**
> EmailDomain emailDomainRetrieve(id)



    Get e-mail domain

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this email domain. | [default to null]

### Return type

[**EmailDomain**](..//Models/EmailDomain.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

