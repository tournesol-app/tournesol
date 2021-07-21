import Cookies from 'js-cookie';
import { v4 as uuid } from 'uuid';

const api_url = process.env.REACT_APP_API_URL;
const client_id = process.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = process.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const fetchLogin = async (username: string, password: string) => {
  let csrfToken = Cookies.get("csrftoken");
  if (csrfToken === undefined) {
    csrfToken = await fetch(api_url + '/admin/login/', { credentials: 'include', }).then(() => Cookies.get("csrftoken"));
  }
  if (csrfToken === undefined) {
    csrfToken = "";
  }
  let params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  params.append('next', '/admin/');
  params.append('csrfmiddlewaretoken', csrfToken);
  const response = await fetch(api_url + '/admin/login/',
    {
      method: 'POST',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    }
  );
  // console.log(response);
  if (response.url !== api_url + '/admin/') { console.error('login failed'); return { data: false }; }
  return { data: true };
}

export const fetchAuthorization = async () => {
  const state = uuid();
  let params = new URLSearchParams();
  params.append('response_type', 'code');
  params.append('client_id', client_id);
  params.append('state', state);
  params.append('redirect_uri', api_url + '/admin/');
  const response = await fetch(api_url + '/o/authorize/?' + params.toString(),
    {
      credentials: 'include',
    }
  );
  // console.log(response);
  const url = new URL(response.url);
  const resp_params = new URLSearchParams(url.search);
  // console.log(resp_params.get('code'));
  let code = resp_params.get('code');
  if (code == null) { code = ''; }
  const resp_state = resp_params.get('state');
  if (state !== resp_state) { console.error('states do not match'); return { data: '' }; }
  return { data: code };
}

export const fetchToken = async (code: string) => {
  let params = new URLSearchParams();
  params.append('code', code);
  params.append('redirect_uri', api_url + '/admin/');
  params.append('grant_type', 'authorization_code');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'read write groups');
  const response = await fetch(api_url + '/o/token/',
    {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    }
  );
  // console.log(response);
  return { data: response.json() };
}

export const fetchTokenFromRefresh = async (refresh_token: string) => {
  let params = new URLSearchParams();
  params.append('refresh_token', refresh_token);
  params.append('redirect_uri', api_url + '/admin/');
  params.append('grant_type', 'refresh_token');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'read write groups');
  const response = await fetch(api_url + '/o/token/',
    {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    }
  );
  // console.log(response);
  return { data: response.json() };
}
