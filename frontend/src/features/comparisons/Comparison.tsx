import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';
import { TFunction, useTranslation } from 'react-i18next';
import { Location } from 'history';

import {
  Box,
  Card,
  CircularProgress,
  Grid,
  useMediaQuery,
  useTheme,
} from '@mui/material';

import { useDocumentTitle, useNotifications } from 'src/hooks';
import {
  UsersService,
  ComparisonRequest,
  ApiError,
} from 'src/services/openapi';
import EntitySelector, {
  SelectorValue,
} from 'src/features/entity_selector/EntitySelector';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { SuggestionHistory } from 'src/features/suggestions/suggestionHistory';
import { autoSuggestionPool } from 'src/features/suggestions/suggestionPool';
import {
  getEntityMetadataName,
  getPollName,
  UID_YT_NAMESPACE,
} from 'src/utils/constants';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import ComparisonEntityContexts from './ComparisonEntityContexts';
import ComparisonHelper from './ComparisonHelper';
import ComparisonInput from './ComparisonInput';
import { ComparisonsContext } from 'src/pages/comparisons/Comparison';

export const UID_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'uidA',
  vidB: 'uidB',
};
const LEGACY_PARAMS: { vidA: string; vidB: string } = {
  vidA: 'videoA',
  vidB: 'videoB',
};

const COMPARISON_MAX_WIDTH = '880px';

const getUidsFromLocation = (location: Location) => {
  const searchParams = new URLSearchParams(location.search);
  let uidA = searchParams.get(UID_PARAMS.vidA);
  if (uidA === null) {
    const legacyA = searchParams.get(LEGACY_PARAMS.vidA);
    if (legacyA) {
      uidA = UID_YT_NAMESPACE + legacyA;
    }
  }
  let uidB = searchParams.get(UID_PARAMS.vidB);
  if (uidB === null) {
    const legacyB = searchParams.get(LEGACY_PARAMS.vidB);
    if (legacyB) {
      uidB = UID_YT_NAMESPACE + legacyB;
    }
  }
  return {
    uidA,
    uidB,
  };
};

const createPageTitle = (
  t: TFunction,
  pollName: string,
  nameA?: string,
  nameB?: string
): string | null => {
  if (!nameA || !nameB) {
    return null;
  }

  const titleA = nameA.length <= 32 ? nameA : `${nameA.substring(0, 32)}…`;
  const titleB = nameB.length <= 32 ? nameB : `${nameB.substring(0, 32)}…`;
  return `${titleA} 🆚 ${titleB} | Tournesol ${getPollName(t, pollName)}`;
};

interface Props {
  afterSubmitCallback?: (
    uidA: string,
    uidB: string
  ) => { uid: string; refreshLeft: boolean };
  autoFillSelectorA?: boolean;
  autoFillSelectorB?: boolean;
}

/**
 * The comparison UI.
 *
 * Containing two entity selectors and the criteria sliders. Note that it
 * currently uses the `useLocation` hook to update the URL parameters when
 * a entity uid is changed. Adding this component into a page will also add
 * these uids in the URL parameters.
 */
