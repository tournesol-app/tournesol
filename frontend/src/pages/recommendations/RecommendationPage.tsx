import React, { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { useLocation, useHistory, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { Box, Grid } from '@mui/material';
import { Person } from '@mui/icons-material';

import { ContentBox, ContentHeader, LoaderWrapper } from 'src/components';
import Pagination from 'src/components/Pagination';
import PreferencesIconButtonLink from 'src/components/buttons/PreferencesIconButtonLink';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import EntityList from 'src/features/entities/EntityList';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import ShareMenuButton from 'src/features/menus/ShareMenuButton';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import type {
  PaginatedContributorRecommendationsList,
  PaginatedRecommendationList,
} from 'src/services/openapi';
import {
  getPublicPersonalRecommendations,
  getRecommendations,
} from 'src/utils/api/recommendations';
import { getRecommendationPageName } from 'src/utils/constants';
import {
  saveRecommendationsLanguages,
  loadRecommendationsLanguages,
  recommendationsLanguagesFromNavigator,
} from 'src/utils/recommendationsLanguages';
import { PollUserSettingsKeys } from 'src/utils/types';

/**
 * Display a collective or personal recommendations.
 *
 * The page also display a the search filters allowed in the current poll.
 */
function RecommendationsPage() {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const { baseUrl, name: pollName, criterias, options } = useCurrentPoll();
  const [isLoading, setIsLoading] = useState(true);

  const userSettings = useSelector(selectSettings).settings;
  const preferredLanguages =
    userSettings?.[pollName as PollUserSettingsKeys]
      ?.recommendations__default_languages;

  const allowPublicPersonalRecommendations =
    options?.allowPublicPersonalRecommendations ?? false;
  const { username } = useParams<{ username: string }>();

  // Can be compared to the current pathname, to determine if the
  // desired recommendations are collective or personal.
  const collectiveRecoPathname = `${baseUrl}/recommendations`;

  const displayPersonalRecommendations =
    allowPublicPersonalRecommendations &&
    location.pathname !== collectiveRecoPathname &&
    username !== undefined;

  const prov:
    | PaginatedRecommendationList
    | PaginatedContributorRecommendationsList = {
    count: 0,
    results: [],
  };

  const [entities, setEntities] = useState(prov);
  const entitiesCount = entities.count || 0;
  const searchParams = new URLSearchParams(location.search);

  const limit = 20;
  const offset = Number(searchParams.get('offset') || 0);
  const autoLanguageDiscovery = options?.defaultRecoLanguageDiscovery ?? false;

  const locationSearchRef = useRef<string>();

  function handleOffsetChange(newOffset: number) {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  }

  useEffect(() => {
    if (location.search === locationSearchRef.current) {
      // This ref is used as a precaution, to avoid triggering
      // this effect redundantly, eg if "history" has changed.
      return;
    }
    locationSearchRef.current = location.search;

    // `searchParams` is defined as a mutable object outside of this
    // effect. So it's safer to recreate it here, instead of adding
    // a dependency to the current effect.
    const searchParams = new URLSearchParams(location.search);
    if (autoLanguageDiscovery && searchParams.get('language') === null) {
      let loadedLanguages = preferredLanguages?.join(',') ?? null;

      if (loadedLanguages === null) {
        loadedLanguages = loadRecommendationsLanguages();
      }

      if (loadedLanguages === null) {
        loadedLanguages = recommendationsLanguagesFromNavigator();
        saveRecommendationsLanguages(loadedLanguages);
      }

      searchParams.set('language', loadedLanguages);
      history.replace({ search: searchParams.toString() });
      return;
    }

    const fetchEntities = async () => {
      setIsLoading(true);

      const newEntities = displayPersonalRecommendations
        ? // Get personal recommendations.
          await getPublicPersonalRecommendations(
            username,
            pollName,
            limit,
            location.search,
            criterias,
            options
          )
        : // Get collective recommendations.
          await getRecommendations(
            pollName,
            limit,
            location.search,
            criterias,
            options
          );

      // A response corresponding to a previous filter state is ignored.
      if (locationSearchRef.current === location.search) {
        setEntities(newEntities);
        setIsLoading(false);
      }
    };

    fetchEntities();
  }, [
    autoLanguageDiscovery,
    criterias,
    displayPersonalRecommendations,
    history,
    location.search,
    options,
    pollName,
    preferredLanguages,
    username,
  ]);

  return (
    <>
      {displayPersonalRecommendations ? (
        <ContentHeader
          title={getRecommendationPageName(t, pollName, true)}
          chipIcon={<Person />}
          chipLabel={t('recommendationsPage.chips.by') + ` ${username}`}
        />
      ) : (
        <ContentHeader title={getRecommendationPageName(t, pollName)} />
      )}
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box px={{ xs: 2, sm: 0 }}>
          <Grid container>
            {/* Filters section. */}
            <Grid item xs={12}>
              {/* Unsafe filter is not available when fetching personal recommendations */}
              <SearchFilter
                showAdvancedFilter={!displayPersonalRecommendations}
                extraActions={
                  <>
                    <ShareMenuButton isIcon />
                    <PreferencesIconButtonLink hash="#recommendations_page" />
                  </>
                }
              />
            </Grid>
          </Grid>
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={
              isLoading ? '' : t('noVideoCorrespondsToSearchCriterias')
            }
          />
        </LoaderWrapper>
        {!isLoading && entitiesCount > 0 && (
          <Pagination
            offset={offset}
            count={entitiesCount}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
}

export default RecommendationsPage;
