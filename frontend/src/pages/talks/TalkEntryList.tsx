import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import TalkSingleEntry from 'src/pages/talks/TalkSingleEntry';
import { TalkEntry } from 'src/services/openapi';

const TalkEntryList = ({ talks }: { talks: Array<TalkEntry> }) => {
  return (
    <Grid container justifyContent="column" spacing={4}>
      {talks.map((talk, idx) => (
        <Grid key={`${idx}_${talk.name}`} width="100%">
          <TalkSingleEntry key={talk.name} talk={talk} />
        </Grid>
      ))}
    </Grid>
  );
};

export default TalkEntryList;