const Comparison = ({
  afterSubmitCallback,
  autoFillSelectorA = false,
  autoFillSelectorB = false,
}: Props) => {
  const { t, i18n } = useTranslation();
  const currentLang = i18n.resolvedLanguage;

  const theme = useTheme();
  const smallScreen = useMediaQuery(theme.breakpoints.down('sm'));

  const history = useHistory();
  const location = useLocation();
  const { showSuccessAlert, displayErrorsFrom } = useNotifications();
  const { setHasLoopedThroughCriteria } = useContext(ComparisonsContext);

  const { name: pollName, options } = useCurrentPoll();
  const mainCriterion = options?.mainCriterionName;

  const initializeWithSuggestions = useRef(true);
  const [isLoading, setIsLoading] = useState(true);

  const selectorAHistory = useRef(new SuggestionHistory(autoSuggestionPool));
  const selectorBHistory = useRef(new SuggestionHistory(autoSuggestionPool));

  const [initialComparison, setInitialComparison] =
    useState<ComparisonRequest | null>(null);

  const { uidA, uidB } = getUidsFromLocation(location);
  const [selectorA, setSelectorA] = useState<SelectorValue>({
    uid: uidA,
    rating: null,
  });
  const [selectorB, setSelectorB] = useState<SelectorValue>({
    uid: uidB,
    rating: null,
  });

  const [pageTitle, setPageTitle] = useState(
    `${t('comparison.newComparison')}`
  );
  useDocumentTitle(pageTitle);

  useEffect(() => {
    if (selectorA.rating?.entity && selectorB.rating?.entity) {
      const nameA = getEntityMetadataName(pollName, selectorA.rating?.entity);
      const nameB = getEntityMetadataName(pollName, selectorB.rating?.entity);
      const title = createPageTitle(t, pollName, nameA, nameB);
      if (title) {
        setPageTitle(title);
      }
    } else {
      setPageTitle(`${t('comparison.newComparison')}`);
    }
  }, [pollName, selectorA.rating?.entity, selectorB.rating?.entity, t]);

  const onChange = useCallback(
    (vidKey: 'vidA' | 'vidB') => (newValue: SelectorValue) => {
      // `window.location` is used here, to avoid memoizing the location
      // defined in component state, which could be obsolete and cause a
      // race condition when the 2 selectors are updated concurrently.
      const searchParams = new URLSearchParams(window.location.search);
      const uid = newValue.uid;

      const uidKey = UID_PARAMS[vidKey];
      if ((searchParams.get(uidKey) || '') !== uid) {
        searchParams.set(uidKey, uid || '');
        searchParams.delete(LEGACY_PARAMS[vidKey]);
        history.replace({ search: searchParams.toString() });
      }
      if (vidKey === 'vidA') {
        setSelectorA(newValue);
      } else if (vidKey === 'vidB') {
        setSelectorB(newValue);
      }

      setHasLoopedThroughCriteria?.(false);
    },
    [history, setHasLoopedThroughCriteria]
  );

  const onChangeA = useMemo(() => onChange('vidA'), [onChange]);
  const onChangeB = useMemo(() => onChange('vidB'), [onChange]);

  const userSettings = useSelector(selectSettings)?.settings;
  const orderedByPreferences =
    userSettings.videos?.comparison__criteria_order ?? [];

  const orderedCriteriaRated =
    [mainCriterion, ...orderedByPreferences].every((orderedCrit) =>
      initialComparison?.criteria_scores.find(
        (critScore) => critScore.criteria === orderedCrit
      )
    ) ?? false;

  /**
   * Automatically initialize the first comparison if the autoFill parameters
   * are true.
   */
  useEffect(() => {
    if (initializeWithSuggestions.current === false) {
      return;
    }

    const autoFillComparison = async () => {
      let autoUidA = null;
      let autoUidB = null;

      if (uidA) {
        selectorAHistory.current.appendRight(pollName, uidA);
      } else if (autoFillSelectorA) {
        autoUidA = await selectorAHistory.current.nextRightOrSuggestion(
          pollName,
          [uidA, uidB]
        );
      }

      if (uidB) {
        selectorBHistory.current.appendRight(pollName, uidB);
      } else if (autoFillSelectorB) {
        autoUidB = await selectorBHistory.current.nextRightOrSuggestion(
          pollName,
          [autoUidA || uidA, uidB]
        );
      }

      if (autoUidA) {
        onChangeA({ uid: autoUidA, rating: null });
      }
      if (autoUidB) {
        onChangeB({ uid: autoUidB, rating: null });
      }

      initializeWithSuggestions.current = false;
    };

    autoFillComparison();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    // Wait for the potential initialization of the suggested entities before
    // retrieving the comparison.
    if (initializeWithSuggestions.current) {
      return;
    }

    setIsLoading(true);
    setInitialComparison(null);

    if (selectorA.uid !== uidA) {
      setSelectorA({ uid: uidA, rating: null });
    }
    if (selectorB.uid !== uidB) {
      setSelectorB({ uid: uidB, rating: null });
    }

    if (uidA && uidB)
      UsersService.usersMeComparisonsRetrieve({
        pollName,
        uidA,
        uidB,
      })
        .then((comparison) => {
          setInitialComparison(comparison);
          setIsLoading(false);
        })
        .catch(() => {
          setInitialComparison(null);
          setIsLoading(false);
        });
  }, [pollName, uidA, uidB, selectorA.uid, selectorB.uid]);

  /**
   * When the UI language changes, refresh the ratings to retrieve the
   * corresponding localized entity contexts.
   */
  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (selectorA.uid) {
      setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
    }

    if (selectorB.uid) {
      setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentLang]);

  const onSubmitComparison = async (
    c: ComparisonRequest,
    partialUpdate?: boolean
  ) => {
    try {
      if (initialComparison) {
        const { entity_a, entity_b, criteria_scores, duration_ms } = c;

        if (partialUpdate === true) {
          const resp = await UsersService.usersMeComparisonsPartialUpdate({
            pollName,
            uidA: entity_a.uid,
            uidB: entity_b.uid,
            requestBody: { criteria_scores, duration_ms },
          });
          setInitialComparison(resp);
        } else {
          await UsersService.usersMeComparisonsUpdate({
            pollName,
            uidA: entity_a.uid,
            uidB: entity_b.uid,
            requestBody: { criteria_scores, duration_ms },
          });
        }
      } else {
        await UsersService.usersMeComparisonsCreate({
          pollName,
          requestBody: c,
        });
        setInitialComparison(c);
      }
    } catch (e) {
      displayErrorsFrom(e as ApiError);
      throw e;
    }

    if (afterSubmitCallback) {
      const suggestion = afterSubmitCallback(c.entity_a.uid, c.entity_b.uid);

      // Do not update the selectors when receiving this message.
      if (suggestion.uid === '__UNMOUNTING_PARENT__') {
        return;
      }

      if (suggestion.uid) {
        if (suggestion.refreshLeft) {
          onChangeA({ uid: suggestion.uid, rating: null });
          setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
        } else {
          onChangeB({ uid: suggestion.uid, rating: null });
          setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
        }
      }
    } else {
      setSelectorA((value) => ({ ...value, ratingIsExpired: true }));
      setSelectorB((value) => ({ ...value, ratingIsExpired: true }));
    }

    if (smallScreen) {
      showSuccessAlert(t('comparison.ok'), 1200);
    } else {
      showSuccessAlert(t('comparison.successfullySubmitted'));
    }
  };

  return (
    <>
      <Grid
        container
        gap={1}
        mb={1}
        maxWidth={COMPARISON_MAX_WIDTH}
        // Allow the CriterionButtons to slide behind the entity selectors.
        zIndex={theme.zIndex.comparisonElevation1}
      >
        <Grid item xs display="flex" flexDirection="column" alignSelf="stretch">
          <EntitySelector
            alignment="left"
            value={selectorA}
            onChange={onChangeA}
            otherUid={uidB}
            history={selectorAHistory.current}
            orderedCriteriaRated={orderedCriteriaRated}
          />
        </Grid>
        <Grid item xs display="flex" flexDirection="column" alignSelf="stretch">
          <EntitySelector
            alignment="right"
            value={selectorB}
            onChange={onChangeB}
            otherUid={uidA}
            history={selectorBHistory.current}
            orderedCriteriaRated={orderedCriteriaRated}
          />
        </Grid>
      </Grid>
      <Grid container gap={1} maxWidth={COMPARISON_MAX_WIDTH}>
        <Grid
          item
          xs={12}
          display="flex"
          alignItems="center"
          flexDirection="column"
          sx={{
            '&:empty': {
              display: 'none',
            },
          }}
          component={Card}
          elevation={2}
        >
          <ComparisonHelper />
        </Grid>
        <Grid item xs={12} sx={{ '&:empty': { display: 'none' } }}>
          <ComparisonEntityContexts
            selectorA={selectorA}
            selectorB={selectorB}
          />
        </Grid>
        <Grid
          item
          xs={12}
          display="flex"
          alignItems="stretch"
          flexDirection="column"
          gap={1}
          sx={{
            '&:empty': { display: 'none' },
          }}
        >
          {selectorA.rating && selectorB.rating ? (
            isLoading ? (
              <Box display="flex" justifyContent="center">
                <CircularProgress color="secondary" />
              </Box>
            ) : (
              <ComparisonInput
                uidA={uidA || ''}
                uidB={uidB || ''}
                onSubmit={onSubmitComparison}
                initialComparison={initialComparison}
                isComparisonPublic={
                  selectorA.rating.individual_rating.is_public &&
                  selectorB.rating.individual_rating.is_public
                }
              />
            )
          ) : selectorA.uid && selectorB.uid ? (
            // Entities are selected but ratings are not loaded yet
            <Box display="flex" justifyContent="center">
              <CircularProgress color="secondary" />
            </Box>
          ) : null}
        </Grid>
      </Grid>
    </>
  );
};

export default Comparison;
