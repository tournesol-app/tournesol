import React from 'react';
import clsx from 'clsx';
import { makeStyles } from '@material-ui/core/styles';
import { Button, Grid } from '@material-ui/core';
import { Link } from 'react-router-dom';
import { AccountCircle } from '@material-ui/icons';

import { useLoginState } from 'src/hooks';

const useStyles = makeStyles({
  AccountInfo: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '8px',
    gap: '8px',
  },
  HeaderButton: {
    fontFamily: 'Poppins',
    textTransform: 'initial',
    fontWeight: 'bold',
    borderWidth: '2px',
  },
  JoinUsButton: {
    background: '#3198C4',
    '&:hover': {
      background: '#269',
    },
    color: '#FFFFFF',
  },
});

const LoggedInActions = () => {
  const classes = useStyles();
  const { logout, loginState } = useLoginState();

  return (
    <>
      <Button
        variant="outlined"
        onClick={logout}
        className={classes.HeaderButton}
      >
        Logout
      </Button>
      <Button
        component={Link}
        to="/settings/profile"
        className={classes.HeaderButton}
        endIcon={<AccountCircle style={{ fontSize: '36px' }} color="action" />}
      >
        {loginState.username}
      </Button>
    </>
  );
};

const LoggedOutActions = () => {
  const classes = useStyles();

  return (
    <>
      <Button
        component={Link}
        variant="outlined"
        className={classes.HeaderButton}
        to="/login"
      >
        Log in
      </Button>
      <Button
        component={Link}
        variant="contained"
        disableElevation
        className={clsx(classes.HeaderButton, classes.JoinUsButton)}
        to="/signup"
      >
        Join us
      </Button>
    </>
  );
};

const AccountInfo = () => {
  const { isLoggedIn } = useLoginState();
  const classes = useStyles();

  return (
    <Grid item md={4} xs={8} className={classes.AccountInfo}>
      {isLoggedIn ? <LoggedInActions /> : <LoggedOutActions />}
    </Grid>
  );
};

export default AccountInfo;
