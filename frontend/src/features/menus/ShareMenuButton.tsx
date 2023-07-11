import React, { useEffect, useRef, useState } from 'react';

import { Button, IconButton } from '@mui/material';
import { Done, Share } from '@mui/icons-material';

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

  const [feedback, setFeedback] = useState(false);
  const feedbackTimeoutId = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    return () => clearTimeout(feedbackTimeoutId.current);
  }, []);

  const handleShareMenuClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    // Define the anchor the first time the user click on the button.
    if (menuAnchor === null) {
      setMenuAnchor(event.currentTarget);
    }
    setIsMenuOpen(true);
  };

  const handleMenuClose = () => {
    setFeedback(true);

    setIsMenuOpen(false);

    if (feedbackTimeoutId.current) {
      clearTimeout(feedbackTimeoutId.current);
    }

    feedbackTimeoutId.current = setTimeout(() => {
      setFeedback(false);
    }, 1200);
  };

  return (
    <>
      {isIcon ? (
        <IconButton aria-label="Share button" onClick={handleShareMenuClick}>
          {feedback ? <Done /> : <Share />}
        </IconButton>
      ) : (
        <Button aria-label="Share button" onClick={handleShareMenuClick}>
          {feedback ? <Done /> : <Share />}
        </Button>
      )}
      <ShareMenu
        shareMessage={shareMessage}
        twitterMessage={twitterMessage}
        menuAnchor={menuAnchor}
        open={isMenuOpen}
        onClose={handleMenuClose}
      />
    </>
  );
};

export default ShareMenuButton;
