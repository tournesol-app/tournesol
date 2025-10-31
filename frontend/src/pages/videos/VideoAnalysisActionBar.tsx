import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { Box, Button, ButtonGroup, Tooltip } from '@mui/material';
import { Compare, Add, Twitter } from '@mui/icons-material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { useCurrentPoll, useLoginState, useNotifications } from 'src/hooks';
import { ContributorRating, Recommendation } from 'src/services/openapi';
import { addToRateLaterList } from 'src/utils/api/rateLaters';
import ShareMenuButton from 'src/features/menus/ShareMenuButton';
import { openTwitterPopup } from 'src/utils/ui';
import { updateContributorRatingEntitySeen } from 'src/utils/api/contributorRatings';

// in milliseconds
const FEEDBACK_DURATION = 1200;

const VideoAnalysisActionBar = ({
  video,
  contributorRating,
  onContributorRatingUpdateSuccessCb,
}: {
  video: Recommendation;
  contributorRating?: ContributorRating | null;
  onContributorRatingUpdateSuccessCb: () => Promise<void>;
}) => {
  const { t } = useTranslation();
  const { isLoggedIn } = useLoginState();
  const { baseUrl, name: pollName, options } = useCurrentPoll();
  const { showSuccessAlert, showInfoAlert } = useNotifications();

  const [rateLaterInProgress, setRateLaterInProgress] = useState(false);
  const [toggleEntitySeenProgress, setToggleEntitySeenProgress] =
    useState(false);

  const onRateLaterClick = async () => {
    // Do not trigger any additionnal rendering when the user clicks
    // repeatedly on the button.
    if (rateLaterInProgress) {
      return;
    }

    setRateLaterInProgress(true);

    try {
      await addToRateLaterList(pollName, video.entity.uid);
      showSuccessAlert(t('actions.videoAddedToRateLaterList'));
    } catch (error) {
      showInfoAlert(t('actions.videoAlreadyInRateLaterList'));
    } finally {
      setTimeout(() => {
        setRateLaterInProgress(false);
      }, FEEDBACK_DURATION);
    }
  };

  const onToggleEntitySeenClick = async () => {
    if (toggleEntitySeenProgress && !isLoggedIn) {
      return;
    }

    setToggleEntitySeenProgress(true);
    const currentSeenStatus = contributorRating?.individual_rating.entity_seen;

    try {
      await updateContributorRatingEntitySeen(
        pollName,
        video.entity.uid,
        currentSeenStatus == undefined ? true : !currentSeenStatus,
        options?.comparisonsCanBePublic === true
      );
      // XXX: missing catch statement
    } finally {
      setTimeout(() => {
        setToggleEntitySeenProgress(false);
      }, FEEDBACK_DURATION);
    }

    onContributorRatingUpdateSuccessCb();
  };

  const getTweet = () => {
    return (
      `${t('entityAnalysisPage.twitter.intro')}\n\n` +
      `${t('entityAnalysisPage.twitter.conclusion')}\n\n` +
      `${window.location.toString()}`
    );
  };

  const shareMessage =
    `${t('entityAnalysisPage.video.shareMessageIntro')}\n\n` +
    `${t('entityAnalysisPage.video.shareMessageConclusion')}\n\n` +
    `${window.location.toString()}`;

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'flex-end',
        gap: 2,
      }}
    >
      <ButtonGroup variant="outlined" color="secondary">
        <Button onClick={() => openTwitterPopup(getTweet())}>
          <Twitter />
        </Button>
        <ShareMenuButton
          shareMessage={shareMessage}
          youtubeLink={
            'https://www.youtube.com/watch?v=' + video.entity.metadata.video_id
          }
        />
      </ButtonGroup>
      {isLoggedIn && (
        <ButtonGroup variant="outlined" color="secondary">
          <Tooltip title={`${t('actions.rateLater')}`} placement="bottom">
            <Button
              color="secondary"
              onClick={onRateLaterClick}
              loading={rateLaterInProgress}
            >
              <Add />
            </Button>
          </Tooltip>
          <Tooltip title={`${t('actions.rateLater')}`} placement="bottom">
            <Button
              color="secondary"
              onClick={onToggleEntitySeenClick}
              loading={toggleEntitySeenProgress}
            >
              {contributorRating?.individual_rating.entity_seen ? (
                <VisibilityOffIcon />
              ) : (
                <VisibilityIcon />
              )}
            </Button>
          </Tooltip>
        </ButtonGroup>
      )}
      <Button
        color="secondary"
        variant="contained"
        startIcon={<Compare />}
        component={RouterLink}
        to={`${baseUrl}/comparison?uidA=${video.entity.uid}`}
      >
        {t('entityAnalysisPage.generic.compare')}
      </Button>
    </Box>
  );
};

export default VideoAnalysisActionBar;
