import React from 'react';

import { IconButton, Tooltip } from '@material-ui/core';
import CompareIcon from '@material-ui/icons/Compare';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import { showSuccessAlert, showInfoAlert } from 'src/utils/notifications';
import { useSnackbar } from 'notistack';

import { Video, UsersService } from 'src/services/openapi';

export const CompareNowAction = ({ videoId }: { videoId: string }) => {
  return (
    <Tooltip title="Compare now" placement="left">
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
  const video_id = videoId;
  const { enqueueSnackbar } = useSnackbar();
  const handleCreation = async () => {
    try {
      await UsersService.usersMeVideoRateLaterCreate({
        requestBody: {
          video: { video_id } as Video,
        },
      });
      showSuccessAlert(
        enqueueSnackbar,
        'The video has been added to your rate later list.'
      );
    } catch (error) {
      showInfoAlert(
        enqueueSnackbar,
        'The video is already in your rate later list.'
      );
    }
  };
  return (
    <Tooltip title="Rate later" placement="left">
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
    const { enqueueSnackbar } = useSnackbar();
    return (
      <Tooltip title="Remove" placement="left">
        <IconButton
          size="medium"
          onClick={async () => {
            await UsersService.usersMeVideoRateLaterDestroy({ videoId });
            if (asyncCallback) await asyncCallback();
            showSuccessAlert(
              enqueueSnackbar,
              'The video has been deleted from your rate later list.'
            );
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
