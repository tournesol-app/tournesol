import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Button, ListItemText, Menu, MenuList, MenuItem } from '@mui/material';
import { ArrowDropDown, ArrowDropUp } from '@mui/icons-material';

const LargeLogoutMenu = () => {
  const { t } = useTranslation();
  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        sx={{
          borderColor: 'rgba(0, 0, 0, 0.23)',
          textTransform: 'initial',
          fontWeight: 'bold',
          borderWidth: '2px',
          color: 'text.primary',
        }}
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

export const MobileLogoutMenu = ({
  menuAnchor,
  open,
  onOpen,
  onClose,
}: {
  menuAnchor: null | HTMLElement;
  open: boolean;
  onOpen: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onClose: () => void;
}) => {
  const { t } = useTranslation();

  return (
    <>
      <Button
        variant="outlined"
        color="inherit"
        sx={{
          borderColor: 'rgba(0, 0, 0, 0.23)',
          textTransform: 'initial',
          fontWeight: 'bold',
          borderWidth: '2px',
          color: 'text.primary',
        }}
        onClick={onOpen}
        endIcon={
          open ? (
            <ArrowDropUp sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
          ) : (
            <ArrowDropDown sx={{ color: 'rgba(0, 0, 0, 0.42)' }} />
          )
        }
      >
        {t('loginButton')}
      </Button>
      {open && (
        <Menu
          id="logged-out-menu"
          open={open}
          anchorEl={menuAnchor}
          onClose={onClose}
          MenuListProps={{
            'aria-labelledby': 'basic-button',
          }}
        >
          <MenuList dense sx={{ py: 0 }}>
            {/* -- my things section -- */}
            <MenuItem
              key="login"
              component={Link}
              to="/login"
              onClick={onClose}
            >
              <ListItemText>{t('loginButton')}</ListItemText>
            </MenuItem>
            <MenuItem
              key="register"
              component={Link}
              to="/signup"
              onClick={onClose}
            >
              <ListItemText>{t('joinUsButton')}</ListItemText>
            </MenuItem>
          </MenuList>
        </Menu>
      )}
    </>
  );
};

export default LargeLogoutMenu;
