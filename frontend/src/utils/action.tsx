import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { IconButton, Tooltip } from '@mui/material';
import CompareIcon from '@mui/icons-material/Compare';
import AddIcon from '@mui/icons-material/Add';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import DeleteIcon from '@mui/icons-material/Delete';

import { UsersService } from 'src/services/openapi';
import { useCurrentPoll, useLoginState, useNotifications } from 'src/hooks';
import { addToRateLaterList } from './api/rateLaters';

export const CompareNowAction = ({ uid }: { uid: string }) => {
  const { t } = useTranslation();
  const { baseUrl, active } = useCurrentPoll();

  // Do not display anything if the poll is inactive. The button is still
  // displayed for anonymous users to invite them to contribute.
  if (!active) {
    return null;
  }

  return (
    <Tooltip title={`${t('actions.compareNow')}`} placement="left">
      <IconButton
        sx={{ color: '#CDCABC' }}
        size="medium"
        component={Link}
        to={`${baseUrl}/comparison/?uidA=${uid}`}
      >
        <CompareIcon />
      </IconButton>
    </Tooltip>
  );
};

export const AddToRateLaterList = ({ uid }: { uid: string }) => {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();
  const { showSuccessAlert, showInfoAlert } = useNotifications();
  const { name: pollName } = useCurrentPoll();

  // Do not display anything if the user is not logged.
  if (!isLoggedIn) {
    return null;
  }

  const handleCreation = async () => {
    try {
      await addToRateLaterList(pollName, uid);
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
    const { name: pollName } = useCurrentPoll();

    return (
      <Tooltip title={`${t('actions.remove')}`} placement="left">
        <IconButton
          size="medium"
          onClick={async () => {
            await UsersService.usersMeRateLaterDestroy({ pollName, uid });
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
        sx={{ color: '#CDCABC' }}
        size="medium"
        component={Link}
        to={`${baseUrl}/entities/${uid}`}
      >
        <QueryStatsIcon />
      </IconButton>
    </Tooltip>
  );
};
