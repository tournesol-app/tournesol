import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import { Box } from '@mui/material';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
  PreferencesIconButtonLink,
  SearchIconButtonLink,
} from 'src/components';
import { useCurrentPoll } from 'src/hooks';
import EntityList from 'src/features/entities/EntityList';
import { updateBackNagivation } from 'src/features/login/loginSlice';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import {
  getFeedTopItemsPageName,
  pollVideosFilters,
} from 'src/utils/constants';
import { PollUserSettingsKeys } from 'src/utils/types';
import {
  initRecoLanguagesWithLocalStorage,
  saveRecoLanguagesToLocalStorage,
} from 'src/utils/recommendationsLanguages';

const ALLOWED_SEARCH_PARAMS = [
  pollVideosFilters.date,
  pollVideosFilters.language,
  'offset',
];
const ENTITIES_LIMIT = 20;
export const FEED_LANG_KEY = 'top-items';

const filterAllowedParams = (
  searchParams: URLSearchParams,
  allowList: string[]
) => {
  for (const key of [...searchParams.keys()]) {
    if (!allowList.includes(key)) {
      searchParams.delete(key);
    }
  }

  return searchParams;
};

const FeedTopItems = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const langsAutoDiscovery = options?.defaultRecoLanguageDiscovery ?? false;

  const userSettings = useSelector(selectSettings).settings;
  const preferredLanguages =
    userSettings?.[pollName as PollUserSettingsKeys]?.feed_topitems__languages;

  const [isLoading, setIsLoading] = useState(true);
  const [entities, setEntities] = useState<PaginatedRecommendationList>({
    count: 0,
    results: [],
  });

  const onOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  };

  useEffect(() => {
    const currentParams = filterAllowedParams(
      new URLSearchParams(location.search),
      ALLOWED_SEARCH_PARAMS
    );

    dispatch(
      updateBackNagivation({
        backPath: location.pathname,
        backParams: currentParams.toString(),
      })
    );
  }, [dispatch, location.pathname, location.search]);

  useEffect(() => {
    // `searchParams` is defined as a mutable object outside of this effect.
    // It's safer to recreate it here, instead of adding a dependency to the
    // current effect.
    const searchString = new URLSearchParams(location.search);
    searchString.set('offset', offset.toString());

    if (langsAutoDiscovery && searchString.get('language') === null) {
      let loadedLanguages = preferredLanguages?.join(',') ?? null;

      if (loadedLanguages === null) {
        loadedLanguages = initRecoLanguagesWithLocalStorage(
          pollName,
          FEED_LANG_KEY
        );
      }

      searchString.set('language', loadedLanguages);
      history.replace({ search: searchString.toString() });
      return;
    }

    filterAllowedParams(searchString, ALLOWED_SEARCH_PARAMS);

    const fetchEntities = async () => {
      setIsLoading(true);
      try {
        const newEntities = await getRecommendations(
          pollName,
          ENTITIES_LIMIT,
          searchString.toString(),
          criterias,
          options
        );
        setEntities(newEntities);
      } catch {
        // todo: display a message
      } finally {
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [
    langsAutoDiscovery,
    criterias,
    history,
    location.search,
    offset,
    options,
    preferredLanguages,
    pollName,
  ]);

  const makeSearchPageSearchParams = () => {
    const searchPageSearchParams = filterAllowedParams(
      new URLSearchParams(location.search),
      ALLOWED_SEARCH_PARAMS
    );
    searchPageSearchParams.set('offset', offset.toString());
    return searchPageSearchParams;
  };

  return (
    <>
      <ContentHeader title={getFeedTopItemsPageName(t, pollName)} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box mb={4} px={{ xs: 2, sm: 0 }}>
          <SearchFilter
            disableAdvanced
            disableCriteria
            disableDuration
            extraActions={
              <Box display="flex" gap={1}>
                <SearchIconButtonLink
                  params={makeSearchPageSearchParams().toString()}
                />
                <PreferencesIconButtonLink hash={`#${pollName}-feed-top`} />
              </Box>
            }
            onLanguagesChange={(langs) =>
              saveRecoLanguagesToLocalStorage(pollName, FEED_LANG_KEY, langs)
            }
          />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              isLoading ? '' : t('entityList.noItemsMatchYourSearchCriteria')
            }
          />
        </LoaderWrapper>
        {!isLoading && (entities.count ?? 0) > 0 && (
          <Pagination
            offset={offset}
            count={entities.count ?? 0}
            onOffsetChange={onOffsetChange}
            limit={ENTITIES_LIMIT}
          />
        )}
      </ContentBox>
    </>
  );
};

export default FeedTopItems;
