# VideoSerializerV2
## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**Integer**](integer.md) |  | [default to null]
**videoUnderscoreid** | [**String**](string.md) | Video ID from YouTube URL, matches ^[A-Za-z0-9-_]+$ | [default to null]
**score** | [**Float**](float.md) | Computed video score. | [default to 0.0]
**name** | [**String**](string.md) | Video Title | [default to null]
**duration** | [**String**](string.md) | Video Duration | [default to null]
**language** | [**String**](string.md) | Language as str. | [default to null]
**publicationUnderscoredate** | [**date**](date.md) | When the video was published | [default to null]
**views** | [**Integer**](integer.md) | Number of views | [default to null]
**uploader** | [**String**](string.md) | Name of the channel (uploader) | [default to null]
**scoreUnderscorepreferencesUnderscoreterm** | [**Float**](float.md) | Computed video score [preferences]. | [default to 0.0]
**scoreUnderscoresearchUnderscoreterm** | [**Float**](float.md) | Computed video score [search]. | [default to 0.0]
**ratingUnderscorenUnderscoreexperts** | [**Integer**](integer.md) | Number of experts in ratings | [default to null]
**ratingUnderscorenUnderscoreratings** | [**Integer**](integer.md) | Number of ratings | [default to null]
**nUnderscorereports** | [**Integer**](integer.md) | Number of times video was reported | [default to null]
**publicUnderscoreexperts** | [**List**](UserInformationSerializerNameOnly.md) | First 10 public contributors | [default to null]
**nUnderscorepublicUnderscoreexperts** | [**Integer**](integer.md) | Number of public contributors | [default to null]
**nUnderscoreprivateUnderscoreexperts** | [**Integer**](integer.md) | Number private contributors | [default to null]
**paretoUnderscoreoptimal** | [**Boolean**](boolean.md) | Is this video pareto-optimal? | [default to null]
**reliability** | [**Float**](float.md) | Reliable and not misleading | [default to null]
**importance** | [**Float**](float.md) | Important and actionable | [default to null]
**engaging** | [**Float**](float.md) | Engaging and thought-provoking | [default to null]
**pedagogy** | [**Float**](float.md) | Clear and pedagogical | [default to null]
**laymanUnderscorefriendly** | [**Float**](float.md) | Layman-friendly | [default to null]
**diversityUnderscoreinclusion** | [**Float**](float.md) | Diversity and Inclusion | [default to null]
**backfireUnderscorerisk** | [**Float**](float.md) | Resilience to backfiring risks | [default to null]
**betterUnderscorehabits** | [**Float**](float.md) | Encourages better habits | [default to null]
**entertainingUnderscorerelaxing** | [**Float**](float.md) | Entertaining and relaxing | [default to null]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

