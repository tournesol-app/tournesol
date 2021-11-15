import { VideoSerializerWithCriteria as Video } from 'src/services/openapi/models/VideoSerializerWithCriteria';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

const _inMemoryCache: { [videoId: string]: Video } = {};

export const getVideoInformation = async (videoId: string) => {
  // TODO: replace this custom method with the automatically generated `VideoService.videoRetrieve``
  // VideoService.videoRetrieve is currently not used because the URL is incorrect
  if (_inMemoryCache[videoId] == undefined) {
    try {
      const response = await fetch(`${api_url}/video/${videoId}`, {
        method: 'GET',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
        },
      });
      _inMemoryCache[videoId] = await response.json();
    } catch (err) {
      console.log(err);
      return {
        name: 'Missing Information',
        publication_date: '',
        uploader: '',
        views: 0,
        video_id: videoId,
        description: '',
        language: null,
        rating_n_ratings: 0,
        rating_n_contributors: 0,
        criteria_scores: [],
      };
    }
  }
  return _inMemoryCache[videoId];
};
