import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Button, Grid } from '@mui/material';
import { AccountCircle, ArrowDropDown, ArrowDropUp } from '@mui/icons-material';

import { useLoginState, useNotifications } from 'src/hooks';
import { revokeAccessToken } from 'src/features/login/loginAPI';
import { LoggedOutActions } from './LogoutActions';
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
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleProfileClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    if (menuAnchor === null) {
      setMenuAnchor(event.currentTarget);
    }

    setIsMenuOpen(true);
  };

  const handleMenuClose = () => {
    setIsMenuOpen(false);
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
        id="personal-menu-button"
        variant="outlined"
        color="inherit"
        onClick={handleProfileClick}
        sx={accountLoginButtonSx}
        startIcon={<AccountCircle sx={{ fontSize: '36px' }} color="action" />}
        endIcon={
          isMenuOpen ? (
            <ArrowDropUp sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
          ) : (
            <ArrowDropDown sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
          )
        }
      >
        {loginState.username}
      </Button>
      <PersonalMenu
        open={isMenuOpen}
        menuAnchor={menuAnchor}
        onClose={handleMenuClose}
        onItemClick={handleMenuClose}
        onLogoutClick={logoutProcess}
      />
    </>
  );
};

const AccountInfo = () => {
  const { isLoggedIn } = useLoginState();

  return (
    <Grid
      item
      md={4}
      xs="auto"
      padding={1}
      display="flex"
      justifyContent="flex-end"
      gap={1}
    >
      {isLoggedIn ? <LoggedInActions /> : <LoggedOutActions />}
    </Grid>
  );
};

export default AccountInfo;
