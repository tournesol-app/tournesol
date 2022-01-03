import React, { useEffect, useState } from 'react';

import { Link as RouterLink } from 'react-router-dom';
import { TextField, Grid, Button, Link, Box } from '@mui/material';
import { useAppSelector, useAppDispatch } from '../../app/hooks';
import { getTokenAsync, selectLogin } from './loginSlice';
import { LoginState } from './LoginState.model';
import { hasValidToken } from './loginUtils';
import { useLocation, Redirect } from 'react-router-dom';
import RedirectState from './RedirectState';
import { Alert, ContentHeader, ContentBox } from 'src/components';

const Login = () => {
  const login: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validToken, setValidToken] = useState(hasValidToken(login));
  const [loginError, setLoginError] = useState<Error | null>(null);
  const location = useLocation();
  const { from: fromUrl } = (location?.state ?? {}) as RedirectState;

  useEffect(() => {
    if (hasValidToken(login)) {
      if (!validToken) {
        setValidToken(true);
      }
    } else {
      if (validToken) {
        setValidToken(false);
      }
    }
  }, [login, validToken]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoginError(null);
    const result: unknown = await dispatch(
      getTokenAsync({ username: username, password: password })
    );
    const resultWithError = result as { error: Error | undefined };
    if (resultWithError.error) {
      setLoginError(resultWithError.error);
    }
  };

  if (validToken) {
    if (fromUrl) {
      return <Redirect to={fromUrl} />;
    } else {
      return <Redirect to="/" />;
    }
  }

  return (
    <>
      <ContentHeader title="Log in to Tournesol" />
      <ContentBox maxWidth="xs">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} direction="column" alignItems="stretch">
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Username"
                name="username"
                color="secondary"
                size="small"
                variant="outlined"
                autoFocus={true}
                onChange={(event) => setUsername(event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Password"
                name="password"
                color="secondary"
                size="small"
                type="password"
                variant="outlined"
                onChange={(event) => setPassword(event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                color="secondary"
                fullWidth
                variant="contained"
                disabled={login.status == 'loading'}
              >
                Log In
              </Button>
            </Grid>
          </Grid>
          {loginError && <Alert>❌ {loginError.message}</Alert>}
        </form>
        <Box my={2}>
          <Link
            component={RouterLink}
            to="/forgot"
            color="secondary"
            underline="hover"
          >
            Forgot your password?
          </Link>
        </Box>
      </ContentBox>
    </>
  );
};

export default Login;
