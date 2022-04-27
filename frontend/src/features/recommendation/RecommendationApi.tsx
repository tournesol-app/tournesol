import {
  PaginatedRecommendationList,
  PollCriteria,
  PollsService,
} from 'src/services/openapi';
import { YOUTUBE_POLL_NAME } from 'src/utils/constants';

const getParamValueAsNumber = (
  params: URLSearchParams,
  key: string
): number | undefined => {
  const value = params.get(key);
  return value ? Number(value) : undefined;
};

/**
 * Replace the key `date` of `params` by a new one compatible with the API.
 */
const buildDateURLParameter = (
  pollName: string,
  params: URLSearchParams
): void => {
  function format(str: string) {
    if (str.length == 1) {
      return '0'.concat(str);
    } else if (str.length == 4) {
      return str.slice(2);
    } else {
      return str;
    }
  }

  if (pollName === YOUTUBE_POLL_NAME) {
    const conversionTime = new Map();
    const dayInMillisecondes = 1000 * 60 * 60 * 24;

    conversionTime.set('Any', 1);
    // Set today to 36 hours instead of 24; to get most of the videos from the
    // previous day
    conversionTime.set('Today', dayInMillisecondes * 1.5);
    conversionTime.set('Week', dayInMillisecondes * 7);
    conversionTime.set('Month', dayInMillisecondes * 31);
    conversionTime.set('Year', dayInMillisecondes * 365);
    const dateNow = Date.now();

    if (params.get('date')) {
      const date = params.get('date');
      params.delete('date');
      if (date != 'Any') {
        // TODO: figure out why adding 1 month is needed here
        const limitPublicationDateMilliseconds =
          dateNow - conversionTime.get(date);
        const param_date = new Date(limitPublicationDateMilliseconds);
        const [d, m, y, H, M, S] = [
          param_date.getDate().toString(),
          (param_date.getMonth() + 1).toString(),
          param_date.getFullYear().toString(),
          param_date.getHours().toString(),
          param_date.getMinutes().toString(),
          param_date.getSeconds().toString(),
        ].map((t) => format(t));
        params.append('date_gte', `${d}-${m}-${y}-${H}-${M}-${S}`);
      }
    }
  }
};

/**
 * Return a metadata `Record` based on the URL parameters, compliant with the
 * given poll.
 *
 * This `Record` is meant to be used as parameter of the generated API
 * services.
 */
const getMetadataFilter = (
  pollName: string,
  params: URLSearchParams
): Record<string, string | string[]> => {
  const metadata: Record<string, string | string[]> = {};

  // build a filter for the YouTube poll
  if (pollName === YOUTUBE_POLL_NAME) {
    const languageFilter = params.get('language');
    const uploaderFilter = params.get('uploader');

    if (languageFilter) {
      metadata['language'] = languageFilter.split(',');
    }

    if (uploaderFilter) {
      metadata['uploader'] = uploaderFilter;
    }
  }

  return metadata;
};

/**
 * Return the recommendations of a given poll.
 */
export const getRecommendations = async (
  pollName: string,
  limit: number,
  searchString: string,
  criterias: PollCriteria[]
): Promise<PaginatedRecommendationList> => {
  const params = new URLSearchParams(searchString);

  buildDateURLParameter(pollName, params);

  try {
    return await PollsService.pollsRecommendationsList({
      name: pollName,
      limit: limit,
      offset: getParamValueAsNumber(params, 'offset'),
      search: params.get('search') ?? undefined,
      dateGte: params.get('date_gte') ?? undefined,
      unsafe: params.get('unsafe') === 'true' ?? undefined,
      metadata: getMetadataFilter(pollName, params),
      weights: Object.fromEntries(
        criterias.map((c) => [c.name, getParamValueAsNumber(params, c.name)])
      ),
    });
  } catch (err) {
    console.error(err);
    return {
      results: [],
      count: 0,
    };
  }
};
