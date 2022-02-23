import React, { useContext } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Button, Box } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

import { TitledSection } from 'src/components';
import { UsersService } from 'src/services/openapi';
import { RatingsContext } from 'src/features/videos/PublicStatusAction';
import { useNotifications } from 'src/hooks';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

function MarkAllRatings() {
  const { t } = useTranslation();
  const { onChange: onRatingChange } = useContext(RatingsContext);
  const { showErrorAlert, showInfoAlert } = useNotifications();

  const updateRatings = async (isPublic: boolean) => {
    try {
      await UsersService.usersMeContributorRatingsAllPartialUpdate({
        pollName: YOUTUBE_POLL_NAME,
        requestBody: { is_public: isPublic },
      });
    } catch (err) {
      showErrorAlert(err?.message || 'Server error');
      return;
    }
    if (onRatingChange) {
      onRatingChange();
    }
    showInfoAlert(
      isPublic
        ? t('ratings.allRatingsMarkedPublic')
        : t('ratings.allRatingsMarkedPrivate')
    );
  };

  return (
    <TitledSection title={t('ratings.updateVisibility')}>
      <Box display="flex" flexDirection="column" gap="8px" py={1}>
        <Button
          color="primary"
          variant="contained"
          size="small"
          onClick={() => updateRatings(true)}
          startIcon={<Visibility />}
        >
          <span>
            <Trans t={t} i18nKey="ratings.markAllAsPublic">
              Mark all as <strong>public</strong>
            </Trans>
          </span>
        </Button>
        <Button
          color="primary"
          variant="contained"
          size="small"
          onClick={() => updateRatings(false)}
          startIcon={<VisibilityOff />}
        >
          <span>
            <Trans t={t} i18nKey="ratings.markAllAsPrivate">
              Mark all as <strong>private</strong>
            </Trans>
          </span>
        </Button>
      </Box>
    </TitledSection>
  );
}

export default MarkAllRatings;
