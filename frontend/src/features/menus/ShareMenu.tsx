import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  ListItemIcon,
  ListItemText,
  Menu,
  MenuList,
  MenuItem,
} from '@mui/material';
import { ContentCopy } from '@mui/icons-material';

interface ContextualMenuProps {
  menuAnchor: null | HTMLElement;
  open: boolean;
  onClose: (event: React.MouseEvent<HTMLElement>) => void;
}

/**
 * A `Menu` displaying several sharing options.
 */
const ShareMenu = ({ menuAnchor, open, onClose }: ContextualMenuProps) => {
  const { t } = useTranslation();

  const copyUriToClipboard = (event: React.MouseEvent<HTMLElement>) => {
    navigator.clipboard.writeText(window.location.toString());
    onClose(event);
  };

  return (
    <Menu
      id="contextual-menu"
      open={open}
      anchorEl={menuAnchor}
      onClose={onClose}
      MenuListProps={{
        'aria-labelledby': 'basic-button',
      }}
    >
      <MenuList dense sx={{ py: 0 }}>
        <MenuItem onClick={copyUriToClipboard}>
          <ListItemIcon>
            <ContentCopy fontSize="small" />
          </ListItemIcon>
          <ListItemText>{t('shareMenu.copyAddress')}</ListItemText>
        </MenuItem>
      </MenuList>
    </Menu>
  );
};

export default ShareMenu;
