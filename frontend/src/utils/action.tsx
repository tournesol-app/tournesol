import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { IconButton, Tooltip } from '@mui/material';
import CompareIcon from '@mui/icons-material/Compare';
import AddIcon from '@mui/icons-material/Add';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { ApiError, UsersService } from 'src/services/openapi';
import { useCurrentPoll, useLoginState, useNotifications } from 'src/hooks';
import { addToRateLaterList } from './api/rateLaters';
import { getEntitySeen } from './entity';
import { EntityResult } from './types';
import { YOUTUBE_POLL_NAME } from './constants';

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
        color="secondary"
        size="medium"
        component={Link}
        to={`${baseUrl}/comparison?uidA=${uid}`}
      >
        <CompareIcon />
      </IconButton>
    </Tooltip>
  );
};

export const ToggleEntitySeen = (asyncCallback?: () => Promise<void>) => {
  const ToggleEntitySeenComponent = ({
    uid,
    entity,
  }: {
    uid: string;
    entity?: EntityResult;
  }) => {
    const { isLoggedIn } = useLoginState();
    const { name: pollName, options } = useCurrentPoll();
    const { contactAdministrator } = useNotifications();
    const { t } = useTranslation();

    const [disabled, setDisabled] = useState(false);

    if (!isLoggedIn || !entity || !('individual_rating' in entity)) {
      return null;
    }

    const currentSeenStatus = getEntitySeen(entity);

    let toolTip: string;

    switch (pollName) {
      case YOUTUBE_POLL_NAME:
        if (currentSeenStatus) {
          toolTip = t('actions.markVideoAsUnseen');
        } else {
          toolTip = t('actions.markVideoAsSeen');
        }

        break;
      default:
        if (currentSeenStatus) {
          toolTip = t('actions.markAsUnseen');
        } else {
          toolTip = t('actions.markAsSeen');
        }
    }

    const handleUpdateEntitySeen = async () => {
      setDisabled(true);
      let success = false;

      try {
        await UsersService.usersMeContributorRatingsPartialUpdate({
          pollName,
          uid,
          requestBody: {
            entity_seen: !currentSeenStatus,
          },
        });

        success = true;
      } catch (error) {
        // Create the contributor rating if it doesn't exist.
        if (error instanceof ApiError) {
          if (error.status === 404) {
            try {
              await UsersService.usersMeContributorRatingsCreate({
                pollName,
                requestBody: {
                  uid: uid,
                  entity_seen: !currentSeenStatus,
                  is_public: options?.comparisonsCanBePublic === true,
                },
              });
            } catch (error) {
              contactAdministrator('error');
            }

            success = true;
          }
        } else {
          console.error(error);
          contactAdministrator('error');
        }
      } finally {
        setDisabled(false);
        if (success && asyncCallback) {
          try {
            await asyncCallback();
          } catch (error) {
            console.error(error);
            contactAdministrator(
              'warning',
              t('actions.toggleEntitySeenSuccessCbError')
            );
          }
        }
      }
    };

    return (
      <Tooltip title={toolTip} placement="left">
        <IconButton
          size="medium"
          color="secondary"
          onClick={handleUpdateEntitySeen}
          disabled={disabled}
        >
          {currentSeenStatus ? <VisibilityOffIcon /> : <VisibilityIcon />}
        </IconButton>
      </Tooltip>
    );
  };

  return ToggleEntitySeenComponent;
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
      <IconButton size="medium" color="secondary" onClick={handleCreation}>
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
          color="secondary"
          size="medium"
          onClick={async () => {
            await UsersService.usersMeRateLaterDestroy({ pollName, uid });
            if (asyncCallback) await asyncCallback();
            showSuccessAlert(t('actions.videoDeletedFromRateLaterList'));
          }}
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
        color="secondary"
        size="medium"
        component={Link}
        to={`${baseUrl}/entities/${uid}`}
      >
        <QueryStatsIcon />
      </IconButton>
    </Tooltip>
  );
};
