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
  youtubeLink,
  feedbackDuration = 1200,
}: {
  isIcon?: boolean;
  shareMessage?: string;
  twitterMessage?: string;
  youtubeLink?: string;
  feedbackDuration?: number;
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

  const handleMenuClose = (
    event: React.MouseEvent<HTMLElement>,
    reason?: string
  ) => {
    if (!['backdropClick', 'escapeKeyDown'].includes(reason ?? '')) {
      setFeedback(true);
    }

    setIsMenuOpen(false);

    if (feedbackTimeoutId.current) {
      clearTimeout(feedbackTimeoutId.current);
    }

    if (!['backdropClick', 'escapeKeyDown'].includes(reason ?? '')) {
      feedbackTimeoutId.current = setTimeout(() => {
        setFeedback(false);
      }, feedbackDuration);
    }
  };

  return (
    <>
      {isIcon ? (
        <IconButton
          aria-label="Share button"
          color="inherit"
          onClick={handleShareMenuClick}
        >
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
        youtubeLink={youtubeLink}
        menuAnchor={menuAnchor}
        open={isMenuOpen}
        onClose={handleMenuClose}
      />
    </>
  );
};

export default ShareMenuButton;
