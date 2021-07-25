const api_url = process.env.REACT_APP_API_URL;

export const fetchComparisons = async (access_token: string) => {
  const response = await fetch(api_url + '/comparison/', {
    headers: {
      Authorization: 'Bearer ' + access_token,
    },
  });
  console.log(response);
  return response.json();
};
