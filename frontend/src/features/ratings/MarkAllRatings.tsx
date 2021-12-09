import React, { useContext } from 'react';
import { Button, Box } from '@material-ui/core';
import { Visibility, VisibilityOff } from '@material-ui/icons';
import { FilterSection } from 'src/components';
import { UsersService } from 'src/services/openapi';
import { RatingsContext } from 'src/features/videos/PublicStatusAction';

function MarkAllRatings() {
  const { onChange: onRatingChange } = useContext(RatingsContext);

  const updateRatings = async (isPublic: boolean) => {
    await UsersService.usersMeContributorRatingsAllPartialUpdate({
      requestBody: { is_public: isPublic },
    });
    if (onRatingChange) {
      onRatingChange();
    }
  };

  return (
    <FilterSection title="Update visibility">
      <Box display="flex" flexDirection="column" gridGap="8px" py={1}>
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
    </FilterSection>
  );
}

export default MarkAllRatings;
