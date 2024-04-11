import React from 'react';
import { useTranslation } from 'react-i18next';

import { Tooltip, Button, useMediaQuery, IconButton } from '@mui/material';
import { Autorenew, SwipeUp } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { theme } from 'src/theme';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

interface Props {
  onClick: () => Promise<void>;
  disabled?: boolean;
  variant?: 'compact' | 'full';
  htmlId?: string;
}

const AutoEntityButton = ({
  onClick,
  disabled = false,
  variant = 'compact',
  htmlId,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const smallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  if (pollName !== YOUTUBE_POLL_NAME) {
    return null;
  }

  return (
    <>
      {smallScreen && variant === 'compact' ? (
        <IconButton
          id={htmlId}
          disabled={disabled}
          color="secondary"
          size="small"
          onClick={onClick}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.8rem' } }}
          data-testid={`auto-entity-button-${variant}`}
        >
          <SwipeUp />
        </IconButton>
      ) : (
        <Tooltip
          title={`${t('entitySelector.newVideo')}`}
          aria-label="new_video"
        >
          {/* A non-disabled element, such as <span>, is required by the Tooltip
            component to properly listen to fired events. */}
          <span>
            <Button
              id={htmlId}
              fullWidth={variant === 'full' ? true : false}
              disabled={disabled}
              color="secondary"
              variant="outlined"
              size="small"
              onClick={onClick}
              startIcon={variant === 'full' ? undefined : <Autorenew />}
              sx={
                variant === 'full'
                  ? { minHeight: '100px', fontSize: '1rem' }
                  : { fontSize: { xs: '0.7rem', sm: '0.8rem' } }
              }
              data-testid={`auto-entity-button-${variant}`}
            >
              {variant === 'full'
                ? t('entitySelector.letTournesolSelectAVideo')
                : t('entitySelector.auto')}
            </Button>
          </span>
        </Tooltip>
      )}
    </>
  );
};

export default AutoEntityButton;
