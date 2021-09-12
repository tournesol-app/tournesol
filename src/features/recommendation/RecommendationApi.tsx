import type { PaginatedVideoList } from 'src/services/openapi/models/PaginatedVideoList';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const getRecommendedVideos = (
  searchString: string,
  language: string,
  date: string,
  callback: (m: PaginatedVideoList) => void
) => {
  fetch(`${api_url}/video/`.concat(searchString), {
    // /?language=` + language + '&date=' + date if you wan to add parameters
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
    .then((data) => {
      callback(data);
    })
    .catch((err) => {
      console.log(err);
      callback({
        results: [],
        count: 0,
      });
    });
};
