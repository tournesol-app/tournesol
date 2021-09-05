// import { ComparisonService } from '../../services/openapi';
// import { OpenAPI } from '../../services/openapi/core/OpenAPI';

const api_url = process.env.REACT_APP_API_URL;

// export const fetchComparisons = (access_token: string) => {
//   OpenAPI.TOKEN = access_token;
//   OpenAPI.BASE = api_url ?? '';
//   return ;
// };

export const fetchComparisons = async (access_token: string) => {
  const response = await fetch(api_url + '/comparison/', {
    headers: {
      Authorization: 'Bearer ' + access_token,
    },
  });
  console.log(response);
  return response.json();
};
