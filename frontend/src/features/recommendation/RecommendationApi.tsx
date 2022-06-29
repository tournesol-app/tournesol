import {
  PaginatedRecommendationList,
  PollCriteria,
  PollsService,
} from 'src/services/openapi';
import {
  PRESIDENTIELLE_2022_POLL_NAME,
  YOUTUBE_POLL_NAME,
} from 'src/utils/constants';
import { SelectablePoll } from 'src/utils/types';

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
  if (pollName === YOUTUBE_POLL_NAME) {
    const conversionTime = new Map();
    const dayInMillisecs = 1000 * 60 * 60 * 24;

    conversionTime.set('Any', 1);
    // Set today to 36 hours instead of 24; to get most of the videos from the
    // previous day
    conversionTime.set('Today', dayInMillisecs * 1.5);
    conversionTime.set('Week', dayInMillisecs * 7);
    conversionTime.set('Month', dayInMillisecs * 31);
    conversionTime.set('Year', dayInMillisecs * 365);

    if (params.get('date')) {
      const date = params.get('date');
      params.delete('date');

      if (date != 'Any') {
        const param_date = new Date(Date.now() - conversionTime.get(date));
        params.append('date_gte', param_date.toISOString());
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
    const durationLteFilter = params.get('duration_lte');
    const durationGteFilter = params.get('duration_gte');

    const languageFilter = params.get('language');
    const uploaderFilter = params.get('uploader');

    if (languageFilter) {
      metadata['language'] = languageFilter.split(',');
    }

    if (uploaderFilter) {
      metadata['uploader'] = uploaderFilter;
    }

    if (durationLteFilter) {
      // from minutes to seconds
      metadata['duration:lte:int'] = (
        parseInt(durationLteFilter) * 60
      ).toString();
    }

    if (durationGteFilter) {
      // from minutes to seconds
      metadata['duration:gte:int'] = (
        parseInt(durationGteFilter) * 60
      ).toString();
    }
  }

  return metadata;
};

export enum ScoreModeEnum {
  DEFAULT = 'default',
  ALL_EQUAL = 'all_equal',
  TRUSTED_ONLY = 'trusted_only',
}

/**
 * Return the recommendations of a given poll.
 */
export const getRecommendations = async (
  pollName: string,
  limit: number,
  searchString: string,
  criterias: PollCriteria[],
  pollOptions?: SelectablePoll
): Promise<PaginatedRecommendationList> => {
  const params = new URLSearchParams(searchString);

  buildDateURLParameter(pollName, params);

  let criteriaWeights = Object.fromEntries(
    criterias.map((c) => [c.name, getParamValueAsNumber(params, c.name)])
  );

  /*
    Temporary workaround for "presidentielle2022":
    Contrary to poll "videos" where the default order for recommendations is an aggregation of
    criteria, here we need to sort by the main criterion only (if custom weights are not provided).
    2 things to fix before removing this workaround:
      - update the backend implementation of "tournesol_score" to apply this new definition
      - make sure that `CriteriaFilter` behaves correctly on initialization, and that its state
      persists after the filter section is closed or the page is refreshed.
  */
  if (
    pollName === PRESIDENTIELLE_2022_POLL_NAME &&
    Object.values(criteriaWeights).filter((x) => x != null).length === 0
  ) {
    criteriaWeights = {
      ...Object.fromEntries(criterias.map((c) => [c.name, 0])),
      [pollOptions?.mainCriterionName ?? '']: 100,
    };
  }

  try {
    return await PollsService.pollsRecommendationsList({
      name: pollName,
      limit: limit,
      offset: getParamValueAsNumber(params, 'offset'),
      search: params.get('search') ?? undefined,
      dateGte: params.get('date_gte') ?? undefined,
      unsafe: params.has('unsafe')
        ? params.get('unsafe') === 'true'
        : pollOptions?.unsafeDefault,
      metadata: getMetadataFilter(pollName, params),
      scoreMode: (params.get('score_mode') as ScoreModeEnum) ?? undefined,
      weights: criteriaWeights,
    });
  } catch (err) {
    console.error(err);
    return {
      results: [],
      count: 0,
    };
  }
};
