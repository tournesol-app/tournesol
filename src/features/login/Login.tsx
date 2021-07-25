import React, { useEffect, useState } from 'react';

import {
  TextField,
  Grid,
  Container,
  makeStyles,
  Button,
} from '@material-ui/core';
import { useAppSelector, useAppDispatch } from '../../app/hooks';
import {
  getTokenAsync,
  getLoginAsync,
  getUserInfoAsync,
  selectLogin,
  getTokenFromRefreshAsync,
} from './loginSlice';
import { hasValidToken } from './tokenValidity';
import { useLocation, useHistory } from 'react-router-dom';
import { fetchAuthorization } from './loginAPI';

const useStyles = makeStyles((theme: any) => ({
  content: {
    marginTop: '64px',
    padding: theme.spacing(3),
  },
}));

const Login = () => {
  const classes = useStyles();
  const login = useAppSelector(selectLogin);
  const dispatch = useAppDispatch();
  const [username, setUsername] = useState('jst');
  const [password, setPassword] = useState('yop');
  const [code, setCode] = useState('');
  const [validToken, setValidToken] = useState(false);
  const history = useHistory();
  const location = useLocation();
  const { from }: any = location?.state ?? '';

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
  }, [login]);

  useEffect(() => {
    if (!validToken && login.logged && !code) {
      console.log('logged in, fetching code');
      fetchAuthorization().then((res) => setCode(res.data));
    }
  }, [validToken, login.logged, code]);

  useEffect(() => {
    if (code) {
      console.log('code received, exchanging it for tokens');
      dispatch(getTokenAsync(code))
        .then(() => {
          console.log('code exchanged for token, erasing code');
          setCode('');
        })
        .catch((error) => {
          console.error(
            'attempt at exchanging code for token failed: ' +
              error +
              ', erasing code'
          );
          setCode('');
        });
    }
  }, [code]);

  useEffect(() => {
    if (login.access_token) {
      console.log('access token received, fetching user info');
      dispatch(getUserInfoAsync(login.access_token));
    }
  }, [login.access_token, dispatch]);

  useEffect(() => {
    if (login.need_refresh && login.refresh_token) {
      console.log('token invalid but refresh token present, trying to refresh');
      dispatch(getTokenFromRefreshAsync(login.refresh_token));
    }
  }, [login.need_refresh, login.access_token, dispatch]);

  useEffect(() => {
    if (login.user_info && from !== '') {
      console.log('user info received');
      history.replace(from);
    }
  }, [login.user_info, history, from]);

  return (
    <div className="Login">
      <Container className={classes.content} maxWidth="xs">
        {login.user_info ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="User"
                name="user"
                size="small"
                variant="outlined"
                InputProps={{ readOnly: true }}
                value={login.user_info.username}
              />
            </Grid>
          </Grid>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Login"
                    name="login"
                    size="small"
                    variant="outlined"
                    onChange={(event) => setUsername(event.target.value)}
                    defaultValue="jst"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Password"
                    name="password"
                    size="small"
                    type="password"
                    variant="outlined"
                    onChange={(event) => setPassword(event.target.value)}
                    defaultValue="yop"
                  />
                </Grid>
              </Grid>
            </Grid>
            <Grid
              item
              xs={10}
              onClick={() =>
                dispatch(
                  getLoginAsync({ username: username, password: password })
                )
              }
              role="login-button"
            >
              <Button color="secondary" fullWidth variant="contained">
                Login
              </Button>
            </Grid>
          </Grid>
        )}
      </Container>
    </div>
  );
};

export default Login;
