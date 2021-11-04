import { VideoSerializerWithCriteria as Video } from 'src/services/openapi/models/VideoSerializerWithCriteria';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const getVideoInformation = (
  videoId: string,
  callback: (m: Video) => void
) => {
  // TODO: replace this custom method with the automatically generated `VideoService.videoRetrieve``
  // VideoService.videoRetrieve is currently not used because the URL is incorrect
  fetch(`${api_url}/video/${videoId}`, {
    method: 'GET',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
    },
  })
    .then((response) => {
      return response.json();
    })
    .then((data: Video) => callback(data))
    .catch((err) => {
      console.log(err);
      callback({
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
      });
    });
};
