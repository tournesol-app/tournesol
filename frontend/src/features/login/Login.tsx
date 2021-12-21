import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useLocation, Redirect } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { TextField, Grid, Button, Link, Box } from '@mui/material';
import { useSnackbar } from 'notistack';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { ContentHeader, ContentBox } from 'src/components';
import { getTokenAsync, selectLogin } from './loginSlice';
import { hasValidToken } from './loginUtils';
import { LoginState } from './LoginState.model';
import RedirectState from './RedirectState';
import { showErrorAlert } from '../../utils/notifications';

const Login = () => {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();
  const login: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validToken, setValidToken] = useState(hasValidToken(login));
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
    const result: unknown = await dispatch(
      getTokenAsync({ username: username, password: password })
    );
    const resultWithError = result as { error: Error | undefined };
    if (resultWithError.error) {
      showErrorAlert(enqueueSnackbar, resultWithError.error.message);
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
      <ContentHeader title={t('login.loginToTournesol')} />
      <ContentBox maxWidth="xs">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} direction="column" alignItems="stretch">
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label={t('username')}
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
                label={t('password')}
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
                {t('login.logInAction')}
              </Button>
            </Grid>
          </Grid>
        </form>
        <Box my={2}>
          <Link
            component={RouterLink}
            to="/forgot"
            color="secondary"
            underline="hover"
          >
            {t('login.forgotYourPassword')}
          </Link>
        </Box>
      </ContentBox>
    </>
  );
};

export default Login;
