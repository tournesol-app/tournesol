import React from 'react';

import { Link } from 'react-router-dom';

import Divider from '@material-ui/core/Divider';
import Paper from '@material-ui/core/Paper';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import MenuList from '@material-ui/core/MenuList';
import MenuItem from '@material-ui/core/MenuItem';
import AccountCircle from '@material-ui/icons/AccountCircle';
import MoreHoriz from '@material-ui/icons/MoreHoriz';
import Settings from '@material-ui/icons/Settings';

export default function SettingsMenu() {
  const pathname = window.location.pathname;
  return (
    <Paper>
      <MenuList>
        <MenuItem
          component={Link}
          to="/settings/profile"
          selected={'/settings/profile' === pathname}
        >
          <ListItemIcon>
            <AccountCircle />
          </ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem
          component={Link}
          to="/settings/account"
          selected={'/settings/account' === pathname}
        >
          <ListItemIcon>
            <Settings />
          </ListItemIcon>
          <ListItemText>Account</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem>
          <ListItemIcon>
            <MoreHoriz />
          </ListItemIcon>
          <ListItemText>More</ListItemText>
        </MenuItem>
      </MenuList>
    </Paper>
  );
}
