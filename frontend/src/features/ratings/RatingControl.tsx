import React, { useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Tooltip, Typography, Box, Switch } from '@mui/material';

import { InternalLink } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import {
  UsersService,
  ContributorRating,
  IndividualRating,
} from 'src/services/openapi';

const setPublicStatus = async (
  pollName: string,
  uid: string,
  isPublic: boolean
) => {
  return await UsersService.usersMeContributorRatingsPartialUpdate({
    pollName,
    uid,
    requestBody: {
      is_public: isPublic,
    },
  });
};

export const RatingControl = ({
  uid,
  individualRating,
  onChange,
}: {
  uid: string;
  individualRating: IndividualRating | null;
  onChange?: (rating: ContributorRating) => void;
}) => {
  const { t } = useTranslation();
  const { name: pollName, baseUrl, options } = useCurrentPoll();
  const [isPublic, setIsPublic] = useState(individualRating?.is_public ?? true);
  const nComparisons = individualRating?.n_comparisons ?? 0;

  const handleChange = React.useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const newStatus = e.target.checked;
      const result = await setPublicStatus(pollName, uid, newStatus);
      setIsPublic(result.individual_rating.is_public);
      if (onChange) {
        onChange(result);
      }
    },
    [onChange, setIsPublic, pollName, uid]
  );

  return (
    <Box display="flex" alignItems="center" flexWrap="wrap" width="100%" px={1}>
      <Typography variant="caption" sx={{ fontSize: '11px' }}>
        {nComparisons > 0 ? (
          <InternalLink
            color="inherit"
            to={`${baseUrl}/comparisons/?uid=${uid}`}
          >
            <Trans t={t} i18nKey="video.nComparisonsByYou" count={nComparisons}>
              {{ count: nComparisons }} comparison by you
            </Trans>
          </InternalLink>
        ) : (
          t('video.notYetComparedByYou')
        )}
      </Typography>
      <Box flexGrow={1} minWidth="12px" />
      {individualRating && options?.comparisonsCanBePublic === true && (
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
      )}
    </Box>
  );
};
