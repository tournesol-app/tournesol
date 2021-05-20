# TournesolApi.VideosApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apiV2VideoSearchTournesol**](VideosApi.md#apiV2VideoSearchTournesol) | **GET** /api/v2/videos/search_tournesol/ | 
[**apiV2VideoSearchYoutube**](VideosApi.md#apiV2VideoSearchYoutube) | **GET** /api/v2/videos/search_youtube/ | 
[**myRatingsArePrivate**](VideosApi.md#myRatingsArePrivate) | **GET** /api/v2/videos/my_ratings_are_private/ | 
[**nThanks**](VideosApi.md#nThanks) | **GET** /api/v2/videos/n_thanks/ | 
[**setAllRatingPrivacy**](VideosApi.md#setAllRatingPrivacy) | **PATCH** /api/v2/videos/set_all_rating_privacy/ | 
[**setRatingPrivacy**](VideosApi.md#setRatingPrivacy) | **PATCH** /api/v2/videos/set_rating_privacy/ | 
[**thankContributors**](VideosApi.md#thankContributors) | **PATCH** /api/v2/videos/thank_contributors/ | 
[**videosCreate**](VideosApi.md#videosCreate) | **POST** /api/v2/videos/ | 
[**videosList**](VideosApi.md#videosList) | **GET** /api/v2/videos/ | 
[**videosRatedVideosList**](VideosApi.md#videosRatedVideosList) | **GET** /api/v2/videos/rated_videos/ | 
[**videosRetrieve**](VideosApi.md#videosRetrieve) | **GET** /api/v2/videos/{id}/ | 



## apiV2VideoSearchTournesol

> PaginatedVideoSerializerV2List apiV2VideoSearchTournesol(opts)



Search videos using the Tournesol algorithm.

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

let apiInstance = new TournesolApi.VideosApi();
let opts = {
  'backfireRisk': 3.4, // Number | Resilience to backfiring risks [preference override]
  'betterHabits': 3.4, // Number | Encourages better habits [preference override]
  'daysAgoGte': "daysAgoGte_example", // String | Upload date, older than x days ago
  'daysAgoLte': "daysAgoLte_example", // String | Upload date, more recent than x days ago
  'diversityInclusion': 3.4, // Number | Diversity and Inclusion [preference override]
  'durationGte': "durationGte_example", // String | duration_gte
  'durationLte': "durationLte_example", // String | duration_lte
  'engaging': 3.4, // Number | Engaging and thought-provoking [preference override]
  'entertainingRelaxing': 3.4, // Number | Entertaining and relaxing [preference override]
  'importance': 3.4, // Number | Important and actionable [preference override]
  'language': "language_example", // String | language
  'largelyRecommended': 3.4, // Number | Should be largely recommended [preference override]
  'laymanFriendly': 3.4, // Number | Layman-friendly [preference override]
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'ordering': "ordering_example", // String | Which field to use when ordering the results.
  'pedagogy': 3.4, // Number | Clear and pedagogical [preference override]
  'reliability': 3.4, // Number | Reliable and not misleading [preference override]
  'search': "search_example", // String | Search string
  'searchModel': "searchModel_example", // String | Use this user's algorithmic representative
  'showAllMyVideos': "showAllMyVideos_example", // String | Show all my videos in search
  'videoId': "videoId_example", // String | video_id
  'viewsGte': "viewsGte_example", // String | views_gte
  'viewsLte': "viewsLte_example" // String | views_lte
};
apiInstance.apiV2VideoSearchTournesol(opts, (error, data, response) => {
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
 **backfireRisk** | **Number**| Resilience to backfiring risks [preference override] | [optional] 
 **betterHabits** | **Number**| Encourages better habits [preference override] | [optional] 
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] 
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] 
 **diversityInclusion** | **Number**| Diversity and Inclusion [preference override] | [optional] 
 **durationGte** | **String**| duration_gte | [optional] 
 **durationLte** | **String**| duration_lte | [optional] 
 **engaging** | **Number**| Engaging and thought-provoking [preference override] | [optional] 
 **entertainingRelaxing** | **Number**| Entertaining and relaxing [preference override] | [optional] 
 **importance** | **Number**| Important and actionable [preference override] | [optional] 
 **language** | **String**| language | [optional] 
 **largelyRecommended** | **Number**| Should be largely recommended [preference override] | [optional] 
 **laymanFriendly** | **Number**| Layman-friendly [preference override] | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **ordering** | **String**| Which field to use when ordering the results. | [optional] 
 **pedagogy** | **Number**| Clear and pedagogical [preference override] | [optional] 
 **reliability** | **Number**| Reliable and not misleading [preference override] | [optional] 
 **search** | **String**| Search string | [optional] 
 **searchModel** | **String**| Use this user&#39;s algorithmic representative | [optional] 
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] 
 **videoId** | **String**| video_id | [optional] 
 **viewsGte** | **String**| views_gte | [optional] 
 **viewsLte** | **String**| views_lte | [optional] 

### Return type

[**PaginatedVideoSerializerV2List**](PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## apiV2VideoSearchYoutube

> PaginatedVideoSerializerV2List apiV2VideoSearchYoutube(search, opts)



Search videos using the YouTube algorithm.

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

let apiInstance = new TournesolApi.VideosApi();
let search = "search_example"; // String | Youtube search phrase
let opts = {
  'daysAgoGte': "daysAgoGte_example", // String | Upload date, older than x days ago
  'daysAgoLte': "daysAgoLte_example", // String | Upload date, more recent than x days ago
  'durationGte': "durationGte_example", // String | duration_gte
  'durationLte': "durationLte_example", // String | duration_lte
  'language': "language_example", // String | language
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'ordering': "ordering_example", // String | Which field to use when ordering the results.
  'showAllMyVideos': "showAllMyVideos_example", // String | Show all my videos in search
  'videoId': "videoId_example", // String | video_id
  'viewsGte': "viewsGte_example", // String | views_gte
  'viewsLte': "viewsLte_example" // String | views_lte
};
apiInstance.apiV2VideoSearchYoutube(search, opts, (error, data, response) => {
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
 **search** | **String**| Youtube search phrase | 
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] 
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] 
 **durationGte** | **String**| duration_gte | [optional] 
 **durationLte** | **String**| duration_lte | [optional] 
 **language** | **String**| language | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **ordering** | **String**| Which field to use when ordering the results. | [optional] 
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] 
 **videoId** | **String**| video_id | [optional] 
 **viewsGte** | **String**| views_gte | [optional] 
 **viewsLte** | **String**| views_lte | [optional] 

### Return type

[**PaginatedVideoSerializerV2List**](PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## myRatingsArePrivate

> PrivateOrPublic myRatingsArePrivate(videoId)



Are my ratings private?

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

let apiInstance = new TournesolApi.VideosApi();
let videoId = "videoId_example"; // String | Youtube Video ID
apiInstance.myRatingsArePrivate(videoId, (error, data, response) => {
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
 **videoId** | **String**| Youtube Video ID | 

### Return type

[**PrivateOrPublic**](PrivateOrPublic.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## nThanks

> NumberOfThanks nThanks(videoId)



Get number of people I thanked for a video.

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

let apiInstance = new TournesolApi.VideosApi();
let videoId = "videoId_example"; // String | Youtube Video ID
apiInstance.nThanks(videoId, (error, data, response) => {
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
 **videoId** | **String**| Youtube Video ID | 

### Return type

[**NumberOfThanks**](NumberOfThanks.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## setAllRatingPrivacy

> setAllRatingPrivacy(isPublic)



Set all video rating privacy.

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

let apiInstance = new TournesolApi.VideosApi();
let isPublic = true; // Boolean | Should all ratings be public
apiInstance.setAllRatingPrivacy(isPublic, (error, data, response) => {
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
 **isPublic** | **Boolean**| Should all ratings be public | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## setRatingPrivacy

> setRatingPrivacy(isPublic, videoId)



Set video rating privacy.

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

let apiInstance = new TournesolApi.VideosApi();
let isPublic = true; // Boolean | Should the rating be public
let videoId = "videoId_example"; // String | Youtube Video ID
apiInstance.setRatingPrivacy(isPublic, videoId, (error, data, response) => {
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
 **isPublic** | **Boolean**| Should the rating be public | 
 **videoId** | **String**| Youtube Video ID | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## thankContributors

> thankContributors(action, videoId)



Thank contributors for the video.

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

let apiInstance = new TournesolApi.VideosApi();
let action = "action_example"; // String | Set/unset
let videoId = "videoId_example"; // String | Youtube Video ID
apiInstance.thankContributors(action, videoId, (error, data, response) => {
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
 **action** | **String**| Set/unset | 
 **videoId** | **String**| Youtube Video ID | 

### Return type

null (empty response body)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


## videosCreate

> VideoSerializerV2 videosCreate(videoSerializerV2)



Add a video to the database (without filling the fields) from Youtube

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

let apiInstance = new TournesolApi.VideosApi();
let videoSerializerV2 = new TournesolApi.VideoSerializerV2(); // VideoSerializerV2 | 
apiInstance.videosCreate(videoSerializerV2, (error, data, response) => {
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
 **videoSerializerV2** | [**VideoSerializerV2**](VideoSerializerV2.md)|  | 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: application/json, application/x-www-form-urlencoded, multipart/form-data
- **Accept**: application/json


## videosList

> PaginatedVideoSerializerV2List videosList(opts)



List all videos with search/filter capability

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

let apiInstance = new TournesolApi.VideosApi();
let opts = {
  'daysAgoGte': "daysAgoGte_example", // String | Upload date, older than x days ago
  'daysAgoLte': "daysAgoLte_example", // String | Upload date, more recent than x days ago
  'durationGte': "durationGte_example", // String | duration_gte
  'durationLte': "durationLte_example", // String | duration_lte
  'language': "language_example", // String | language
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'ordering': "ordering_example", // String | Which field to use when ordering the results.
  'search': "search_example", // String | Search string
  'showAllMyVideos': "showAllMyVideos_example", // String | Show all my videos in search
  'videoId': "videoId_example", // String | video_id
  'viewsGte': "viewsGte_example", // String | views_gte
  'viewsLte': "viewsLte_example" // String | views_lte
};
apiInstance.videosList(opts, (error, data, response) => {
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
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] 
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] 
 **durationGte** | **String**| duration_gte | [optional] 
 **durationLte** | **String**| duration_lte | [optional] 
 **language** | **String**| language | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **ordering** | **String**| Which field to use when ordering the results. | [optional] 
 **search** | **String**| Search string | [optional] 
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] 
 **videoId** | **String**| video_id | [optional] 
 **viewsGte** | **String**| views_gte | [optional] 
 **viewsLte** | **String**| views_lte | [optional] 

### Return type

[**PaginatedVideoSerializerV2List**](PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videosRatedVideosList

> PaginatedVideoSerializerV2List videosRatedVideosList(opts)



Get videos and search results.

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

let apiInstance = new TournesolApi.VideosApi();
let opts = {
  'daysAgoGte': "daysAgoGte_example", // String | Upload date, older than x days ago
  'daysAgoLte': "daysAgoLte_example", // String | Upload date, more recent than x days ago
  'durationGte': "durationGte_example", // String | duration_gte
  'durationLte': "durationLte_example", // String | duration_lte
  'language': "language_example", // String | language
  'limit': 56, // Number | Number of results to return per page.
  'offset': 56, // Number | The initial index from which to return the results.
  'ordering': "ordering_example", // String | Which field to use when ordering the results.
  'search': "search_example", // String | Search string
  'showAllMyVideos': "showAllMyVideos_example", // String | Show all my videos in search
  'videoId': "videoId_example", // String | video_id
  'viewsGte': "viewsGte_example", // String | views_gte
  'viewsLte': "viewsLte_example" // String | views_lte
};
apiInstance.videosRatedVideosList(opts, (error, data, response) => {
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
 **daysAgoGte** | **String**| Upload date, older than x days ago | [optional] 
 **daysAgoLte** | **String**| Upload date, more recent than x days ago | [optional] 
 **durationGte** | **String**| duration_gte | [optional] 
 **durationLte** | **String**| duration_lte | [optional] 
 **language** | **String**| language | [optional] 
 **limit** | **Number**| Number of results to return per page. | [optional] 
 **offset** | **Number**| The initial index from which to return the results. | [optional] 
 **ordering** | **String**| Which field to use when ordering the results. | [optional] 
 **search** | **String**| Search string | [optional] 
 **showAllMyVideos** | **String**| Show all my videos in search | [optional] 
 **videoId** | **String**| video_id | [optional] 
 **viewsGte** | **String**| views_gte | [optional] 
 **viewsLte** | **String**| views_lte | [optional] 

### Return type

[**PaginatedVideoSerializerV2List**](PaginatedVideoSerializerV2List.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## videosRetrieve

> VideoSerializerV2 videosRetrieve(id)



Get one video by internal ID

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

let apiInstance = new TournesolApi.VideosApi();
let id = 56; // Number | A unique integer value identifying this video.
apiInstance.videosRetrieve(id, (error, data, response) => {
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
 **id** | **Number**| A unique integer value identifying this video. | 

### Return type

[**VideoSerializerV2**](VideoSerializerV2.md)

### Authorization

[cookieAuth](../README.md#cookieAuth), [tokenAuth](../README.md#tokenAuth)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

