import React, { useContext } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Tooltip, Typography, Box, Switch, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { UsersService, ContributorRating } from 'src/services/openapi';
import { idFromUid } from 'src/utils/video';
import { UID_YT_NAMESPACE, YOUTUBE_POLL_NAME } from 'src/utils/constants';

const setPublicStatus = async (videoId: string, isPublic: boolean) => {
  return await UsersService.usersMeContributorRatingsPartialUpdate({
    pollName: YOUTUBE_POLL_NAME,
    uid: UID_YT_NAMESPACE + videoId,
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
  const { t } = useTranslation();
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
      <Typography variant="caption" sx={{ fontSize: '11px' }}>
        {nComparisons > 0 ? (
          <Link
            color="inherit"
            component={RouterLink}
            to={`/comparisons/?video=${videoId}`}
          >
            <Trans t={t} i18nKey="video.nComparisonsByYou" count={nComparisons}>
              {{ count: nComparisons }} comparison by you
            </Trans>
          </Link>
        ) : (
          t('video.notYetComparedByYou')
        )}
      </Typography>
      <Box flexGrow={1} minWidth="12px" />
      <Tooltip
        title={
          <Typography variant="caption">
            {isPublic
              ? t('video.contributionsArePublicMessage')
              : t('video.contributionsArePrivateMessage')}
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
            sx={{
              color: isPublic ? '#222' : '#bbb',
              textTransform: 'capitalize',
            }}
          >
            {t('public')}
          </Typography>
        </Box>
      </Tooltip>
    </Box>
  );
};

interface RatingsContextValue {
  getContributorRating?: (videoId: string) => ContributorRating;
  onChange?: (rating?: ContributorRating) => void;
}

export const RatingsContext = React.createContext<RatingsContextValue>({});

export const PublicStatusAction = ({ uid }: { uid: string }) => {
  const videoId = idFromUid(uid);
  const { getContributorRating, onChange } = useContext(RatingsContext);
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
