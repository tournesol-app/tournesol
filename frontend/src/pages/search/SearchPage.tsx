import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';

import { Box } from '@mui/material';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
  PreferencesIconButtonLink,
} from 'src/components';
import BackIconButton from 'src/components/buttons/BackIconButton';
import { useCurrentPoll } from 'src/hooks';
import EntityList from 'src/features/entities/EntityList';
import { selectLogin } from 'src/features/login/loginSlice';
import ShareMenuButton from 'src/features/menus/ShareMenuButton';
import SearchFilter from 'src/features/recommendation/SearchFilter';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { PaginatedRecommendationList } from 'src/services/openapi';
import { getRecommendations } from 'src/utils/api/recommendations';
import { getFeedTopItemsPageName } from 'src/utils/constants';
import { PollUserSettingsKeys } from 'src/utils/types';
import {
  loadRecommendationsLanguages,
  recommendationsLanguagesFromNavigator,
  saveRecommendationsLanguages,
} from 'src/utils/recommendationsLanguages';

const ENTITIES_LIMIT = 20;

const SearchPage = () => {
  const { t } = useTranslation();

  const history = useHistory();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);

  const { name: pollName, criterias, options } = useCurrentPoll();
  const autoLangDiscovery = options?.defaultRecoLanguageDiscovery ?? false;

  const loginState = useSelector(selectLogin);
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
    // `searchParams` is defined as a mutable object outside of this effect.
    // It's safer to recreate it here, instead of adding a dependency to the
    // current effect.
    const searchString = new URLSearchParams(location.search);
    searchString.set('offset', offset.toString());

    if (autoLangDiscovery && searchString.get('language') === null) {
      let loadedLanguages = preferredLanguages?.join(',') ?? null;

      if (loadedLanguages === null) {
        // TODO: load from a != local storage key?
        // TODO: any reason to keep this logic? the browser extension?
        loadedLanguages = loadRecommendationsLanguages();
      }

      if (loadedLanguages === null) {
        loadedLanguages = recommendationsLanguagesFromNavigator();
        // TODO: save as a != local storage key?
        saveRecommendationsLanguages(loadedLanguages);
      }

      searchString.set('language', loadedLanguages);
      history.replace({ search: searchString.toString() });
      return;
    }

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
    autoLangDiscovery,
    criterias,
    history,
    location.search,
    offset,
    options,
    preferredLanguages,
    pollName,
  ]);

  const createBackButtonPath = () => {
    const backPath = loginState.backPath;
    const backParams = loginState.backParams;

    if (!backPath) {
      return '';
    }

    return backParams ? backPath + '?' + backParams : backPath;
  };

  const backButtonPath = createBackButtonPath();

  return (
    <>
      <ContentHeader title={getFeedTopItemsPageName(t, pollName)} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box mb={4} px={{ xs: 2, sm: 0 }}>
          <SearchFilter
            extraActions={
              <Box display="flex" gap={1}>
                <ShareMenuButton isIcon />
                {backButtonPath && <BackIconButton path={backButtonPath} />}
                <PreferencesIconButtonLink hash={`#${pollName}-search`} />
              </Box>
            }
          />
        </Box>
        <LoaderWrapper isLoading={isLoading}>
          <EntityList
            entities={entities.results}
            emptyMessage={isLoading ? '' : t('entityList.noItems')}
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

export default SearchPage;
