/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React, { useState } from 'react';

import CircularProgress from '@material-ui/core/CircularProgress';
import { makeStyles } from '@material-ui/core/styles';
import { TournesolAPI } from '../api';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
  },
}));

export default () => {
  const classes = useStyles();

  const [requested, setRequested] = useState(false);

  const logout = () => {
    const api = new TournesolAPI.LoginSignupApi();
    api.loginSignupLogoutPartialUpdate(() => {
      window.history.pushState({}, '', '/');
      window.location.reload();
    });
  };

  if (!requested) {
    setRequested(true);
    logout();
  }

  return (
    <div className={classes.root}>
      <p>
        Logging out...<br />
        <CircularProgress color="secondary" />
      </p>
    </div>
  );
};
