import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  ListItemIcon,
  ListItemText,
  Menu,
  MenuList,
  MenuItem,
} from '@mui/material';
import { ContentCopy, Link, Twitter } from '@mui/icons-material';
import { openTwitterPopup } from 'src/utils/ui';

interface ContextualMenuProps {
  menuAnchor: null | HTMLElement;
  open: boolean;
  twitterMessage?: string;
  shareMessage?: string;
  onClose: (event: React.MouseEvent<HTMLElement>) => void;
}

/**
 * A `Menu` displaying several sharing options.
 */
const ShareMenu = ({
  menuAnchor,
  open,
  twitterMessage,
  shareMessage,
  onClose,
}: ContextualMenuProps) => {
  const { t } = useTranslation();

  const copyUriToClipboard = (event: React.MouseEvent<HTMLElement>) => {
    navigator.clipboard.writeText(window.location.toString());
    onClose(event);
  };

  const copyShareMessage = (event: React.MouseEvent<HTMLElement>) => {
    if (shareMessage) navigator.clipboard.writeText(shareMessage);
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
            <Link fontSize="small" />
          </ListItemIcon>
          <ListItemText>{t('shareMenu.copyAddress')}</ListItemText>
        </MenuItem>
        {shareMessage && (
          <MenuItem onClick={copyShareMessage}>
            <ListItemIcon>
              <ContentCopy fontSize="small" />
            </ListItemIcon>
            <ListItemText>{t('shareMenu.copyShareMessage')}</ListItemText>
          </MenuItem>
        )}

        {twitterMessage && (
          <MenuItem onClick={() => openTwitterPopup(twitterMessage)}>
            <ListItemIcon>
              <Twitter fontSize="small" />
            </ListItemIcon>
            <ListItemText>{t('shareMenu.shareOnTwitter')}</ListItemText>
          </MenuItem>
        )}
      </MenuList>
    </Menu>
  );
};

export default ShareMenu;
