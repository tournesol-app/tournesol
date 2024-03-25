import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useLocation, Redirect } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  TextField,
  Grid,
  Button,
  Box,
  Divider,
  Typography,
} from '@mui/material';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { ContentHeader, ContentBox, InternalLink } from 'src/components';
import { getTokenAsync, selectLogin } from './loginSlice';
import { hasValidToken } from './loginUtils';
import { LoginState } from './LoginState.model';
import RedirectState from './RedirectState';
import { useCurrentPoll, useNotifications } from 'src/hooks';

const Login = () => {
  const { t } = useTranslation();
  const { showErrorAlert } = useNotifications();
  const login: LoginState = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();
  const [formHasBeenSubmitted, setFormHasBeenSubmitted] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [validToken, setValidToken] = useState(hasValidToken(login));
  const { baseUrl } = useCurrentPoll();
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
    setFormHasBeenSubmitted(true);
    event.preventDefault();
    const result: unknown = await dispatch(
      getTokenAsync({ username: username, password: password })
    );
    const resultWithError = result as { error: Error | undefined };
    if (resultWithError.error) {
      showErrorAlert(resultWithError.error.message);
    }
  };

  if (validToken) {
    if (fromUrl) {
      return <Redirect to={fromUrl} />;
    } else {
      return <Redirect to={baseUrl ?? '/'} />;
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
                label={t('usernameOrEmail')}
                name="username"
                color="secondary"
                size="small"
                variant="outlined"
                autoFocus={true}
                autoComplete="username"
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
                autoComplete="current-password"
                onChange={(event) => setPassword(event.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                type="submit"
                color="secondary"
                fullWidth
                variant="contained"
                disabled={formHasBeenSubmitted && login.status === 'loading'}
              >
                {t('login.logInAction')}
              </Button>
            </Grid>
          </Grid>
        </form>
        <Box my={2}>
          <InternalLink to="/forgot">
            {t('login.forgotYourPassword')}
          </InternalLink>
        </Box>
        <Divider />
        <Box my={2}>
          <Typography variant="subtitle1" gutterBottom>
            {t('login.noAccountYet')}
          </Typography>
          <Button
            color="secondary"
            fullWidth
            variant="outlined"
            component={RouterLink}
            to="/signup"
          >
            {t('login.signUp')}
          </Button>
        </Box>
      </ContentBox>
    </>
  );
};

export default Login;
