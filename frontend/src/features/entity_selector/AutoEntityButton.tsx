import React, { useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';

import { Tooltip, Button, useMediaQuery, IconButton } from '@mui/material';
import { Autorenew } from '@mui/icons-material';

import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { theme } from 'src/theme';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { getUidForComparison } from 'src/utils/video';

interface Props {
  currentUid: string | null;
  otherUid: string | null;
  onResponse: (newUid: string | null) => void;
  onClick: () => void;
  disabled?: boolean;
  autoFill?: boolean;
  variant?: 'compact' | 'full';
}

const AutoEntityButton = ({
  currentUid,
  otherUid,
  onResponse,
  onClick,
  disabled = false,
  autoFill = false,
  variant = 'compact',
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const smallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const mountedRef = useRef(false);

  // askNewVideo needs to compare the received UID with the current `otherUid`
  // but it can't access the updated props so we keep a ref with the latest value.
  const otherUidRef = useRef(otherUid);
  otherUidRef.current = otherUid;

  const askNewVideo = useCallback(
    async ({ fromAutoFill = false } = {}) => {
      onClick();

      const newUid: string | null = await getUidForComparison(
        currentUid || '',
        otherUid ? otherUid : null,
        pollName
      );

      if (!mountedRef.current) return;

      if (newUid) {
        // When both videos are auto filled it's common to receive the same video twice.
        // When it happens we ask for another one.
        if (fromAutoFill && newUid === otherUidRef.current) {
          onResponse(null);
          askNewVideo({ fromAutoFill: true });
          return;
        }

        onResponse(newUid);
      } else {
        onResponse(null);
      }
    },
    [currentUid, otherUid, onClick, onResponse, pollName]
  );

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const previousUidRef = useRef<string | null | undefined>(undefined);
  useEffect(() => {
    // We only want to autofill when the currentUid is cleared, not when the other dependencies
    // change. We must handle the prop change because the component stays mounted when we click on
    // "Compare" and we already are on the comparison page.
    if (currentUid === previousUidRef.current) return;
    previousUidRef.current = currentUid;

    if (autoFill && currentUid === null) askNewVideo({ fromAutoFill: true });
  }, [autoFill, currentUid, askNewVideo]);

  if (pollName !== YOUTUBE_POLL_NAME) {
    return null;
  }

  return (
    <>
      {smallScreen && variant === 'compact' ? (
        <IconButton
          disabled={disabled}
          color="secondary"
          size="small"
          onClick={askNewVideo}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.8rem' } }}
          data-testid={`auto-entity-button-${variant}`}
        >
          <Autorenew />
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
              fullWidth={variant === 'full' ? true : false}
              disabled={disabled}
              color="secondary"
              variant="outlined"
              size="small"
              onClick={askNewVideo}
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
