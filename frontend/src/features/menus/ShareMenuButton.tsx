import React, { useState } from 'react';

import { Share } from '@mui/icons-material';
import { IconButton } from '@mui/material';

import ShareMenu from 'src/features/menus/ShareMenu';

/**
 * An `IconButton` displaying the `ShareMenu` when clicked.
 */
const ShareMenuButton = () => {
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
      <IconButton aria-label="Share button" onClick={handleShareMenuClick}>
        <Share />
      </IconButton>
      <ShareMenu
        menuAnchor={menuAnchor}
        open={isMenuOpen}
        onClose={handleMenuClose}
      />
    </>
  );
};

export default ShareMenuButton;
