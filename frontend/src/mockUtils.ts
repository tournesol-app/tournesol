const client_id = import.meta.env.REACT_APP_OAUTH_CLIENT_ID || '';
const client_secret = import.meta.env.REACT_APP_OAUTH_CLIENT_SECRET || '';

export const mockAppRequests = () => {
  fetchMock.mockResponse((req) => {
    if (req.url.match('/o/token')) {
      const params = new URLSearchParams(req.body?.toString());
      const hasCorrectAuth =
        req.headers.get('Authorization') ===
        'Basic ' + btoa(client_id + ':' + client_secret);
      const isPassword = params.get('grant_type') === 'password';
      const isRefreshToken = params.get('grant_type') === 'refresh_token';

      // Valid login
      if (
        hasCorrectAuth &&
        isPassword &&
        params.get('username') === 'jst' &&
        params.get('password') === 'yop' &&
        params.get('scope') === 'read write groups'
      ) {
        return {
          init: {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
            },
          },
          body: JSON.stringify({
            access_token: 'dummy_new_access_token',
            refresh_token: 'dummy_new_refresh_token',
            expires_in: 3600,
          }),
        };
      }

      // Refresh token
      if (hasCorrectAuth && isRefreshToken) {
        return {
          init: {
            status: 200,
            headers: {
              'Content-Type': 'application/json',
            },
          },
          body: JSON.stringify({
            access_token: 'dummy_new_access_token',
            refresh_token: 'dummy_new_refresh_token',
            expires_in: 3600,
          }),
        };
      }

      return {
        init: {
          status: 401,
        },
        body: '{}',
      };
    }

    if (req.url.match('/users/me/settings')) {
      return {
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify({}),
      };
    }

    if (req.url.match('/polls/videos/')) {
      return {
        init: {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
          },
        },
        body: JSON.stringify({
          name: 'videos',
          criterias: [
            {
              name: 'largely_recommended',
              label: 'Should be largely recommended',
              optional: false,
            },
          ],
          entity_type: 'video',
          active: true,
        }),
      };
    }

    return {
      init: {
        status: 403,
      },
    };
  });
};
