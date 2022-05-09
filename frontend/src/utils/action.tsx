import React from 'react';
import { useTranslation } from 'react-i18next';
import { IconButton, Tooltip } from '@mui/material';
import CompareIcon from '@mui/icons-material/Compare';
import AddIcon from '@mui/icons-material/Add';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import DeleteIcon from '@mui/icons-material/Delete';

import { Video, UsersService } from 'src/services/openapi';
import { useCurrentPoll, useNotifications } from 'src/hooks';
import { idFromUid } from './video';

export const CompareNowAction = ({ uid }: { uid: string }) => {
  const { t } = useTranslation();
  const { baseUrl, active } = useCurrentPoll();

  if (!active) {
    return null;
  }

  return (
    <Tooltip title={`${t('actions.compareNow')}`} placement="left">
      <IconButton
        size="medium"
        href={`${baseUrl}/comparison/?uidA=${uid}`}
        sx={{ color: '#CDCABC' }}
      >
        <CompareIcon />
      </IconButton>
    </Tooltip>
  );
};

export const AddToRateLaterList = ({ uid }: { uid: string }) => {
  const { t } = useTranslation();
  const { showSuccessAlert, showInfoAlert } = useNotifications();
  const handleCreation = async () => {
    try {
      await UsersService.usersMeVideoRateLaterCreate({
        requestBody: {
          video: { video_id: idFromUid(uid) } as Video,
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
        sx={{ color: '#CDCABC' }}
      >
        <AddIcon />
      </IconButton>
    </Tooltip>
  );
};

export const RemoveFromRateLater = (asyncCallback?: () => void) => {
  const RemoveFromRateLaterComponnent = ({ uid }: { uid: string }) => {
    const { t } = useTranslation();
    const { showSuccessAlert } = useNotifications();
    const videoId = idFromUid(uid);

    return (
      <Tooltip title={`${t('actions.remove')}`} placement="left">
        <IconButton
          size="medium"
          onClick={async () => {
            await UsersService.usersMeVideoRateLaterDestroy({ videoId });
            if (asyncCallback) await asyncCallback();
            showSuccessAlert(t('actions.videoDeletedFromRateLaterList'));
          }}
          sx={{ color: '#CDCABC' }}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };
  return RemoveFromRateLaterComponnent;
};

export const AnalysisPageLink = ({ uid }: { uid: string }) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  return (
    <Tooltip title={`${t('actions.analysis')}`} placement="left">
      <IconButton
        size="medium"
        href={`${baseUrl}/entities/${uid}`}
        sx={{ color: '#CDCABC' }}
      >
        <QueryStatsIcon />
      </IconButton>
    </Tooltip>
  );
};
