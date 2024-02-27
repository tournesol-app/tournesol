import React from 'react';

import Grid from '@mui/material/Unstable_Grid2';

import EventSingleEntry from 'src/pages/events/EventSingleEntry';
import { TournesolEvent } from 'src/services/openapi';

const EventEntryList = ({ events }: { events: Array<TournesolEvent> }) => {
  return (
    <Grid container justifyContent="column" spacing={4}>
      {events.map((event, idx) => (
        <Grid key={`${idx}_${event.name}`} width="100%">
          <EventSingleEntry key={event.name} event={event} />
        </Grid>
      ))}
    </Grid>
  );
};

export default EventEntryList;
