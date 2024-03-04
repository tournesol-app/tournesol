import React from 'react';
import { Link } from 'react-router-dom';

import { Button, ButtonGroup } from '@mui/material';
import { Science, YouTube } from '@mui/icons-material';

interface EventsMenuProps {
  selected: string;
}

const EventsMenu = ({ selected }: EventsMenuProps) => {
  return (
    <ButtonGroup
      color="secondary"
      fullWidth
      variant="outlined"
      aria-label="Basic button group"
    >
      <Button
        component={Link}
        to="/events"
        variant={selected === 'all' ? 'contained' : undefined}
      >
        All events
      </Button>
      <Button
        component={Link}
        to="/live"
        startIcon={<YouTube />}
        variant={selected === 'live' ? 'contained' : undefined}
      >
        Live
      </Button>
      <Button
        component={Link}
        to="/talks"
        startIcon={<Science />}
        variant={selected === 'talks' ? 'contained' : undefined}
      >
        Talks
      </Button>
    </ButtonGroup>
  );
};

export default EventsMenu;
