import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { Button, ButtonGroup, Grid, Tooltip } from '@mui/material';
import { Compare, ContentCopy, Twitter, Add } from '@mui/icons-material';

import { useCurrentPoll, useLoginState, useNotifications } from 'src/hooks';
import { VideoSerializerWithCriteria } from 'src/services/openapi';
import { addToRateLaterList } from 'src/utils/api/rateLaters';
import { SNACKBAR_DYNAMIC_FEEDBACK_MS } from 'src/utils/notifications';
import { useSnackbar } from 'notistack';

const VideoAnalysisToolbar = ({
  video,
}: {
  video: VideoSerializerWithCriteria;
}) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();
  const { isLoggedIn } = useLoginState();
  const { showSuccessAlert, showInfoAlert } = useNotifications();
  const { enqueueSnackbar } = useSnackbar();
  const { name: pollName } = useCurrentPoll();

  const uid = `yt:${video.video_id}`;

  const copyUriToClipboard = () => {
    navigator.clipboard.writeText(window.location.toString());
    enqueueSnackbar(t('copyUriToClipboard.copied'), {
      variant: 'success',
      autoHideDuration: SNACKBAR_DYNAMIC_FEEDBACK_MS,
    });
  };

  const handleCreation = async () => {
    try {
      await addToRateLaterList(pollName, uid);
      showSuccessAlert(t('actions.videoAddedToRateLaterList'));
    } catch (error) {
      showInfoAlert(t('actions.videoAlreadyInRateLaterList'));
    }
  };

  return (
    <Grid container item display="flex" justifyContent="flex-end" gap={2}>
      <ButtonGroup variant="outlined" color="secondary">
        <Button>
          <Twitter />
        </Button>
        <Button onClick={copyUriToClipboard}>
          <ContentCopy />
        </Button>
      </ButtonGroup>
      {isLoggedIn && (
        <Tooltip title={`${t('actions.rateLater')}`} placement="left">
          <Button
            size="medium"
            color="secondary"
            onClick={handleCreation}
            variant="outlined"
          >
            <Add />
          </Button>
        </Tooltip>
      )}
      <Button
        color="secondary"
        variant="contained"
        endIcon={<Compare />}
        component={RouterLink}
        to={`${baseUrl}/comparison?uidA=${uid}`}
      >
        {t('entityAnalysisPage.generic.compare')}
      </Button>
    </Grid>
  );
};

export default VideoAnalysisToolbar;
