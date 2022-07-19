import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Button, IconButton } from '@mui/material';
import { Check, ContentCopy } from '@mui/icons-material';

// in milliseconds
const DISPLAY_DELAY = 1200;

/**
 * A button that copies the current URI to the browser clipboard when clicked.
 */
export const CopyToClipboardButton = () => {
  const { t } = useTranslation();

  const [text, setText] = useState(t('copyToClipboard.copy'));
  const [feedback, setFeedback] = useState(false);

  const copyUriToClipboard = () => {
    navigator.clipboard.writeText(window.location.toString());

    // Do not trigger any additionnal rendering when the user clicks
    // repeatedly on the button.
    if (feedback) {
      return;
    }

    setFeedback(true);
    setText(t('copyToClipboard.copied'));

    setTimeout(() => {
      setFeedback(false);
      setText(t('copyToClipboard.copy'));
    }, DISPLAY_DELAY);
  };

  return (
    <Button
      color="secondary"
      variant="outlined"
      endIcon={feedback ? <Check /> : <ContentCopy />}
      onClick={copyUriToClipboard}
    >
      {text}
    </Button>
  );
};

/**
 * An icon button that copies the current URI to the browser clipboard when
 * clicked.
 */
export const CopyToClipboardIconButton = () => {
  const [feedback, setFeedback] = useState(false);

  const copyUriToClipboard = () => {
    navigator.clipboard.writeText(window.location.toString());

    // Do not trigger any additionnal rendering when the user clicks
    // repeatedly on the button.
    if (feedback) {
      return;
    }

    setFeedback(true);

    setTimeout(() => {
      setFeedback(false);
    }, DISPLAY_DELAY);
  };

  return (
    <IconButton onClick={copyUriToClipboard}>
      {feedback ? <Check /> : <ContentCopy />}
    </IconButton>
  );
};

export default CopyToClipboardButton;
