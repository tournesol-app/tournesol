import React from 'react';

import PollList from 'src/features/polls/PollList';
import { Typography, Box } from '@mui/material';

const PollListSection = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">
        Explore Tournesol&apos;s Possibilities
      </Typography>
      <Typography paragraph>
        Tournesol is used to compare multiple types of alternatives. See the
        list below and choose the Tournesol that is best for you
      </Typography>
      <PollList />
    </Box>
  );
};

export default PollListSection;
