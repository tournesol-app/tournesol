import React from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router';
import { Link } from 'react-router-dom';

import {
  ListItemIcon,
  ListItemText,
  MenuList,
  MenuItem,
  Paper,
} from '@mui/material';

import { settingsMenu, TournesolMenuItemType } from 'src/utils/menus';

export default function SettingsMenu() {
  const { t } = useTranslation();
  const location = useLocation();
  return (
    <Paper>
      <MenuList>
        {settingsMenu(t).map((item: TournesolMenuItemType) => (
          <MenuItem
            key={item.id}
            component={Link}
            to={item.to}
            selected={item.to === location.pathname}
          >
            <ListItemIcon>
              <item.icon />
            </ListItemIcon>
            <ListItemText>{item.text}</ListItemText>
          </MenuItem>
        ))}
      </MenuList>
    </Paper>
  );
}
