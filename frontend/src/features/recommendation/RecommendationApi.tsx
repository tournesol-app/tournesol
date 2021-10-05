import type { PaginatedVideoList } from 'src/services/openapi/models/PaginatedVideoList';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const getRecommendedVideos = (
  searchString: string,
  callback: (m: PaginatedVideoList) => void
) => {
  const dayInMillisecondes = 1000 * 60 * 60 * 24;
  const conversionTime = new Map();
  const params = new URLSearchParams(searchString);
  conversionTime.set('Any', 1);
  conversionTime.set('Today', dayInMillisecondes);
  conversionTime.set('Week', dayInMillisecondes * 7);
  conversionTime.set('Month', dayInMillisecondes * 31);
  conversionTime.set('Year', dayInMillisecondes * 365);
  const dateNow = Date.now();

  if (params.get('date')) {
    const date = params.get('date');
    params.delete('date');
    if (date != 'Any') {
      // TODO figure out why the 1 month adding is needed here
      const limitPublicationDateMilliseconds =
        dateNow - conversionTime.get(date) + dayInMillisecondes * 31;
      const param_date = new Date(limitPublicationDateMilliseconds);
      const [d, m, y, H, M, S] = [
        param_date.getDate().toString(),
        param_date.getMonth().toString(),
        param_date.getFullYear().toString(),
        param_date.getHours().toString(),
        param_date.getMinutes().toString(),
        param_date.getSeconds().toString(),
      ].map((t) => format(t));
      params.append('date_gte', `${d}-${m}-${y}-${H}-${M}-${S}`);
    }
  }

  function format(str: string) {
    if (str.length == 1) {
      return '0'.concat(str);
    } else if (str.length == 4) {
      return str.slice(2);
    } else {
      return str;
    }
  }

  params.append('limit', '20');
  searchString = params.toString();

  // TODO once backend is fixed, use automatically generated code
  fetch(`${api_url}/video/?`.concat(searchString), {
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
