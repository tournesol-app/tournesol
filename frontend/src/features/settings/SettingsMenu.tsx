import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { useLocation } from 'react-router';

import Paper from '@mui/material/Paper';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import MenuList from '@mui/material/MenuList';
import MenuItem from '@mui/material/MenuItem';
import AccountCircle from '@mui/icons-material/AccountCircle';
import Settings from '@mui/icons-material/Settings';

export default function SettingsMenu() {
  const { t } = useTranslation();
  const location = useLocation();
  return (
    <Paper>
      <MenuList>
        <MenuItem
          component={Link}
          to="/settings/profile"
          selected={'/settings/profile' === location.pathname}
        >
          <ListItemIcon>
            <AccountCircle />
          </ListItemIcon>
          <ListItemText>{t('profile')}</ListItemText>
        </MenuItem>
        <MenuItem
          component={Link}
          to="/settings/account"
          selected={'/settings/account' === location.pathname}
        >
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>{t('settings.account')}</ListItemText>
        </MenuItem>
      </MenuList>
    </Paper>
  );
}
