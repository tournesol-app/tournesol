# VideoReportsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**videoReportsCreate**](VideoReportsApi.md#videoReportsCreate) | **POST** /api/v2/video_reports/ | 
[**videoReportsList**](VideoReportsApi.md#videoReportsList) | **GET** /api/v2/video_reports/ | 
[**videoReportsPartialUpdate**](VideoReportsApi.md#videoReportsPartialUpdate) | **PATCH** /api/v2/video_reports/{id}/ | 
[**videoReportsRetrieve**](VideoReportsApi.md#videoReportsRetrieve) | **GET** /api/v2/video_reports/{id}/ | 
[**videoReportsUpdate**](VideoReportsApi.md#videoReportsUpdate) | **PUT** /api/v2/video_reports/{id}/ | 


<a name="videoReportsCreate"></a>
# **videoReportsCreate**
> VideoReportsSerializerV2 videoReportsCreate(videoReportsSerializerV2)



    Report a video

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoReportsSerializerV2** | [**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)|  |

### Return type

[**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="videoReportsList"></a>
# **videoReportsList**
> PaginatedVideoReportsSerializerV2List videoReportsList(limit, offset, onlyMine, videoVideoId)



    Show all anonymized video reports

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **onlyMine** | **String**| only_mine | [optional] [default to null]
 **videoVideoId** | **String**| video__video_id | [optional] [default to null]

### Return type

[**PaginatedVideoReportsSerializerV2List**](..//Models/PaginatedVideoReportsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoReportsPartialUpdate"></a>
# **videoReportsPartialUpdate**
> VideoReportsSerializerV2 videoReportsPartialUpdate(id, patchedVideoReportsSerializerV2)



    Change some fields in a video report

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video reports. | [default to null]
 **patchedVideoReportsSerializerV2** | [**PatchedVideoReportsSerializerV2**](..//Models/PatchedVideoReportsSerializerV2.md)|  | [optional]

### Return type

[**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="videoReportsRetrieve"></a>
# **videoReportsRetrieve**
> VideoReportsSerializerV2 videoReportsRetrieve(id)



    Get one video report

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video reports. | [default to null]

### Return type

[**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoReportsUpdate"></a>
# **videoReportsUpdate**
> VideoReportsSerializerV2 videoReportsUpdate(id, videoReportsSerializerV2)



    Change all fields in a video report

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video reports. | [default to null]
 **videoReportsSerializerV2** | [**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)|  |

### Return type

[**VideoReportsSerializerV2**](..//Models/VideoReportsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

