import React from 'react';

import { Link } from 'react-router-dom';
import { useLocation } from 'react-router';

import Paper from '@material-ui/core/Paper';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import MenuList from '@material-ui/core/MenuList';
import MenuItem from '@material-ui/core/MenuItem';
import AccountCircle from '@material-ui/icons/AccountCircle';
import Settings from '@material-ui/icons/Settings';

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
