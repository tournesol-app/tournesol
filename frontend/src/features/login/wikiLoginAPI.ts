import { JSONObject } from 'src/utils/types';
// import Cookies from 'js-cookie';
import { v4 as uuid } from 'uuid';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_WIKI_OAUTH_CLIENT_ID || '';

export class WikiLoginError extends Error {
  public readonly data: JSONObject;

  constructor(data: JSONObject) {
    const message = data?.error_description || 'Login failed.';
    super(String(message));
    this.data = data;
  }
}

export const fetchLogin = async (username: string, password: string) => {
  const csrfToken = await fetch(api_url + '/admin/login/', {
    credentials: 'include',
  })
    .then((res) => res.text())
    .then((txt) => {
      const match = /name="csrfmiddlewaretoken" value="([^"]*)"/.exec(txt);
      return match ? match[1] : undefined;
    });
  if (csrfToken === undefined) {
    console.error('no CSRF token found');
    return Promise.reject('login failed');
  }
  console.log(csrfToken);
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  params.append('next', '/admin/');
  params.append('csrfmiddlewaretoken', csrfToken);
  const response = await fetch(api_url + '/admin/login/', {
    method: 'POST',
    mode: 'cors',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'x-csrftoken': csrfToken,
    },
    body: params.toString(),
  });
  console.log(response);
  // if (response.url !== api_url + '/admin/') {
  //   console.error('login failed');
  //   return Promise.reject('login failed');
  // }
  return;
};

export const fetchAuthorization = async () => {
  const state = uuid();
  const params = new URLSearchParams();
  params.append('response_type', 'code');
  params.append('client_id', client_id);
  params.append('state', state);
  params.append(
    'redirect_uri',
    'http://tournesol-wiki/wiki/Special:PluggableAuthLogin'
  );
  const response = await fetch(api_url + '/o/authorize/?' + params.toString(), {
    mode: 'cors',
    credentials: 'include',
  });
  console.log(response);
  window.location.replace(response.url);
  const url = new URL(response.url);
  const resp_params = new URLSearchParams(url.search);
  const code = resp_params.get('code');
  if (code == null) {
    console.error('code not present');
    return Promise.reject('code not present');
  }
  const resp_state = resp_params.get('state');
  if (state !== resp_state) {
    console.error('states do not match');
    return Promise.reject('states do not match');
  }
  return { data: code };
};
