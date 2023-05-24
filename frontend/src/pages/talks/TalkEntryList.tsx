import { Box } from '@mui/material';
import React from 'react';

import TalkSingleEntry from 'src/pages/talks/TalkSingleEntry';
import { TalkEntry } from 'src/services/mocks';

const TalkEntryList = ({ talks }: { talks: Array<TalkEntry> }) => {
  return (
    <>
      {talks.map((talk) => (
        <Box key={talk.uid} my={2}>
          <TalkSingleEntry key={`q_${talk.title}`} talk={talk} />
        </Box>
      ))}
    </>
  );
};

export default TalkEntryList;
