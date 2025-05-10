import React from 'react';

import Grid2 from '@mui/material/Grid2';

import EventSingleEntry from 'src/pages/events/EventSingleEntry';
import { TournesolEvent } from 'src/services/openapi';

const EventEntryList = ({ events }: { events: Array<TournesolEvent> }) => {
  return (
    <Grid2
      container
      spacing={4}
      sx={{
        justifyContent: 'column',
      }}
    >
      {events.map((event, idx) => (
        <Grid2
          key={`${idx}_${event.name}`}
          sx={{
            width: '100%',
          }}
        >
          <EventSingleEntry key={event.name} event={event} />
        </Grid2>
      ))}
    </Grid2>
  );
};

export default EventEntryList;
