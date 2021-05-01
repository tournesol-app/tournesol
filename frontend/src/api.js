import jQuery from 'jquery';

const camelcaseKeys = require('camelcase-keys');
const toJsonSchema = require('@openapi-contrib/openapi-schema-to-json-schema');

// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

// https://www.techiediaries.com/django-react-forms-csrf-axios/:
// Returns a cookie by name
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = jQuery.trim(cookies[i]);
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function getApiV2Client() {
  // Returns the API v2 client with proper authentication with Django

  // Obtaining the Django CSRF token for form submissions
  /* eslint-disable global-require */
  const TournesolApi = require('../api/src');
  /* eslint-enable global-require */
  const defaultClient = TournesolApi.ApiClient.instance;
  defaultClient.basePath = window.location.origin;
  const { cookieAuth } = defaultClient.authentications;
  cookieAuth.apiKey = csrftoken;
  cookieAuth.in = 'header';
  cookieAuth.name = 'X-CSRFToken';
  return TournesolApi;
}

// Obtaining the API.
export const TournesolAPI = getApiV2Client();

// format error returned by the API
export const formatError = (err) => `${err.toString()} ${err.response.text}`;

// iterate over the dictionary
// callback(object, key)
export function recursiveIterDict(o, callback) {
  Object.keys(o).forEach((k) => {
    if (o[k] !== null && typeof o[k] === 'object') {
      recursiveIterDict(o[k], callback);
    }
    callback(o, k);
  });
}

// transform undefined to null to allow for deleting fields
export function undefinedToNullValue(data) {
  recursiveIterDict(data, (o, k) => {
    if (o[k] === undefined) {
      o[k] = null; // eslint-disable-line no-param-reassign
    }
  });
  return data;
}

export function errorToJsonError(err) {
  const errJson = JSON.parse(err.response.text);
  recursiveIterDict(errJson, (o, k) => {
    if (Array.isArray(o[k]) && o[k].length > 0 && typeof o[k][0] === 'string') {
      o[k] = { __errors: o[k] }; // eslint-disable-line no-param-reassign
    }
  });
  return errJson;
}

// download URL and convert to b64 data URL
// https://gist.github.com/oliyh/db3d1a582aefe6d8fee9
export const urlToDataURL = (urlOrig, name = null) =>
  new Promise((resolve, reject) => {
    // http -> https

    let url;
    if (
      window.location.protocol.startsWith('https') &&
      urlOrig &&
      urlOrig.startsWith('http:')
    ) {
      url = urlOrig.replace('http://', 'https://');
    } else {
      url = urlOrig;
    }

    const xmlHTTP = new XMLHttpRequest();
    xmlHTTP.open('GET', url, true);

    if (!url) {
      reject(new Error('Please provide a url'));
    }

    xmlHTTP.responseType = 'arraybuffer';
    xmlHTTP.onload = function onload() {
      const arr = new Uint8Array(this.response);
      const contentType = this.getResponseHeader('content-type');

      // https://gist.github.com/jonleighton/958841
      // TODO: replace with a faster library call instead of JS loop
      function uint8ToBase64(buffer) {
        let binary = '';
        const len = buffer.byteLength;
        for (let i = 0; i < len; i += 1) {
          binary += String.fromCharCode(buffer[i]);
        }
        return window.btoa(binary);
      }
      // var raw = new TextDecoder("utf-8").decode(arr);
      // var b64 = btoa(raw);
      const b64 = uint8ToBase64(arr);
      let basename;
      if (name === null) {
        [basename] = url.split('/').reverse();
      } else {
        basename = name;
      }
      const dataURL = `data:${contentType};filename=${basename};base64,${b64}`;
      resolve(dataURL);
    };
    xmlHTTP.onerror = function error() {
      reject(new Error('Request failed'));
    };
    xmlHTTP.send();
  });

/// get a JSON froa a given URL
export const getJSON = (url) =>
  new Promise((resolve, reject) => {
    const xmlHTTP = new XMLHttpRequest();
    xmlHTTP.open('GET', url, true);
    xmlHTTP.setRequestHeader('Accept', 'application/json');
    xmlHTTP.setRequestHeader('X-CSRFToken', csrftoken);
    xmlHTTP.responseType = 'json';
    xmlHTTP.onload = function onload() {
      resolve(this.response);
    };
    xmlHTTP.onerror = function onerror() {
      reject(new Error('Request failed'));
    };
    xmlHTTP.send();
  });

