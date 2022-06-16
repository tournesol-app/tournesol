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
import { Logout } from '@mui/icons-material';
import { TournesolMenuItemType, settingsMenu } from 'src/utils/menus';

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
        {/* -- settings section -- */}
        {settingsMenu(t).map((item: TournesolMenuItemType) => (
          <MenuItem
            key={item.id}
            component={RouterLink}
            to={item.to}
            onClick={onItemClick}
            selected={item.to === location.pathname}
          >
            <ListItemIcon>
              <item.icon fontSize="small" />
            </ListItemIcon>
            <ListItemText>{item.text}</ListItemText>
          </MenuItem>
        ))}
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
