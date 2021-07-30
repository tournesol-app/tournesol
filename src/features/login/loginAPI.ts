import { UserInfo } from './UserInfo.model';

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
  let params = new URLSearchParams();
  params.append('grant_type', 'password');
  params.append('username', username);
  params.append('password', password);
  params.append('redirect_uri', api_url + '/admin/');
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
      data.id_token === undefined ||
      data.expires_in === undefined
    ) {
      console.error('tokens not present');
      return Promise.reject('tokens not present');
    }
    return data;
  });
  return { data: jresp };
};

export const fetchTokenFromRefresh = async (refresh_token: string) => {
  let params = new URLSearchParams();
  params.append('refresh_token', refresh_token);
  params.append('redirect_uri', api_url + '/admin/');
  params.append('grant_type', 'refresh_token');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'read write groups');
  const response = await fetch(api_url + '/o/token/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
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
      console.error('tokens not present');
      return Promise.reject('tokens not present');
    }
    return data;
  });
  return { data: jresp };
};

export const fetchUserInfo = async (
  access_token: string
): Promise<UserInfo> => {
  const response = await fetch(api_url + '/o/userinfo/', {
    headers: {
      Authorization: 'Bearer ' + access_token,
    },
  });
  // console.log(response);
  return response.json();
};
