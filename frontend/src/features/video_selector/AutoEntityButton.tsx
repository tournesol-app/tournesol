import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tooltip, IconButton } from '@mui/material';
import { AutoFixHigh as MagicWandIcon } from '@mui/icons-material';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { YOUTUBE_POLL_NAME, UID_YT_NAMESPACE } from 'src/utils/constants';
import { getVideoForComparison, idFromUid } from 'src/utils/video';

interface Props {
  currentUid: string;
  otherUid: string | null;
  onResponse: (newUid: string | null) => void;
  onClick: () => void;
}

const AutoEntityButton = ({
  currentUid,
  otherUid,
  onResponse,
  onClick,
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
    <Tooltip title={`${t('videoSelector.newVideo')}`} aria-label="new_video">
      <IconButton aria-label="new_video" onClick={askNewVideo}>
        <MagicWandIcon fontSize="small" />
      </IconButton>
    </Tooltip>
  );
};

export default AutoEntityButton;
