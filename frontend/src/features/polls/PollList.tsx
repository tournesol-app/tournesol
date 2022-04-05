import React from 'react';
import { Stack } from '@mui/material';
import PollLargeButton from 'src/features/polls/PollLargeButton';
import { polls } from 'src/utils/constants';

const orderedPolls = [...polls].sort((a, b) => a.displayOrder - b.displayOrder);

const PollList = () => {
  return (
    <Stack direction="row" spacing={2}>
      {orderedPolls.map((poll) => {
        return <PollLargeButton key={poll.name} poll={poll} />;
      })}
    </Stack>
  );
};

export default PollList;
