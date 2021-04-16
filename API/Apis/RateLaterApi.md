# RateLaterApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**rateLaterBulkDeletePartialUpdate**](RateLaterApi.md#rateLaterBulkDeletePartialUpdate) | **PATCH** /api/v2/rate_later/bulk_delete/ | 
[**rateLaterCreate**](RateLaterApi.md#rateLaterCreate) | **POST** /api/v2/rate_later/ | 
[**rateLaterDestroy**](RateLaterApi.md#rateLaterDestroy) | **DELETE** /api/v2/rate_later/{id}/ | 
[**rateLaterList**](RateLaterApi.md#rateLaterList) | **GET** /api/v2/rate_later/ | 
[**rateLaterRetrieve**](RateLaterApi.md#rateLaterRetrieve) | **GET** /api/v2/rate_later/{id}/ | 


<a name="rateLaterBulkDeletePartialUpdate"></a>
# **rateLaterBulkDeletePartialUpdate**
> rateLaterBulkDeletePartialUpdate(patchedVideoRateLaterDelete)



    Delete many videos from the list by IDs.

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **patchedVideoRateLaterDelete** | [**List**](..//Models/PatchedVideoRateLaterDelete.md)|  |

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: Not defined

<a name="rateLaterCreate"></a>
# **rateLaterCreate**
> VideoRateLaterSerializerV2 rateLaterCreate(videoRateLaterSerializerV2)



    Schedule a video to be rated later

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoRateLaterSerializerV2** | [**VideoRateLaterSerializerV2**](..//Models/VideoRateLaterSerializerV2.md)|  |

### Return type

[**VideoRateLaterSerializerV2**](..//Models/VideoRateLaterSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="rateLaterDestroy"></a>
# **rateLaterDestroy**
> rateLaterDestroy(id)



    Remove a video from rate later list

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video rate later. | [default to null]

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

<a name="rateLaterList"></a>
# **rateLaterList**
> PaginatedVideoRateLaterSerializerV2List rateLaterList(limit, offset, videoVideoId)



    Get videos queued to be rated later

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **videoVideoId** | **String**| video__video_id | [optional] [default to null]

### Return type

[**PaginatedVideoRateLaterSerializerV2List**](..//Models/PaginatedVideoRateLaterSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="rateLaterRetrieve"></a>
# **rateLaterRetrieve**
> VideoRateLaterSerializerV2 rateLaterRetrieve(id)



    Get one video to be rated later (by object ID)

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video rate later. | [default to null]

### Return type

[**VideoRateLaterSerializerV2**](..//Models/VideoRateLaterSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

