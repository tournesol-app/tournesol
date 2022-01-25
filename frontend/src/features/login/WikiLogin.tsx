import React, { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { TextField, Grid, Button, Link, Box } from '@mui/material';

import { useAppSelector, useAppDispatch } from 'src/app/hooks';
import { ContentHeader, ContentBox } from 'src/components';
import { getLoginAsync, selectWikiLogin } from './wikiLoginSlice';
import { WikiLoginState } from './WikiLoginState.model';
import { useNotifications } from 'src/hooks';
import { fetchAuthorization } from './wikiLoginAPI';

const Login = () => {
  const { t } = useTranslation();
  const { showErrorAlert } = useNotifications();
  const login: WikiLoginState = useAppSelector(selectWikiLogin);
  const dispatch = useAppDispatch();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');

  useEffect(() => {
    if (login.status == 'idle' && login.logged && !code) {
      console.log('logged in, fetching code');
      fetchAuthorization().then((res) => setCode(res.data));
    }
  }, [login, code]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const result: unknown = await dispatch(
      getLoginAsync({ username: username, password: password })
    );
    const resultWithError = result as { error: Error | undefined };
    if (resultWithError.error) {
      showErrorAlert(resultWithError.error.message);
    }
  };

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
