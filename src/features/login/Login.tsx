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
  selectLogin,
  getTokenFromRefreshAsync,
} from './loginSlice';
import { hasValidToken } from './tokenValidity';
import { useLocation, useHistory } from 'react-router-dom';

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
  const [validToken, setValidToken] = useState(hasValidToken(login));
  const [shouldTryRefresh, setShouldTryRefresh] = useState(
    login.refresh_token && !hasValidToken(login)
  );
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
  }, [login, validToken]);

  useEffect(() => {
    if (!validToken && shouldTryRefresh && login.refresh_token) {
      console.log('token invalid but refresh token present, trying to refresh');
      setShouldTryRefresh(false);
      dispatch(getTokenFromRefreshAsync(login.refresh_token));
    }
  }, [validToken, shouldTryRefresh, login.refresh_token, dispatch]);

  useEffect(() => {
    if (validToken && from !== '') {
      console.log('logged in, redirecting');
      history.replace(from);
    }
  }, [validToken, history, from]);

  return (
    <div className="Login">
      <Container className={classes.content} maxWidth="xs">
        {validToken ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="User"
                name="user"
                size="small"
                variant="outlined"
                InputProps={{ readOnly: true }}
                value={username}
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
                  getTokenAsync({ username: username, password: password })
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
