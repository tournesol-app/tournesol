# Documentation for Tournesol API

<a name="documentation-for-api-endpoints"></a>
## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*ConstantsApi* | [**viewConstants**](Apis/ConstantsApi.md#viewconstants) | **GET** /api/v2/constants/view_constants/ | Get constants.
*EmailDomainApi* | [**emailDomainList**](Apis/EmailDomainApi.md#emaildomainlist) | **GET** /api/v2/email_domain/ | List e-mail domains
*EmailDomainApi* | [**emailDomainRetrieve**](Apis/EmailDomainApi.md#emaildomainretrieve) | **GET** /api/v2/email_domain/{id}/ | Get e-mail domain
*ExpertRatingsApi* | [**apiV2ExpertRatingsDoubleDown**](Apis/ExpertRatingsApi.md#apiv2expertratingsdoubledown) | **PATCH** /api/v2/expert_ratings/double_down/ | Double the weight of one of the ratings on one of the features.
*ExpertRatingsApi* | [**apiV2ExpertRatingsSampleVideo**](Apis/ExpertRatingsApi.md#apiv2expertratingssamplevideo) | **GET** /api/v2/expert_ratings/sample_video/ | Sample a video to rate.
*ExpertRatingsApi* | [**apiV2ExpertRatingsShowInconsistencies**](Apis/ExpertRatingsApi.md#apiv2expertratingsshowinconsistencies) | **GET** /api/v2/expert_ratings/inconsistencies/ | Get inconsistencies in Expert Ratings.
*ExpertRatingsApi* | [**disagreements**](Apis/ExpertRatingsApi.md#disagreements) | **GET** /api/v2/expert_ratings/disagreements/ | Get disagreements in Expert Ratings.
*ExpertRatingsApi* | [**expertRatingsByVideoIdsPartialUpdate**](Apis/ExpertRatingsApi.md#expertratingsbyvideoidspartialupdate) | **PATCH** /api/v2/expert_ratings/by_video_ids/ | Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.
*ExpertRatingsApi* | [**expertRatingsByVideoIdsRetrieve**](Apis/ExpertRatingsApi.md#expertratingsbyvideoidsretrieve) | **GET** /api/v2/expert_ratings/by_video_ids/ | Get/set ratings by video IDs, with reverse order (v1-v2 and v2-v1) supported.
*ExpertRatingsApi* | [**expertRatingsCreate**](Apis/ExpertRatingsApi.md#expertratingscreate) | **POST** /api/v2/expert_ratings/ | Rate two videos
*ExpertRatingsApi* | [**expertRatingsList**](Apis/ExpertRatingsApi.md#expertratingslist) | **GET** /api/v2/expert_ratings/ | List my own expert ratings
*ExpertRatingsApi* | [**expertRatingsOnlineByVideoIdsPartialUpdate**](Apis/ExpertRatingsApi.md#expertratingsonlinebyvideoidspartialupdate) | **PATCH** /api/v2/expert_ratings/online_by_video_ids/ | Do online updates on ratings.
*ExpertRatingsApi* | [**expertRatingsOnlineByVideoIdsRetrieve**](Apis/ExpertRatingsApi.md#expertratingsonlinebyvideoidsretrieve) | **GET** /api/v2/expert_ratings/online_by_video_ids/ | Do online updates on ratings.
*ExpertRatingsApi* | [**expertRatingsPartialUpdate**](Apis/ExpertRatingsApi.md#expertratingspartialupdate) | **PATCH** /api/v2/expert_ratings/{id}/ | Change some fields in a rating
*ExpertRatingsApi* | [**expertRatingsRetrieve**](Apis/ExpertRatingsApi.md#expertratingsretrieve) | **GET** /api/v2/expert_ratings/{id}/ | Set and get expert ratings.
*ExpertRatingsApi* | [**expertRatingsSampleFirstVideoRetrieve**](Apis/ExpertRatingsApi.md#expertratingssamplefirstvideoretrieve) | **GET** /api/v2/expert_ratings/sample_first_video/ | Sample a video to rate.
*ExpertRatingsApi* | [**expertRatingsSamplePopularVideoRetrieve**](Apis/ExpertRatingsApi.md#expertratingssamplepopularvideoretrieve) | **GET** /api/v2/expert_ratings/sample_popular_video/ | Sample a popular video.
*ExpertRatingsApi* | [**expertRatingsSampleVideoWithOtherRetrieve**](Apis/ExpertRatingsApi.md#expertratingssamplevideowithotherretrieve) | **GET** /api/v2/expert_ratings/sample_video_with_other/ | Sample a video to rate.
*ExpertRatingsApi* | [**expertRatingsSkipVideoPartialUpdate**](Apis/ExpertRatingsApi.md#expertratingsskipvideopartialupdate) | **PATCH** /api/v2/expert_ratings/skip_video/ | Set and get expert ratings.
*ExpertRatingsApi* | [**expertRatingsUpdate**](Apis/ExpertRatingsApi.md#expertratingsupdate) | **PUT** /api/v2/expert_ratings/{id}/ | Change all fields in a rating
*ExpertRatingsApi* | [**registerSliderChange**](Apis/ExpertRatingsApi.md#registersliderchange) | **POST** /api/v2/expert_ratings/register_slider_change/ | Register any change in slider values on the rating page.
*LoginSignupApi* | [**loginSignupChangePasswordPartialUpdate**](Apis/LoginSignupApi.md#loginsignupchangepasswordpartialupdate) | **PATCH** /api/v2/login_signup/change_password/ | Change password
*LoginSignupApi* | [**loginSignupList**](Apis/LoginSignupApi.md#loginsignuplist) | **GET** /api/v2/login_signup/ | Get my username in a list
*LoginSignupApi* | [**loginSignupLoginPartialUpdate**](Apis/LoginSignupApi.md#loginsignuploginpartialupdate) | **PATCH** /api/v2/login_signup/login/ | Register a user.
*LoginSignupApi* | [**loginSignupLogoutPartialUpdate**](Apis/LoginSignupApi.md#loginsignuplogoutpartialupdate) | **PATCH** /api/v2/login_signup/logout/ | Log out.
*LoginSignupApi* | [**loginSignupPartialUpdate**](Apis/LoginSignupApi.md#loginsignuppartialupdate) | **PATCH** /api/v2/login_signup/{id}/ | Update my username
*LoginSignupApi* | [**loginSignupRegisterCreate**](Apis/LoginSignupApi.md#loginsignupregistercreate) | **POST** /api/v2/login_signup/register/ | Register a user.
*LoginSignupApi* | [**loginSignupResetPasswordPartialUpdate**](Apis/LoginSignupApi.md#loginsignupresetpasswordpartialupdate) | **PATCH** /api/v2/login_signup/reset_password/ | Reset password.
*LoginSignupApi* | [**loginSignupRetrieve**](Apis/LoginSignupApi.md#loginsignupretrieve) | **GET** /api/v2/login_signup/{id}/ | Get my username by my user preferences id
*LoginSignupApi* | [**loginSignupUpdate**](Apis/LoginSignupApi.md#loginsignupupdate) | **PUT** /api/v2/login_signup/{id}/ | Update my username
*RateLaterApi* | [**rateLaterBulkDeletePartialUpdate**](Apis/RateLaterApi.md#ratelaterbulkdeletepartialupdate) | **PATCH** /api/v2/rate_later/bulk_delete/ | Delete many videos from the list by IDs.
*RateLaterApi* | [**rateLaterCreate**](Apis/RateLaterApi.md#ratelatercreate) | **POST** /api/v2/rate_later/ | Schedule a video to be rated later
*RateLaterApi* | [**rateLaterDestroy**](Apis/RateLaterApi.md#ratelaterdestroy) | **DELETE** /api/v2/rate_later/{id}/ | Remove a video from rate later list
*RateLaterApi* | [**rateLaterList**](Apis/RateLaterApi.md#ratelaterlist) | **GET** /api/v2/rate_later/ | Get videos queued to be rated later
*RateLaterApi* | [**rateLaterRetrieve**](Apis/RateLaterApi.md#ratelaterretrieve) | **GET** /api/v2/rate_later/{id}/ | Get one video to be rated later (by object ID)
*StatisticsApi* | [**view**](Apis/StatisticsApi.md#view) | **GET** /api/v2/statistics/view/ | Get statistics for the website.
*UserInformationApi* | [**userInformationAddVerifyEmailPartialUpdate**](Apis/UserInformationApi.md#userinformationaddverifyemailpartialupdate) | **PATCH** /api/v2/user_information/{id}/add_verify_email/ | Add an address and ask for verification.
*UserInformationApi* | [**userInformationList**](Apis/UserInformationApi.md#userinformationlist) | **GET** /api/v2/user_information/ | List and filter user information
*UserInformationApi* | [**userInformationPartialUpdate**](Apis/UserInformationApi.md#userinformationpartialupdate) | **PATCH** /api/v2/user_information/{id}/ | Partially update my user information
*UserInformationApi* | [**userInformationPublicModelsList**](Apis/UserInformationApi.md#userinformationpublicmodelslist) | **GET** /api/v2/user_information/public_models/ | Ask for e-mail verification for all unverified e-mails.
*UserInformationApi* | [**userInformationRetrieve**](Apis/UserInformationApi.md#userinformationretrieve) | **GET** /api/v2/user_information/{id}/ | Get information about one user
*UserInformationApi* | [**userInformationSearchExpertiseList**](Apis/UserInformationApi.md#userinformationsearchexpertiselist) | **GET** /api/v2/user_information/search_expertise/ | Get and set my UserInformation.
*UserInformationApi* | [**userInformationSearchUsernameList**](Apis/UserInformationApi.md#userinformationsearchusernamelist) | **GET** /api/v2/user_information/search_username/ | Get and set my UserInformation.
*UserInformationApi* | [**userInformationUpdate**](Apis/UserInformationApi.md#userinformationupdate) | **PUT** /api/v2/user_information/{id}/ | Replace my user information
*UserInformationApi* | [**userInformationVerifyAllEmailsPartialUpdate**](Apis/UserInformationApi.md#userinformationverifyallemailspartialupdate) | **PATCH** /api/v2/user_information/{id}/verify_all_emails/ | Ask for e-mail verification for all unverified e-mails.
*UserInformationApi* | [**userInformationVerifyEmailPartialUpdate**](Apis/UserInformationApi.md#userinformationverifyemailpartialupdate) | **PATCH** /api/v2/user_information/{id}/verify_email/ | Ask for e-mail verification.
*UserPreferencesApi* | [**userPreferencesList**](Apis/UserPreferencesApi.md#userpreferenceslist) | **GET** /api/v2/user_preferences/ | Show my user preferences in a list
*UserPreferencesApi* | [**userPreferencesMyPartialUpdate**](Apis/UserPreferencesApi.md#userpreferencesmypartialupdate) | **PATCH** /api/v2/user_preferences/my/ | Get/set my own user preferences.
*UserPreferencesApi* | [**userPreferencesMyRetrieve**](Apis/UserPreferencesApi.md#userpreferencesmyretrieve) | **GET** /api/v2/user_preferences/my/ | Get/set my own user preferences.
*UserPreferencesApi* | [**userPreferencesPartialUpdate**](Apis/UserPreferencesApi.md#userpreferencespartialupdate) | **PATCH** /api/v2/user_preferences/{id}/ | Change some fields in user preferences
*UserPreferencesApi* | [**userPreferencesRetrieve**](Apis/UserPreferencesApi.md#userpreferencesretrieve) | **GET** /api/v2/user_preferences/{id}/ | Get user preferences
*UserPreferencesApi* | [**userPreferencesUpdate**](Apis/UserPreferencesApi.md#userpreferencesupdate) | **PUT** /api/v2/user_preferences/{id}/ | Change all fields in user preferences
*VideoCommentsApi* | [**apiV2VideoCommentsSetMark**](Apis/VideoCommentsApi.md#apiv2videocommentssetmark) | **POST** /api/v2/video_comments/{id}/set_mark/ | Mark a comment with a flag (like/dislike/red flag).
*VideoCommentsApi* | [**videoCommentsCreate**](Apis/VideoCommentsApi.md#videocommentscreate) | **POST** /api/v2/video_comments/ | Comment on a video
*VideoCommentsApi* | [**videoCommentsList**](Apis/VideoCommentsApi.md#videocommentslist) | **GET** /api/v2/video_comments/ | List and filter comments
*VideoCommentsApi* | [**videoCommentsPartialUpdate**](Apis/VideoCommentsApi.md#videocommentspartialupdate) | **PATCH** /api/v2/video_comments/{id}/ | Change some fields in a comment
*VideoCommentsApi* | [**videoCommentsRetrieve**](Apis/VideoCommentsApi.md#videocommentsretrieve) | **GET** /api/v2/video_comments/{id}/ | Get one comment
*VideoCommentsApi* | [**videoCommentsUpdate**](Apis/VideoCommentsApi.md#videocommentsupdate) | **PUT** /api/v2/video_comments/{id}/ | Change all fields in a comment
*VideoRatingsApi* | [**videoRatingStatistics**](Apis/VideoRatingsApi.md#videoratingstatistics) | **GET** /api/v2/video_ratings/video_rating_statistics/ | Get statistical data on video ratings.
*VideoRatingsApi* | [**videoRatingsList**](Apis/VideoRatingsApi.md#videoratingslist) | **GET** /api/v2/video_ratings/ | Get my video ratings (predictions of my algorithmic representative)
*VideoRatingsApi* | [**videoRatingsRetrieve**](Apis/VideoRatingsApi.md#videoratingsretrieve) | **GET** /api/v2/video_ratings/{id}/ | Get one video rating (predictions of my algorithmic representative)
*VideoReportsApi* | [**videoReportsCreate**](Apis/VideoReportsApi.md#videoreportscreate) | **POST** /api/v2/video_reports/ | Report a video
*VideoReportsApi* | [**videoReportsList**](Apis/VideoReportsApi.md#videoreportslist) | **GET** /api/v2/video_reports/ | Show all anonymized video reports
*VideoReportsApi* | [**videoReportsPartialUpdate**](Apis/VideoReportsApi.md#videoreportspartialupdate) | **PATCH** /api/v2/video_reports/{id}/ | Change some fields in a video report
*VideoReportsApi* | [**videoReportsRetrieve**](Apis/VideoReportsApi.md#videoreportsretrieve) | **GET** /api/v2/video_reports/{id}/ | Get one video report
*VideoReportsApi* | [**videoReportsUpdate**](Apis/VideoReportsApi.md#videoreportsupdate) | **PUT** /api/v2/video_reports/{id}/ | Change all fields in a video report
*VideosApi* | [**apiV2VideoSearchTournesol**](Apis/VideosApi.md#apiv2videosearchtournesol) | **GET** /api/v2/videos/search_tournesol/ | Search videos using the Tournesol algorithm.
*VideosApi* | [**apiV2VideoSearchYoutube**](Apis/VideosApi.md#apiv2videosearchyoutube) | **GET** /api/v2/videos/search_youtube/ | Search videos using the YouTube algorithm.
*VideosApi* | [**myRatingsArePrivate**](Apis/VideosApi.md#myratingsareprivate) | **GET** /api/v2/videos/my_ratings_are_private/ | Are my ratings private?
*VideosApi* | [**nThanks**](Apis/VideosApi.md#nthanks) | **GET** /api/v2/videos/n_thanks/ | Get number of people I thanked for a video.
*VideosApi* | [**setAllRatingPrivacy**](Apis/VideosApi.md#setallratingprivacy) | **PATCH** /api/v2/videos/set_all_rating_privacy/ | Set all video rating privacy.
*VideosApi* | [**setRatingPrivacy**](Apis/VideosApi.md#setratingprivacy) | **PATCH** /api/v2/videos/set_rating_privacy/ | Set video rating privacy.
*VideosApi* | [**thankContributors**](Apis/VideosApi.md#thankcontributors) | **PATCH** /api/v2/videos/thank_contributors/ | Thank contributors for the video.
*VideosApi* | [**videosCreate**](Apis/VideosApi.md#videoscreate) | **POST** /api/v2/videos/ | Add a video to the database (without filling the fields) from Youtube
*VideosApi* | [**videosList**](Apis/VideosApi.md#videoslist) | **GET** /api/v2/videos/ | List all videos with search/filter capability
*VideosApi* | [**videosRetrieve**](Apis/VideosApi.md#videosretrieve) | **GET** /api/v2/videos/{id}/ | Get one video by internal ID


<a name="documentation-for-models"></a>
## Documentation for Models

 - [ConstantsSerializerV2](.//Models/ConstantsSerializerV2.md)
 - [ContextEnum](.//Models/ContextEnum.md)
 - [Degree](.//Models/Degree.md)
 - [DegreeOfPoliticalEngagementEnum](.//Models/DegreeOfPoliticalEngagementEnum.md)
 - [Disagreement](.//Models/Disagreement.md)
 - [EmailDomain](.//Models/EmailDomain.md)
 - [ExpertRatingsSerializerV2](.//Models/ExpertRatingsSerializerV2.md)
 - [Expertise](.//Models/Expertise.md)
 - [ExpertiseKeyword](.//Models/ExpertiseKeyword.md)
 - [Feature](.//Models/Feature.md)
 - [GenderEnum](.//Models/GenderEnum.md)
 - [GenericError](.//Models/GenericError.md)
 - [GenericErrorDetailEnum](.//Models/GenericErrorDetailEnum.md)
 - [Inconsistencies](.//Models/Inconsistencies.md)
 - [MoralPhilosophyEnum](.//Models/MoralPhilosophyEnum.md)
 - [NationalityEnum](.//Models/NationalityEnum.md)
 - [NumberOfThanks](.//Models/NumberOfThanks.md)
 - [OnlineResponse](.//Models/OnlineResponse.md)
 - [OnlyUsername](.//Models/OnlyUsername.md)
 - [OnlyUsernameAndID](.//Models/OnlyUsernameAndID.md)
 - [PaginatedDisagreementList](.//Models/PaginatedDisagreementList.md)
 - [PaginatedEmailDomainList](.//Models/PaginatedEmailDomainList.md)
 - [PaginatedExpertRatingsSerializerV2List](.//Models/PaginatedExpertRatingsSerializerV2List.md)
 - [PaginatedExpertiseList](.//Models/PaginatedExpertiseList.md)
 - [PaginatedInconsistenciesList](.//Models/PaginatedInconsistenciesList.md)
 - [PaginatedOnlyUsernameAndIDList](.//Models/PaginatedOnlyUsernameAndIDList.md)
 - [PaginatedOnlyUsernameList](.//Models/PaginatedOnlyUsernameList.md)
 - [PaginatedUserInformationPublicSerializerV2List](.//Models/PaginatedUserInformationPublicSerializerV2List.md)
 - [PaginatedUserPreferencesSerializerV2List](.//Models/PaginatedUserPreferencesSerializerV2List.md)
 - [PaginatedVerifiableEmailList](.//Models/PaginatedVerifiableEmailList.md)
 - [PaginatedVideoCommentsSerializerV2List](.//Models/PaginatedVideoCommentsSerializerV2List.md)
 - [PaginatedVideoRateLaterSerializerV2List](.//Models/PaginatedVideoRateLaterSerializerV2List.md)
 - [PaginatedVideoRatingsSerializerV2List](.//Models/PaginatedVideoRatingsSerializerV2List.md)
 - [PaginatedVideoRatingsStatisticsSerializerV2List](.//Models/PaginatedVideoRatingsStatisticsSerializerV2List.md)
 - [PaginatedVideoReportsSerializerV2List](.//Models/PaginatedVideoReportsSerializerV2List.md)
 - [PaginatedVideoSerializerV2List](.//Models/PaginatedVideoSerializerV2List.md)
 - [PatchedChangePassword](.//Models/PatchedChangePassword.md)
 - [PatchedDegree](.//Models/PatchedDegree.md)
 - [PatchedExpertRatingsSerializerV2](.//Models/PatchedExpertRatingsSerializerV2.md)
 - [PatchedExpertise](.//Models/PatchedExpertise.md)
 - [PatchedExpertiseKeyword](.//Models/PatchedExpertiseKeyword.md)
 - [PatchedLogin](.//Models/PatchedLogin.md)
 - [PatchedOnlyUsernameAndID](.//Models/PatchedOnlyUsernameAndID.md)
 - [PatchedResetPassword](.//Models/PatchedResetPassword.md)
 - [PatchedUserInformationPublicSerializerV2](.//Models/PatchedUserInformationPublicSerializerV2.md)
 - [PatchedUserPreferencesSerializerV2](.//Models/PatchedUserPreferencesSerializerV2.md)
 - [PatchedVerifiableEmail](.//Models/PatchedVerifiableEmail.md)
 - [PatchedVideo](.//Models/PatchedVideo.md)
 - [PatchedVideoCommentsSerializerV2](.//Models/PatchedVideoCommentsSerializerV2.md)
 - [PatchedVideoRateLaterDelete](.//Models/PatchedVideoRateLaterDelete.md)
 - [PatchedVideoReportsSerializerV2](.//Models/PatchedVideoReportsSerializerV2.md)
 - [PoliticalAffiliationEnum](.//Models/PoliticalAffiliationEnum.md)
 - [PrivateOrPublic](.//Models/PrivateOrPublic.md)
 - [RaceEnum](.//Models/RaceEnum.md)
 - [RatingModeEnum](.//Models/RatingModeEnum.md)
 - [Register](.//Models/Register.md)
 - [ReligionEnum](.//Models/ReligionEnum.md)
 - [ReportField](.//Models/ReportField.md)
 - [ResidenceEnum](.//Models/ResidenceEnum.md)
 - [Samplevideov3Error](.//Models/Samplevideov3Error.md)
 - [Samplevideov3ErrorDetailEnum](.//Models/Samplevideov3ErrorDetailEnum.md)
 - [SingleFeatureRating](.//Models/SingleFeatureRating.md)
 - [SliderChangeSerializerV2](.//Models/SliderChangeSerializerV2.md)
 - [StatisticsSerializerV2](.//Models/StatisticsSerializerV2.md)
 - [StatusEnum](.//Models/StatusEnum.md)
 - [UserInformationPublicSerializerV2](.//Models/UserInformationPublicSerializerV2.md)
 - [UserInformationSerializerNameOnly](.//Models/UserInformationSerializerNameOnly.md)
 - [UserPreferencesSerializerV2](.//Models/UserPreferencesSerializerV2.md)
 - [VerifiableEmail](.//Models/VerifiableEmail.md)
 - [VideoCommentsSerializerV2](.//Models/VideoCommentsSerializerV2.md)
 - [VideoRateLaterSerializerV2](.//Models/VideoRateLaterSerializerV2.md)
 - [VideoRatingsSerializerV2](.//Models/VideoRatingsSerializerV2.md)
 - [VideoRatingsStatisticsSerializerV2](.//Models/VideoRatingsStatisticsSerializerV2.md)
 - [VideoReportsSerializerV2](.//Models/VideoReportsSerializerV2.md)
 - [VideoSerializerV2](.//Models/VideoSerializerV2.md)


<a name="documentation-for-authorization"></a>
## Documentation for Authorization

<a name="cookieAuth"></a>
### cookieAuth

- **Type**: API key
- **API key parameter name**: Session
- **Location**: 

<a name="tokenAuth"></a>
### tokenAuth

- **Type**: HTTP basic authentication

