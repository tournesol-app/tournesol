import React from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';
import { useSnackbar } from 'notistack';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import { Button, Grid } from '@mui/material';
import { AccountCircle } from '@mui/icons-material';

import { useLoginState } from 'src/hooks';
import { revokeAccessToken } from '../../../login/loginAPI';
import { contactAdministratorLowSeverity } from '../../../../utils/notifications';

const useStyles = makeStyles((theme) => ({
  AccountInfo: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '8px',
    gap: '8px',
  },
  HeaderButton: {
    textTransform: 'initial',
    fontWeight: 'bold',
    borderWidth: '2px',
    color: theme.palette.text.primary,
  },
  JoinUsButton: {
    background: '#3198C4',
    '&:hover': {
      background: '#269',
    },
    color: '#FFFFFF',
  },
}));

const LoggedInActions = () => {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();

  const classes = useStyles();
  const { logout, loginState } = useLoginState();

  const logoutProcess = async () => {
    if (loginState.refresh_token) {
      await revokeAccessToken(loginState.refresh_token).catch(() => {
        contactAdministratorLowSeverity(
          enqueueSnackbar,
          t('logoutNonImpactingError')
        );
      });
    }
    logout();
  };

  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        sx={{ borderColor: 'rgba(0, 0, 0, 0.23)' }}
        onClick={logoutProcess}
        className={classes.HeaderButton}
      >
        {t('logoutButton')}
      </Button>
      <Button
        variant="text"
        color="secondary"
        component={Link}
        to="/settings/profile"
        className={classes.HeaderButton}
        endIcon={<AccountCircle sx={{ fontSize: '36px' }} color="action" />}
      >
        {loginState.username}
      </Button>
    </>
  );
};

const LoggedOutActions = () => {
  const { t } = useTranslation();
  const classes = useStyles();

  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        sx={{ borderColor: 'rgba(0, 0, 0, 0.23)' }}
        component={Link}
        className={classes.HeaderButton}
        to="/login"
      >
        {t('loginButton')}
      </Button>
      <Button
        component={Link}
        variant="contained"
        disableElevation
        className={clsx(classes.HeaderButton, classes.JoinUsButton)}
        to="/signup"
      >
        {t('joinUsButton')}
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
