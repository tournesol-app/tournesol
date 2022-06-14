import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tooltip, Button } from '@mui/material';
import { Autorenew } from '@mui/icons-material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { YOUTUBE_POLL_NAME, UID_YT_NAMESPACE } from 'src/utils/constants';
import { getVideoForComparison, idFromUid } from 'src/utils/video';

interface Props {
  currentUid: string;
  otherUid: string | null;
  onResponse: (newUid: string | null) => void;
  onClick: () => void;
  disabled?: boolean;
}

const AutoEntityButton = ({
  currentUid,
  otherUid,
  onResponse,
  onClick,
  disabled = false,
}: Props) => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  const askNewVideo = async () => {
    onClick();
    const newVideoId: string | null = await getVideoForComparison(
      otherUid ? idFromUid(otherUid) : null,
      idFromUid(currentUid)
    );
    if (newVideoId) {
      onResponse(`${UID_YT_NAMESPACE}${newVideoId}`);
    } else {
      onResponse(null);
    }
  };

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
