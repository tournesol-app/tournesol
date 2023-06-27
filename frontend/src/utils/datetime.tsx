/**
 * Return a formatted local date of a string representing an ISO 8601 date
 * and time with timezone. Use it only to display information to humans aware
 * of the time zone contained in `datetime`, not to compute dates.
 *
 * If the supported format is not recognized, return null.
 *
 * Supported formats:
 *    - 2000-01-31T14:15:59+0200  -> 2000-01-31
 */
export const localDate = (datetime: string): string | null => {
  const datetimeSplit = datetime.split('T');

  if (datetimeSplit.length === 0) {
    return null;
  }

  const dateSplit = datetimeSplit[0].split('-');

  if (dateSplit.length !== 3) {
    return null;
  }

  return `${dateSplit[0]}-${dateSplit[1]}-${dateSplit[2]}`;
};

/**
 * Return the local time of a string representing an ISO 8601 date and time
 * with timezone. Use it only to display information to humans aware of the
 * time zone contained in `datetime`, not to compute dates.
 *
 * If the supported format is not recognized, return null.
 *
 * Supported formats:
 *    - 2000-01-31T14:15:59+0200  -> 14:15
 *    - 2000-01-31T14:15:59+02:00 -> 14:15
 *    - 2000-01-31T14:15:59+02    -> 14:15
 */
export const localTime = (datetime: string): string | null => {
  const datetimeSplit = datetime.split('T');

  if (datetimeSplit.length === 0) {
    return null;
  }

  const time = datetimeSplit[1].split('+');

  if (time.length !== 2) {
    return null;
  }

  const timeSplit = time[0].split(':');

  if (timeSplit.length !== 3) {
    return null;
  }

  return `${timeSplit[0]}:${timeSplit[1]}`;
};
