import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Button, Grid } from '@mui/material';
import { AccountCircle } from '@mui/icons-material';

import { useLoginState, useNotifications } from 'src/hooks';
import { revokeAccessToken } from '../../../login/loginAPI';
import PersonalMenu from './PersonalMenu';

const accountLoginButtonSx = {
  borderColor: 'rgba(0, 0, 0, 0.23)',
  textTransform: 'initial',
  fontWeight: 'bold',
  borderWidth: '2px',
  color: 'text.primary',
};

const LoggedInActions = () => {
  const { t } = useTranslation();
  const { contactAdministratorLowSeverity } = useNotifications();

  const { logout, loginState } = useLoginState();

  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);

  const handleProfileClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const logoutProcess = async () => {
    if (loginState.refresh_token) {
      await revokeAccessToken(loginState.refresh_token).catch(() => {
        contactAdministratorLowSeverity(t('logoutNonImpactingError'));
      });
    }
    logout();
  };

  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        onClick={handleProfileClick}
        sx={accountLoginButtonSx}
        endIcon={<AccountCircle sx={{ fontSize: '36px' }} color="action" />}
      >
        {loginState.username}
      </Button>
      <PersonalMenu
        menuAnchor={menuAnchor}
        onClose={handleMenuClose}
        onItemClick={handleMenuClose}
        onLogoutClick={logoutProcess}
      />
    </>
  );
};

const LoggedOutActions = () => {
  const { t } = useTranslation();

  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        sx={accountLoginButtonSx}
        component={Link}
        to="/login"
      >
        {t('loginButton')}
      </Button>
      <Button
        component={Link}
        variant="contained"
        disableElevation
        sx={{
          textTransform: 'initial',
          fontWeight: 'bold',
          borderWidth: '2px',
          color: '#FFFFFF',
          background: '#3198C4',
          '&:hover': {
            background: '#269',
          },
        }}
        to="/signup"
      >
        {t('joinUsButton')}
      </Button>
    </>
  );
};

const AccountInfo = () => {
  const { isLoggedIn } = useLoginState();

  return (
    <Grid
      item
      md={4}
      xs={9}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: '8px',
        gap: '8px',
      }}
    >
      {isLoggedIn ? <LoggedInActions /> : <LoggedOutActions />}
    </Grid>
  );
};

export default AccountInfo;
