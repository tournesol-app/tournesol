import React from 'react';

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
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem
          component={Link}
          to="/settings/account"
          selected={'/settings/account' === location.pathname}
        >
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>Account</ListItemText>
        </MenuItem>
      </MenuList>
    </Paper>
  );
}
