import React, { useContext } from 'react';
import { Button, Box } from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useSnackbar } from 'notistack';

import { TitledSection } from 'src/components';
import { UsersService } from 'src/services/openapi';
import { RatingsContext } from 'src/features/videos/PublicStatusAction';
import { showErrorAlert, showInfoAlert } from 'src/utils/notifications';

function MarkAllRatings() {
  const { onChange: onRatingChange } = useContext(RatingsContext);
  const { enqueueSnackbar } = useSnackbar();

  const updateRatings = async (isPublic: boolean) => {
    try {
      await UsersService.usersMeContributorRatingsAllPartialUpdate({
        requestBody: { is_public: isPublic },
      });
    } catch (err) {
      showErrorAlert(enqueueSnackbar, err?.message || 'Server error');
      return;
    }
    if (onRatingChange) {
      onRatingChange();
    }
    showInfoAlert(
      enqueueSnackbar,
      isPublic
        ? 'All your ratings have been marked as public.'
        : 'All your ratings have been marked as private.'
    );
  };

  return (
    <TitledSection title="Update visibility">
      <Box display="flex" flexDirection="column" gap="8px" py={1}>
        <Button
          color="primary"
          variant="contained"
          size="small"
          onClick={() => updateRatings(true)}
          startIcon={<Visibility />}
        >
          <span>
            Mark all as <strong>public</strong>
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
            Mark all as <strong>private</strong>
          </span>
        </Button>
      </Box>
    </TitledSection>
  );
}

export default MarkAllRatings;
