import React from 'react';

import { Link } from 'react-router-dom';
import { Typography, Button, Box } from '@material-ui/core';

// ContributeSection is a paragraph displayed on the HomePage
// that helps users know how to contribute as users of Tournesol
const ContributeSection = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">Contribute!</Typography>
      <Typography paragraph>
        Tournesol identifies high quality content from comparisons provided by
        the community. To contribute, you must compare videos that you have
        watched. First copy paste two links to videos, then tell us which video
        you think should be largely recommended. If you want to you can also
        compare the videos in more details based on the multiple comparison
        criterias.
      </Typography>
      <Button
        color="primary"
        variant="contained"
        component={Link}
        to="/comparison"
      >
        Compare videos now
      </Button>
    </Box>
  );
};

export default ContributeSection;
