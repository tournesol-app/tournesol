# VideoCommentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiV2VideoCommentsSetMark**](VideoCommentsApi.md#apiV2VideoCommentsSetMark) | **POST** /api/v2/video_comments/{id}/set_mark/ | 
[**videoCommentsCreate**](VideoCommentsApi.md#videoCommentsCreate) | **POST** /api/v2/video_comments/ | 
[**videoCommentsList**](VideoCommentsApi.md#videoCommentsList) | **GET** /api/v2/video_comments/ | 
[**videoCommentsPartialUpdate**](VideoCommentsApi.md#videoCommentsPartialUpdate) | **PATCH** /api/v2/video_comments/{id}/ | 
[**videoCommentsRetrieve**](VideoCommentsApi.md#videoCommentsRetrieve) | **GET** /api/v2/video_comments/{id}/ | 
[**videoCommentsUpdate**](VideoCommentsApi.md#videoCommentsUpdate) | **PUT** /api/v2/video_comments/{id}/ | 


<a name="apiV2VideoCommentsSetMark"></a>
# **apiV2VideoCommentsSetMark**
> VideoCommentsSerializerV2 apiV2VideoCommentsSetMark(action, id, marker)



    Mark a comment with a flag (like/dislike/red flag).

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **action** | **String**| Delete or add the marker, one of [&#39;add&#39;, &#39;delete&#39;, &#39;toggle&#39;] | [default to null] [enum: add, delete, toggle]
 **id** | **Integer**| A unique integer value identifying this video comment. | [default to null]
 **marker** | **String**| The marker to set, one of [&#39;votes_plus&#39;, &#39;votes_minus&#39;, &#39;red_flags&#39;] | [default to null] [enum: red_flags, votes_minus, votes_plus]

### Return type

[**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoCommentsCreate"></a>
# **videoCommentsCreate**
> VideoCommentsSerializerV2 videoCommentsCreate(videoCommentsSerializerV2)



    Comment on a video

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **videoCommentsSerializerV2** | [**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)|  |

### Return type

[**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="videoCommentsList"></a>
# **videoCommentsList**
> PaginatedVideoCommentsSerializerV2List videoCommentsList(backfireRisk, betterHabits, comment, diversityInclusion, engaging, entertainingRelaxing, importance, laymanFriendly, limit, offset, parentComment, pedagogy, reliability, userUserUsername, videoVideoId)



    List and filter comments

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfireRisk** | **String**| backfire_risk | [optional] [default to null]
 **betterHabits** | **String**| better_habits | [optional] [default to null]
 **comment** | **String**| comment | [optional] [default to null]
 **diversityInclusion** | **String**| diversity_inclusion | [optional] [default to null]
 **engaging** | **String**| engaging | [optional] [default to null]
 **entertainingRelaxing** | **String**| entertaining_relaxing | [optional] [default to null]
 **importance** | **String**| importance | [optional] [default to null]
 **laymanFriendly** | **String**| layman_friendly | [optional] [default to null]
 **limit** | **Integer**| Number of results to return per page. | [optional] [default to null]
 **offset** | **Integer**| The initial index from which to return the results. | [optional] [default to null]
 **parentComment** | **String**| parent_comment | [optional] [default to null]
 **pedagogy** | **String**| pedagogy | [optional] [default to null]
 **reliability** | **String**| reliability | [optional] [default to null]
 **userUserUsername** | **String**| user__user__username | [optional] [default to null]
 **videoVideoId** | **String**| video__video_id | [optional] [default to null]

### Return type

[**PaginatedVideoCommentsSerializerV2List**](..//Models/PaginatedVideoCommentsSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoCommentsPartialUpdate"></a>
# **videoCommentsPartialUpdate**
> VideoCommentsSerializerV2 videoCommentsPartialUpdate(id, patchedVideoCommentsSerializerV2)



    Change some fields in a comment

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video comment. | [default to null]
 **patchedVideoCommentsSerializerV2** | [**PatchedVideoCommentsSerializerV2**](..//Models/PatchedVideoCommentsSerializerV2.md)|  | [optional]

### Return type

[**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

<a name="videoCommentsRetrieve"></a>
# **videoCommentsRetrieve**
> VideoCommentsSerializerV2 videoCommentsRetrieve(id)



    Get one comment

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video comment. | [default to null]

### Return type

[**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

<a name="videoCommentsUpdate"></a>
# **videoCommentsUpdate**
> VideoCommentsSerializerV2 videoCommentsUpdate(id, videoCommentsSerializerV2)



    Change all fields in a comment

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **Integer**| A unique integer value identifying this video comment. | [default to null]
 **videoCommentsSerializerV2** | [**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)|  |

### Return type

[**VideoCommentsSerializerV2**](..//Models/VideoCommentsSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json

