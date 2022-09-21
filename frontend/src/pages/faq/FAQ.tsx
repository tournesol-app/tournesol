import React from 'react';

import { Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';

const FAQ = () => {
  return (
    <>
      <ContentHeader title="Frequently Asked Questions" />
      <ContentBox maxWidth="md">
        <Typography variant="h4" gutterBottom>
          Can you explain what is Tournesol again?
        </Typography>
        <Typography paragraph textAlign="justify">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
          culpa qui officia deserunt mollit anim id est laborum.
        </Typography>

        <Typography variant="h4" gutterBottom>
          Why should I participate?
        </Typography>
        <Typography paragraph textAlign="justify">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </Typography>

        <Typography variant="h4" gutterBottom>
          I like both video Im comparing, what should I do?
        </Typography>
        <Typography paragraph textAlign="justify">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat.
        </Typography>
      </ContentBox>
    </>
  );
};

export default FAQ;
