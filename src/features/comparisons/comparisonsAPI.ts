const api_url = process.env.REACT_APP_API_URL;

export const fetchComparisons = async (access_token: string) => {
  const response = await fetch(api_url + '/comparison/',
    {
      headers: {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );
  console.log(response);
  return response.json();
}