/// Get tournesol API schema
export const getSchema = () => getJSON('/static/schema.json');

// convert from OpenAPI schema to JSONSchema
export function fromOpenAPIToJsonSchema(apiSchema) {
  const formJSON = toJsonSchema(apiSchema, { keepNotSupported: ['readOnly'] });
  delete formJSON.$schema;
  recursiveIterDict(formJSON, (o, k) => {
    // description to title
    if (k === 'description') {
      o.title = o[k]; // eslint-disable-line no-param-reassign
      delete o[k]; // eslint-disable-line no-param-reassign
    }
  });
  return formJSON;
}

// API call to get videos in EXPERT interface
export const GET_VIDEO_FOR_COMPARISON = (onlyRated, callback) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  // callback(video.video_id)
  api.apiV2ExpertRatingsSampleVideo({ onlyRated }, (_err, data, _resp) =>
    callback(data.video_id),
  );
};

// Writes a new entry in the database table ExpertRating
//
// comparison has type:
// {
//   video_1: string,
//   video_2: string,
//   [featureNames]: 0 <= number <= 100,
// }
export const SUBMIT_COMPARISON_RESULT = (
  user,
  comparison,
  callback,
  callbackSuccess = null,
) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.expertRatingsCreate(comparison, (err, _data, _resp) => {
    if (err) callback(formatError(err));
    else if (callbackSuccess) {
      callbackSuccess();
    }
  });
};

// This API call updates on comparison submitted by an expert
//
// comparison has type:
// {
//   video_1: string,
//   video_2: string,
//   feature: string,
//   score: 0 <= number <= 100
// }
export const UPDATE_COMPARISON = (
  comparison,
  callback,
  callbackSuccess = null,
) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.expertRatingsByVideoIdsPartialUpdate(
    comparison.video_1,
    comparison.video_2,
    { patchedExpertRatingsSerializerV2: comparison },
    (err, data, _resp) => {
      window.err = err;
      if (!data) callback(formatError(err));
      else if (callbackSuccess) {
        callbackSuccess();
      }
    },
  );
};

export const GET_COMPARISON_RATING = (
  videoLeft,
  videoRight,
  callbackSuccess,
  callbackFail,
) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.expertRatingsByVideoIdsRetrieve(
    videoLeft,
    videoRight,
    {},
    (error, data, _resp) => {
      if (!error) callbackSuccess(data);
      else callbackFail();
    },
  );
};

// API call to set USER preferences
export const SET_PREFERENCES = (preferences_, callback) => {
  const api = new TournesolAPI.UserPreferencesApi();
  api.userPreferencesMyPartialUpdate(
    { patchedUserPreferencesSerializerV2: preferences_ },
    (_err, data, _resp) => callback(data),
  );
};

export const GET_PREFERENCES = (callback) => {
  const api = new TournesolAPI.UserPreferencesApi();
  api.userPreferencesMyRetrieve((_err, data, _resp) => callback(data));
};

// API call to query a list of videos to recommend for a USER
export const GET_TOP_RECOMMENDATION = (preferences, options, callback) => {
  const api = new TournesolAPI.VideosApi();
  SET_PREFERENCES(preferences, () => {
    if (options.searchYTRaw === 'true') {
      api.apiV2VideoSearchYoutube(options.search, {}, (_err, data, _resp) =>
        callback(data.results),
      );
    } else {
      api.apiV2VideoSearchTournesol(
        { ...options, ...camelcaseKeys(preferences) },
        (_err, data, _resp) => callback(data.results),
      );
    }
  });
};

// API call to add a new video as an EXPERT
export const SUBMIT_VIDEO = (videoId, callbackSuccess, callbackFail) => {
  const api = new TournesolAPI.VideosApi();
  api.videosCreate({ video_id: videoId }, (err, data, _resp) => {
    if (err) callbackFail(formatError(err));
    else callbackSuccess(data);
  });
};

