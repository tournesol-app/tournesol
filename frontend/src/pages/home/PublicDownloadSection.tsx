import React from 'react';
import { Typography, Button, Box } from '@material-ui/core';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
  const api_url = process.env.REACT_APP_API_URL;
  return (
    <Box
      display="flex"
      flexDirection="column"
      color="white"
      maxWidth="640px"
      alignItems="flex-start"
    >
      <Typography variant="h1">Download Public Dataset!</Typography>
      <Typography paragraph>
        Contributors on Tournesol can decide to make their data public. You may
        download the dataset of all data publicly available. We hope this
        important data will prove useful for researchers on ethics of algorithms
        and large scale recommender systems.
      </Typography>
      <Button
        component="a"
        href={`${api_url}/exports/comparisons/`}
        // to change once zip folder functionality is implemented on the backend
        download="export.csv"
        color="primary"
        variant="contained"
      >
        Click to Download
      </Button>
    </Box>
  );
};

export default PublicDownloadSection;
