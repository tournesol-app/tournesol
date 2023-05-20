import React from 'react';
import { Typography, Box } from '@mui/material';
import { useTranslation } from 'react-i18next';

import PollList from 'src/features/polls/PollList';

const PollListSection = () => {
  const { t } = useTranslation();

  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography id="explore" variant="h4" gutterBottom>
        {t('home.exploreTournesolPossibilities')}
      </Typography>
      <Typography paragraph>
        {t('home.tournesolToComparedMultipleTypesOfAlternatives')}
      </Typography>
      <PollList />
    </Box>
  );
};

export default PollListSection;
