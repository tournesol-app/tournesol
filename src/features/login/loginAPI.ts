const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const fetchToken = async ({
  username,
  password,
}: {
  username: string;
  password: string;
}) => {
  const params = new URLSearchParams();
  params.append('grant_type', 'password');
  params.append('username', username);
  params.append('password', password);
  params.append('scope', 'read write groups');
  params.append('response_type', 'code id_token token');
  const response = await fetch(api_url + '/o/token/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
    },
    body: params.toString(),
  });
  // console.log(response);
  const jresp = response.json().then((data) => {
    if (
      data.access_token === undefined ||
      data.refresh_token === undefined ||
      data.expires_in === undefined
    ) {
      console.error('login failed: tokens not present');
      return Promise.reject('login failed: tokens not present');
    }
    return data;
  });
  return { data: jresp };
};

export const fetchTokenFromRefresh = async (refresh_token: string) => {
  const params = new URLSearchParams();
  params.append('refresh_token', refresh_token);
  params.append('grant_type', 'refresh_token');
  params.append('scope', 'read write groups');
  const response = await fetch(api_url + '/o/token/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
    },
    body: params.toString(),
  });
  // console.log(response);
  const jresp = response.json().then((data) => {
    if (
      data.access_token === undefined ||
      data.refresh_token === undefined ||
      data.expires_in === undefined
    ) {
      console.error('refresh failed: tokens not present');
      return Promise.reject('refresh failed: tokens not present');
    }
    return data;
  });
  return { data: jresp };
};
