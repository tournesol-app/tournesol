import { PollStatistics, Statistics } from 'src/services/openapi';

/**
 * Given a Statistics object, return the PollStatistics of the poll identified
 * by its `name`.
 */
export const getPollStats = (
  publicStats: Statistics | undefined,
  name: string
): PollStatistics | undefined => {
  if (!publicStats) {
    return;
  }
  return publicStats.polls.find((poll) => poll.name === name);
};
