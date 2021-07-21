import React from 'react';

import { TextField, Grid, Container, makeStyles, Button } from '@material-ui/core';
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

  return (
    <div className="Login">
      <Container className={classes.content} maxWidth="xs">
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField fullWidth label="Email" name="email" size="small" variant="outlined" />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  size="small"
                  type="password"
                  variant="outlined"
                />
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12} onClick={() => dispatch(getTokenAsync({code: [login.code], client_id: '83x0YNh0F4oq0aP5QOPEguAG5xOKKaYNL9M8H8xW', client_secret: 'xw39T12ej01eU6JJ5kxuRir1cuWRdMqipgBHSptAdGPf9e8HXSnzkaYIgZw3hnD2hO17Bd7HkPBbVink7Ly4F31jkiIOYfhndI5RX6MKsysaw1wCYHrOYmx2KBGo4OvI'}))}>
            <Button color="secondary" fullWidth variant="contained">
              Token
            </Button>
          </Grid>
          <Grid item xs={12} onClick={() => dispatch(getTokenFromRefreshAsync({refresh_token: [login.refresh_token], client_id: '83x0YNh0F4oq0aP5QOPEguAG5xOKKaYNL9M8H8xW', client_secret: 'xw39T12ej01eU6JJ5kxuRir1cuWRdMqipgBHSptAdGPf9e8HXSnzkaYIgZw3hnD2hO17Bd7HkPBbVink7Ly4F31jkiIOYfhndI5RX6MKsysaw1wCYHrOYmx2KBGo4OvI'}))}>
            <Button color="secondary" fullWidth variant="contained">
              Refresh
            </Button>
          </Grid>
          <Grid item xs={12} onClick={() => dispatch(getAuthorizationAsync({client_id: '83x0YNh0F4oq0aP5QOPEguAG5xOKKaYNL9M8H8xW', state: 'plop'}))}>
            <Button color="secondary" fullWidth variant="contained">
              Auth
            </Button>
          </Grid>
          <Grid item xs={12} onClick={() => dispatch(getLoginAsync({username: 'jst', password: 'yop'}))}>
            <Button color="secondary" fullWidth variant="contained">
              Login
            </Button>
          </Grid>
          <Grid item xs={12}>
            <TextField fullWidth label="Token" name="token" size="small" InputProps={{ readOnly: true, }} value={login.token} />
          </Grid>
        </Grid>
      </Container>
    </div>
  );
}

export default Login;