// API call to report VIDEOS
export const REPORT_VIDEO = (videoId, info, callbackSuccess, callbackFail) => {
  const api = new TournesolAPI.VideoReportsApi();
  api.videoReportsCreate(
    TournesolAPI.VideoReportsSerializerV2.constructFromObject({
      ...info,
      video: videoId,
    }),
    (err, data, _resp) => {
      if (err) callbackFail(formatError(err));
      else callbackSuccess(data);
    },
  );
};

// API call to query a list of all videos
export const GET_ALL_VIDEOS = (callback) => {
  const api = new TournesolAPI.VideosApi();
  api.videosList({}, (_err, data, _resp) => callback(data.results));
};

// API call to query a specific video
export const GET_VIDEO = (videoId, callback) => {
  const api = new TournesolAPI.VideosApi();
  api.videosList({ videoId }, (_err, data, _resp) => {
    if (data.results[0]) callback(data.results[0]);
    else callback(null);
  });
};

// API call to get comments
export const GET_COMMENTS = (videoId, callback, parentComment = null) => {
  const api = new TournesolAPI.VideoCommentsApi();
  api.videoCommentsList(
    { videoVideoId: videoId, parentComment },
    (_err, data, _resp) => callback(data.results),
  );
};

// API call to get reports
export const GET_REPORTS = (videoId, callback) => {
  const api = new TournesolAPI.VideoReportsApi();
  api.videoReportsList({ videoVideoId: videoId }, (_err, data, _resp) =>
    callback(data.results),
  );
};

// API call to get ratings for videos
export const GET_SINGLE_VIDEO_RATINGS = (callback, options = {}) => {
  const api = new TournesolAPI.VideoRatingsApi();
  api.videoRatingsList(options, (_err, data, _resp) => callback(data.results));
};

// API call to get ratings for videos
export const GET_COMPARISON_RATINGS = (callback, options = {}) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.expertRatingsList(options, (_err, data, _resp) => callback(data.results));
};

// API call to get cyclic inconsistencies
export const GET_CYCLIC_INCONSISTENCIES = (username, callback) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.apiV2ExpertRatingsShowInconsistencies({}, (_err, data, _resp) =>
    callback(data.results),
  );
};

// API call to submit a comment
export const SUBMIT_COMMENT = (options, callbackSuccess, callbackFail) => {
  const api = new TournesolAPI.VideoCommentsApi();
  api.videoCommentsCreate(
    TournesolAPI.VideoCommentsSerializerV2.constructFromObject(options),
    (err, data, _resp) => {
      if (err) callbackFail(formatError(err));
      else callbackSuccess(data);
    },
  );
};

// API call to submit a comment
export const SUBMIT_EDITED_COMMENT = (
  commentId,
  comment,
  callbackSuccess,
  callbackFail,
) => {
  const api = new TournesolAPI.VideoCommentsApi();
  api.videoCommentsPartialUpdate(
    commentId,
    { patchedVideoCommentsSerializerV2: { comment } },
    (err, data, _resp) => {
      if (err) callbackFail(formatError(err));
      else callbackSuccess(data);
    },
  );
};

// API call to double down on a rating
export const DOUBLE_DOWN = (
  username,
  video1,
  video2,
  feature,
  callbackFail,
  callbackSuccess,
) => {
  const api = new TournesolAPI.ExpertRatingsApi();
  api.apiV2ExpertRatingsDoubleDown(
    feature,
    video1,
    video2,
    (err, data, _resp) => {
      if (err) callbackFail(formatError(err));
      else callbackSuccess(data);
    },
  );
};

// API call to flag a comment (thumbs up/down; red flag)
export const FLAG_COMMENT = (commentId, field, callback) => {
  const api = new TournesolAPI.VideoCommentsApi();
  api.apiV2VideoCommentsSetMark(
    'toggle',
    commentId,
    field,
    (_err, data, _resp) => callback(data),
  );
};

export const SUBMIT_COMMENT_FEATURES = (commentId, features) => {
  const api = new TournesolAPI.VideoCommentsApi();
  api.videoCommentsPartialUpdate(commentId, {
    patchedVideoCommentsSerializerV2: features,
  });
};
