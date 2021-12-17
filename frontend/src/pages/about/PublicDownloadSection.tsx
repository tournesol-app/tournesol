import React from 'react';

import { Typography, Button } from '@material-ui/core';

// PublicDownloadSection is a paragraph displayed on the HomePage
// that helps users know how to download the public video comparisons available for their use case
const PublicDownloadSection = () => {
  const api_url = process.env.REACT_APP_API_URL;
  return (
    <>
      <Typography variant="h1">Public Database</Typography>
      <Typography paragraph>
        Contributors on Tournesol can decide to make their data public. We hope
        this important data will prove useful for researchers on ethics of
        algorithms and large scale recommender systems. Our public database can
        be downloaded by clicking the button below and is published under{' '}
        <a
          href="https://opendatacommons.org/licenses/by/1-0/"
          style={{ color: 'white' }}
        >
          Open Data Commons Attribution License (ODC-By)
        </a>
        .
      </Typography>
      <Typography paragraph>
        Finally, we would like to thank all of the contributors who compared
        videos on Tournesol. We count so far about 2500 users who compared 9000
        times more than 3000 videos.
      </Typography>

      <Button
        component="a"
        href={`${api_url}/exports/comparisons/`}
        download="tournesol_public_export.csv"
        color="primary"
        variant="contained"
      >
        Click to Download
      </Button>
    </>
  );
};

export default PublicDownloadSection;
