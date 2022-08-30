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
import { Logout, VideoLibrary, HowToReg } from '@mui/icons-material';
import { TournesolMenuItemType, settingsMenu } from 'src/utils/menus';
import { useCurrentPoll, useLoginState } from 'src/hooks';

interface PersonalMenuProps {
  menuAnchor: null | HTMLElement;
  open: boolean;
  onClose: (event: React.MouseEvent<HTMLElement>) => void;
  onItemClick: (event: React.MouseEvent<HTMLElement>) => void;
  onLogoutClick: () => void;
}

const PersonalMenu = ({
  menuAnchor,
  open,
  onClose,
  onItemClick,
  onLogoutClick,
}: PersonalMenuProps) => {
  const { t } = useTranslation();
  const location = useLocation();
  const { baseUrl, options } = useCurrentPoll();
  const { loginState } = useLoginState();

  const allowPublicPersonalRecommendations =
    options?.allowPublicPersonalRecommendations ?? false;

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
        {/* -- my things section -- */}
        {allowPublicPersonalRecommendations && [
          <MenuItem
            key="public-personal-recommendations"
            component={RouterLink}
            to={`${baseUrl}/users/${loginState.username}/recommendations?date=`}
            onClick={onItemClick}
          >
            <ListItemIcon>
              <VideoLibrary fontSize="small" />
            </ListItemIcon>
            <ListItemText>{t('personalMenu.yourRecommendations')}</ListItemText>
          </MenuItem>,
        ]}
        <MenuItem
          key="personal-vouchers"
          component={RouterLink}
          to={`${baseUrl}/personal-vouchers`}
          onClick={onItemClick}
        >
          <ListItemIcon>
            <HowToReg fontSize="small" />
          </ListItemIcon>
          <ListItemText>{t('personalMenu.vouchers')}</ListItemText>
        </MenuItem>
        <Divider key="my-things-divider" />
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
