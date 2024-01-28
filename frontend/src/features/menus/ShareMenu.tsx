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

interface ShareMenuProps {
  menuAnchor: null | HTMLElement;
  open: boolean;
  shareMessage?: string;
  twitterMessage?: string;
  youtubeLink?: string;
  onClose: (event: React.MouseEvent<HTMLElement>, reason?: string) => void;
}

/**
 * A `Menu` displaying several sharing options.
 */
const ShareMenu = ({
  menuAnchor,
  open,
  shareMessage,
  twitterMessage,
  youtubeLink,
  onClose,
}: ShareMenuProps) => {
  const { t } = useTranslation();
  const navigatorCanShare = navigator.share != undefined;

  const shareText = (text: string) => {
    if (navigatorCanShare) {
      navigator.share({ text });
    } else {
      navigator.clipboard.writeText(text);
    }
  };

  const shareUrl = (url: string) => {
    if (navigatorCanShare) {
      navigator.share({ url });
    } else {
      navigator.clipboard.writeText(url);
    }
  };

  const shareCurrentUrl = (event: React.MouseEvent<HTMLElement>) => {
    shareUrl(window.location.toString());
    onClose(event);
  };

  const shareAsMessage = (event: React.MouseEvent<HTMLElement>) => {
    if (shareMessage) {
      shareText(shareMessage);
    }
    onClose(event);
  };

  const shareYoutubeLink = (event: React.MouseEvent<HTMLElement>) => {
    if (youtubeLink) {
      shareUrl(youtubeLink);
    }
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
        <MenuItem onClick={shareCurrentUrl}>
          <ListItemIcon>
            <Link fontSize="small" />
          </ListItemIcon>
          <ListItemText>
            {navigatorCanShare
              ? t('shareMenu.shareAddress')
              : t('shareMenu.copyAddress')}
          </ListItemText>
        </MenuItem>
        {shareMessage && (
          <MenuItem onClick={shareAsMessage}>
            <ListItemIcon>
              <ContentCopy fontSize="small" />
            </ListItemIcon>
            <ListItemText>
              {navigatorCanShare
                ? t('shareMenu.shareAsMessage')
                : t('shareMenu.copyShareMessage')}
            </ListItemText>
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
        {navigatorCanShare && !!youtubeLink && (
          <MenuItem onClick={shareYoutubeLink}>
            <ListItemIcon>
              <Link fontSize="small" />
            </ListItemIcon>
            <ListItemText>{t('shareMenu.shareYoutubeLink')}</ListItemText>
          </MenuItem>
        )}
      </MenuList>
    </Menu>
  );
};

export default ShareMenu;
