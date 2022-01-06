import React from 'react';
import { useTranslation } from 'react-i18next';
import { IconButton, Tooltip } from '@mui/material';
import CompareIcon from '@mui/icons-material/Compare';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

import { Video, UsersService } from 'src/services/openapi';
import { useNotifications } from 'src/hooks';

export const CompareNowAction = ({ videoId }: { videoId: string }) => {
  const { t } = useTranslation();
  return (
    <Tooltip title={`${t('actions.compareNow')}`} placement="left">
      <IconButton
        size="medium"
        href={`/comparison/?videoA=${videoId}`}
        style={{ color: '#CDCABC' }}
      >
        <CompareIcon />
      </IconButton>
    </Tooltip>
  );
};

export const AddToRateLaterList = ({ videoId }: { videoId: string }) => {
  const { t } = useTranslation();
  const { showSuccessAlert, showInfoAlert } = useNotifications();
  const handleCreation = async () => {
    try {
      await UsersService.usersMeVideoRateLaterCreate({
        requestBody: {
          video: { video_id: videoId } as Video,
        },
      });
      showSuccessAlert(t('actions.videoAddedToRateLaterList'));
    } catch (error) {
      showInfoAlert(t('actions.videoAlreadyInRateLaterList'));
    }
  };
  return (
    <Tooltip title={`${t('actions.rateLater')}`} placement="left">
      <IconButton
        size="medium"
        color="secondary"
        onClick={handleCreation}
        style={{ color: '#CDCABC' }}
      >
        <AddIcon />
      </IconButton>
    </Tooltip>
  );
};

export const RemoveFromRateLater = (asyncCallback?: () => void) => {
  const RemoveFromRateLaterComponnent = ({ videoId }: { videoId: string }) => {
    const { t } = useTranslation();
    const { showSuccessAlert } = useNotifications();
    return (
      <Tooltip title={`${t('actions.remove')}`} placement="left">
        <IconButton
          size="medium"
          onClick={async () => {
            await UsersService.usersMeVideoRateLaterDestroy({ videoId });
            if (asyncCallback) await asyncCallback();
            showSuccessAlert(t('actions.videoDeletedFromRateLaterList'));
          }}
          style={{ color: '#CDCABC' }}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };
  return RemoveFromRateLaterComponnent;
};
