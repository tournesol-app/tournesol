import React from 'react';
import { useTranslation } from 'react-i18next';

import { Link as RouterLink } from 'react-router-dom';

import {
  Divider,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
} from '@mui/material';
import { AccountCircle, Logout, Settings } from '@mui/icons-material';

interface PersonalMenuProps {
  menuAnchor: null | HTMLElement;
  onClose: (event: React.MouseEvent<HTMLElement>) => void;
  onItemClick: (event: React.MouseEvent<HTMLElement>) => void;
  onLogoutClick: () => void;
}

const PersonalMenu = ({
  menuAnchor,
  onClose,
  onItemClick,
  onLogoutClick,
}: PersonalMenuProps) => {
  const { t } = useTranslation();

  const open = Boolean(menuAnchor);

  return (
    <Menu
      id="personal-menu"
      open={open}
      anchorEl={menuAnchor}
      onClose={onClose}
      MenuListProps={{
        'aria-labelledby': 'basic-button',
      }}
    >
      <MenuItem
        component={RouterLink}
        to="/settings/profile"
        onClick={onItemClick}
      >
        <ListItemIcon>
          <AccountCircle fontSize="small" />
        </ListItemIcon>
        <ListItemText>{t('profile')}</ListItemText>
      </MenuItem>
      <MenuItem
        component={RouterLink}
        to="/settings/account"
        onClick={onItemClick}
      >
        <ListItemIcon>
          <Settings fontSize="small" />
        </ListItemIcon>
        <ListItemText>{t('settings.account')}</ListItemText>
      </MenuItem>
      <Divider />
      <MenuItem onClick={onLogoutClick}>
        <ListItemIcon>
          <Logout fontSize="small" />
        </ListItemIcon>
        <ListItemText>{t('logoutButton')}</ListItemText>
      </MenuItem>
    </Menu>
  );
};

export default PersonalMenu;
