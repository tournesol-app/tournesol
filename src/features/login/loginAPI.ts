import Cookies from 'js-cookie';

export const fetchToken = (code: string, client_id: string, client_secret: string) => {
  let params = new URLSearchParams();
  params.append('code', code);
  params.append('redirect_uri', 'http://localhost:8000/admin/');
  params.append('grant_type', 'authorization_code');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'read write groups');
  return fetch('http://localhost:8000/o/token/',
    {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    },
  )
    .then(response => {
      console.log(response);
      return { data: response.json() }
    })
}

export const fetchTokenFromRefresh = (refresh_token: string, client_id: string, client_secret: string) => {
  let params = new URLSearchParams();
  params.append('refresh_token', refresh_token);
  params.append('redirect_uri', 'http://localhost:8000/admin/');
  params.append('grant_type', 'refresh_token');
  params.append('client_id', client_id);
  params.append('client_secret', client_secret);
  params.append('scope', 'read write groups');
  return fetch('http://localhost:8000/o/token/',
    {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    },
  )
    .then(response => {
      console.log(response);
      return { data: response.json()}
    })
}

export const fetchAuthorization = (client_id: string, state: string) => {
  let params = new URLSearchParams();
  params.append('response_type', 'code');
  params.append('client_id', client_id);
  params.append('state', state);
  params.append('redirect_uri', 'http://localhost:8000/admin/');
  return fetch('http://localhost:8000/o/authorize/?' + params.toString(),
    {
      credentials: 'include',
    },
  )
    .then(response => {
      console.log(response);
      const url = new URL(response.url);
      const params = new URLSearchParams(url.search);
      console.log(params.get('code'));
      let code = params.get('code');
      if (code == null) {code = ''}
      return { data: code }
    })
}

export const fetchLogin = (username: string, password: string) => {
  let csrfToken = Cookies.get("csrftoken")
  if (csrfToken === undefined) {
    csrfToken = "";
  }
  let params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  params.append('next', '/admin/');
  params.append('csrfmiddlewaretoken', csrfToken);
  return fetch('http://localhost:8000/admin/login/',
    {
      method: 'POST',
      mode: 'cors',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    },
  )
    .then(response => {
      console.log(response);
      return { data: 'true' }
    })
}
