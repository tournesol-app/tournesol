import React, { useContext } from 'react';
import { Tooltip, Typography, Box, Switch } from '@material-ui/core';

import { UsersService, ContributorRating } from 'src/services/openapi';

const setPublicStatus = async (videoId: string, isPublic: boolean) => {
  return await UsersService.usersMeContributorRatingsPartialUpdate({
    videoId,
    requestBody: {
      is_public: isPublic,
    },
  });
};

export const UserRatingPublicToggle = ({
  videoId,
  nComparisons,
  isPublic,
  onChange,
}: {
  videoId: string;
  nComparisons: number;
  isPublic: boolean;
  onChange?: (rating: ContributorRating) => void;
}) => {
  const handleChange = React.useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const newStatus = e.target.checked;
      const rating = await setPublicStatus(videoId, newStatus);
      if (onChange) {
        onChange(rating);
      }
    },
    [onChange, videoId]
  );

  return (
    <Box display="flex" alignItems="center" flexWrap="wrap" width="100%" px={1}>
      <Typography variant="caption" style={{ fontSize: '11px' }}>
        {nComparisons > 0
          ? `${nComparisons} comparison(s) by you`
          : 'Not yet compared by you'}
      </Typography>
      <Box flexGrow={1} minWidth="12px" />
      <Tooltip
        title={
          <Typography variant="caption">
            {isPublic
              ? 'Your contributions about this video are currently public. \
              Comparisons appear in the public data associated to your profile only if you tag both videos as public.'
              : 'Your contributions about this video are currently private. \
            The details of your personal ratings are not published, but\
            they may still be used to compute public aggregated scores about videos.'}
          </Typography>
        }
        placement="bottom"
      >
        <Box component="label" display="inline-flex" alignItems="center">
          <Switch
            checked={isPublic}
            onChange={handleChange}
            size="small"
            color="primary"
            edge="start"
          />
          <Typography
            variant="caption"
            style={{ color: isPublic ? '#222' : '#bbb' }}
          >
            Public
          </Typography>
        </Box>
      </Tooltip>
    </Box>
  );
};

interface PublicStatusContextValue {
  getContributorRating?: (videoId: string) => ContributorRating;
  onChange?: (rating: ContributorRating) => void;
}

export const PublicStatusContext =
  React.createContext<PublicStatusContextValue>({});

export const PublicStatusAction = ({ videoId }: { videoId: string }) => {
  const { getContributorRating, onChange } = useContext(PublicStatusContext);
  const contributorRating = getContributorRating?.(videoId);
  if (contributorRating == null || contributorRating.is_public == null) {
    return null;
  }
  return (
    <UserRatingPublicToggle
      nComparisons={contributorRating.n_comparisons}
      isPublic={contributorRating.is_public}
      videoId={videoId}
      onChange={onChange}
    />
  );
};
