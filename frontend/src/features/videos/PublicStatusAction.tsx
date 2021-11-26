import React, { useState } from 'react';
import { Tooltip, Typography, Box, Switch } from '@material-ui/core';
import { AccountBox as AccountBoxIcon } from '@material-ui/icons';

import { UsersService, ContributorRating } from 'src/services/openapi';

const setPublicStatus = async (videoId: string, isPublic: boolean) => {
  await UsersService.usersMeContributorRatingsPartialUpdate(videoId, {
    is_public: isPublic,
  });
};

export const UserRatingPublicToggle = ({
  videoId,
  nComparisons,
  isPublic,
}: {
  videoId: string;
  nComparisons: number;
  isPublic: boolean;
}) => {
  const [checked, setChecked] = useState(isPublic);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const newStatus = e.target.checked;
    await setPublicStatus(videoId, newStatus);
    setChecked(newStatus);
  };

  return (
    <Box display="flex" alignItems="center" gridGap="8px" flexWrap="wrap">
      <AccountBoxIcon color="action" titleAccess="Your contributions" />
      <Typography variant="caption">
        {nComparisons > 0
          ? `${nComparisons} comparison(s)`
          : 'No comparison yet'}
      </Typography>
      |
      <Tooltip
        title={
          <Typography variant="caption">
            {checked
              ? 'Your contributions about this video are currently public. \
             They may appear in public data, associated with your profile.'
              : 'Your contributions about this video are currently private. \
            The details of your personal ratings are not published, but\
            they may still be used to compute public aggregated scores about videos.'}
          </Typography>
        }
        placement="bottom"
      >
        <Box component="label" display="inline-flex" alignItems="center">
          <Typography
            variant="caption"
            style={{ color: checked ? '#bbb' : '#222' }}
          >
            Private
          </Typography>
          <Switch
            checked={checked}
            onChange={handleChange}
            size="small"
            color="primary"
          />
          <Typography
            variant="caption"
            style={{ color: checked ? '#222' : '#bbb' }}
          >
            Public
          </Typography>
        </Box>
      </Tooltip>
    </Box>
  );
};

export const getPublicStatusAction = (
  getContributorRating: (videoId: string) => ContributorRating | null
) => {
  const Action = ({ videoId }: { videoId: string }) => {
    const contributorRating = getContributorRating(videoId);
    if (contributorRating == null || contributorRating.is_public == null) {
      return null;
    }
    return (
      <UserRatingPublicToggle
        nComparisons={contributorRating.n_comparisons}
        isPublic={contributorRating.is_public}
        videoId={videoId}
      />
    );
  };
  return Action;
};
