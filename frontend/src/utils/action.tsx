import React from 'react';

import { IconButton, Tooltip } from '@material-ui/core';
import CompareIcon from '@material-ui/icons/Compare';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';

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
  return (
    <Tooltip title="Rate later" placement="left">
      <IconButton
        size="medium"
        color="secondary"
        onClick={() =>
          UsersService.usersMeVideoRateLaterCreate({
            video: { video_id } as Video,
          })
        }
        style={{ color: '#CDCABC' }}
      >
        <AddIcon />
      </IconButton>
    </Tooltip>
  );
};

export const RemoveFromRateLater = (asyncCallback?: () => void) => {
  const RemoveFromRateLaterComponnent = ({ videoId }: { videoId: string }) => {
    const video_id = videoId;
    return (
      <Tooltip title="Remove" placement="left">
        <IconButton
          size="medium"
          onClick={async () => {
            await UsersService.usersMeVideoRateLaterDestroy(video_id);
            if (asyncCallback) await asyncCallback();
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
