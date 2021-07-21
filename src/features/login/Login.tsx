import React, { useState } from 'react';

import { TextField, Grid, Container, makeStyles, Button } from '@material-ui/core';
import { Check, Clear } from '@material-ui/icons';
import { useAppSelector, useAppDispatch } from '../../app/hooks';
import {
  getAuthorizationAsync,
  getTokenAsync,
  getTokenFromRefreshAsync,
  getLoginAsync,
  selectLogin,
} from './loginSlice';

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

  return (
    <div className="Login">
      <Container className={classes.content} maxWidth="xs">
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
                  defaultValue='jst'
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
                  defaultValue='yop'
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={10} onClick={() => dispatch(getLoginAsync({ username: username, password: password }))}>
            <Button color="secondary" fullWidth variant="contained">
              Login
            </Button>
          </Grid>
          <Grid item xs={2}>
            {login.logged ? <Check /> : <Clear />}
          </Grid>
          <Grid item xs={10} onClick={() => dispatch(getAuthorizationAsync())}>
            <Button color="secondary" fullWidth variant="contained">
              Auth
            </Button>
          </Grid>
          <Grid item xs={2}>
            {(login.code !== '') ? <Check /> : <Clear />}
          </Grid>
          <Grid item xs={10} onClick={() => dispatch(getTokenAsync(login.code))}>
            <Button color="secondary" fullWidth variant="contained">
              Token
            </Button>
          </Grid>
          <Grid item xs={2}>
            {(login.access_token !== '') ? <Check /> : <Clear />}
          </Grid>
          <Grid item xs={12} onClick={() => dispatch(getTokenFromRefreshAsync(login.refresh_token))}>
            <Button color="secondary" fullWidth variant="contained">
              Refresh
            </Button>
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth label="Authorization Code" name="code" size="small" InputProps={{ readOnly: true, }} value={login.code} />
            <TextField fullWidth label="Access Token" name="access_token" size="small" InputProps={{ readOnly: true, }} value={login.access_token} />
            <TextField fullWidth label="Refresh Token" name="refresh_token" size="small" InputProps={{ readOnly: true, }} value={login.refresh_token} />
            <TextField fullWidth label="ID Token" name="id_token" size="small" InputProps={{ readOnly: true, }} value={login.id_token} />
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default Login;
