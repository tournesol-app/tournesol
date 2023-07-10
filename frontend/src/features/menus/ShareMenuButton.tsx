import React, { useState } from 'react';

import { Share } from '@mui/icons-material';
import { Button, IconButton } from '@mui/material';

import ShareMenu from 'src/features/menus/ShareMenu';

/**
 * An `Button` displaying the `ShareMenu` when clicked.
 */
const ShareMenuButton = ({
  isIcon,
  shareMessage,
  twitterMessage,
}: {
  isIcon?: boolean;
  shareMessage?: string;
  twitterMessage?: string;
}) => {
  const [menuAnchor, setMenuAnchor] = React.useState<null | HTMLElement>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleShareMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    // Define the anchor the first time the user click on the button.
    if (menuAnchor === null) {
      setMenuAnchor(event.currentTarget);
    }
    setIsMenuOpen(true);
  };

  const handleMenuClose = () => {
    setIsMenuOpen(false);
  };

  return (
    <>
      {isIcon ? (
        <IconButton aria-label="Share button" onClick={handleShareMenuClick}>
          <Share />
        </IconButton>
      ) : (
        <Button aria-label="Share button" onClick={handleShareMenuClick}>
          <Share />
        </Button>
      )}
      <ShareMenu
        twitterMessage={twitterMessage}
        shareMessage={shareMessage}
        menuAnchor={menuAnchor}
        open={isMenuOpen}
        onClose={handleMenuClose}
      />
    </>
  );
};

export default ShareMenuButton;
