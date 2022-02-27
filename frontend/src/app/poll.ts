import React from 'react';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

interface PollContextValue {
  name: string;
  setPollName: React.Dispatch<React.SetStateAction<string>>;
}

export const PollContext = React.createContext<PollContextValue>({
  name: YOUTUBE_POLL_NAME,
  setPollName: (x) => x,
});
