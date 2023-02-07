import React, { useEffect, useCallback, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Tooltip, Button } from '@mui/material';
import { Autorenew } from '@mui/icons-material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { YOUTUBE_POLL_NAME, UID_YT_NAMESPACE } from 'src/utils/constants';
import { getVideoForComparison, idFromUid } from 'src/utils/video';

interface Props {
  currentUid: string | null;
  otherUid: string | null;
  onResponse: (newUid: string | null) => void;
  onClick: () => void;
  disabled?: boolean;
  autoFill?: boolean;
}

const AutoEntityButton = ({
  currentUid,
  otherUid,
  onResponse,
  onClick,
  disabled = false,
  autoFill = false,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();
  const mountedRef = useRef(false);

  // askNewVideo needs to compare the received UID with the current `otherUid`
  // but it can't access the updated props so we keep a ref with the latest value.
  const otherUidRef = useRef(otherUid);
  otherUidRef.current = otherUid;

  const askNewVideo = useCallback(
    async ({ fromAutoFill = false } = {}) => {
      onClick();
      const newVideoId: string | null = await getVideoForComparison(
        otherUid ? idFromUid(otherUid) : null,
        idFromUid(currentUid || '')
      );

      if (!mountedRef.current) return;

      if (newVideoId) {
        const newVideoUid = `${UID_YT_NAMESPACE}${newVideoId}`;

        // When both videos are auto filled it's common to receive the same video twice.
        // When it happens we ask for another one.
        if (fromAutoFill && newVideoUid === otherUidRef.current) {
          onResponse(null);
          askNewVideo({ fromAutoFill: true });
          return;
        }

        onResponse(newVideoUid);
      } else {
        onResponse(null);
      }
    },
    [currentUid, otherUid, onClick, onResponse]
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
    <Tooltip title={`${t('entitySelector.newVideo')}`} aria-label="new_video">
      {/* A <span> element is required to allow wrapping a disabled button.  */}
      <span>
        <Button
          disabled={disabled}
          color="secondary"
          variant="outlined"
          size="small"
          onClick={askNewVideo}
          startIcon={<Autorenew />}
          sx={{ fontSize: { xs: '0.7rem', sm: '0.8rem' } }}
        >
          {t('entitySelector.autoEntityButton')}
        </Button>
      </span>
    </Tooltip>
  );
};

export default AutoEntityButton;
