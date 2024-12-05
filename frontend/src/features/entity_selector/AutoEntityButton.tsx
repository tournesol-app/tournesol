import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';

import { Tooltip, Button, useMediaQuery } from '@mui/material';
import { Autorenew, SwipeUp } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { theme } from 'src/theme';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { ComparisonsContext } from 'src/pages/comparisons/Comparison';
import { MobileButton } from 'src/components/buttons';

interface Props {
  onClick: () => Promise<void>;
  disabled?: boolean;
  variant?: 'compact' | 'full';
  compactLabel?: string;
  compactLabelLoc?: 'left' | 'right';
}

const AutoEntityButton = ({
  onClick,
  disabled = false,
  variant = 'compact',
  compactLabel,
  compactLabelLoc,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const smallScreen = useMediaQuery(theme.breakpoints.down('sm'));
  const context = useContext(ComparisonsContext);

  if (pollName !== YOUTUBE_POLL_NAME) {
    return null;
  }

  return (
    <>
      {smallScreen && variant === 'compact' ? (
        <MobileButton
          className={context.hasLoopedThroughCriteria ? 'glowing' : undefined}
          disabled={disabled}
          color="secondary"
          size="small"
          onClick={onClick}
          sx={{
            fontSize: { xs: '0.7rem', sm: '0.8rem' },
          }}
          data-testid={`auto-entity-button-${variant}`}
          startIcon={compactLabelLoc === 'left' ? compactLabel : undefined}
          endIcon={compactLabelLoc === 'right' ? compactLabel : undefined}
        >
          <SwipeUp />
        </MobileButton>
      ) : (
        <Tooltip
          title={`${t('entitySelector.newVideo')}`}
          aria-label="new_video"
        >
          {/* A non-disabled element, such as <span>, is required by the Tooltip
            component to properly listen to fired events. */}
          <span>
            <Button
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
