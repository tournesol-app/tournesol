import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink, useLocation } from 'react-router-dom';

import {
  Divider,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuList,
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
  const location = useLocation();

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
      <MenuList dense sx={{ py: 0 }}>
        <MenuItem
          component={RouterLink}
          to="/settings/profile"
          onClick={onItemClick}
          selected={'/settings/profile' === location.pathname}
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
          selected={'/settings/account' === location.pathname}
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
      </MenuList>
    </Menu>
  );
};

export default PersonalMenu;
