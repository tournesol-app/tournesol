import { JSONObject } from 'src/utils/types';

const api_url = import.meta.env.REACT_APP_API_URL;
const client_id = import.meta.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = import.meta.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export class LoginError extends Error {
  public readonly data: JSONObject;

  constructor(data: JSONObject) {
    const message = data?.error_description || 'Login failed.';
    super(String(message));
    this.data = data;
  }
}

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
  let response;
  try {
    response = await fetch(api_url + '/o/token/', {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        Authorization: 'Basic ' + btoa(client_id + ':' + client_secret),
      },
      body: params.toString(),
    });
  } catch {
    return Promise.reject('Connection to server failed.');
  }
  const jresp = response.json().then((data) => {
    if (
      data.access_token === undefined ||
      data.refresh_token === undefined ||
      data.expires_in === undefined
    ) {
      return Promise.reject(new LoginError(data));
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

export const revokeAccessToken = async (token: string) => {
  const params = new URLSearchParams();
  params.append('token', token);
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('token_type_hint', 'refresh_token');
  const response = await fetch(api_url + '/o/revoke_token/', {
    method: 'POST',
    mode: 'cors',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: params.toString(),
  });

  return response;
};
