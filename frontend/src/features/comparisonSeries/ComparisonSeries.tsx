import React, { useEffect, useRef, useState } from 'react';
import { Redirect, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import {
  Button,
  Container,
  Step,
  StepLabel,
  Stepper,
  Typography,
} from '@mui/material';

import DialogBox from 'src/components/DialogBox';
import LoaderWrapper from 'src/components/LoaderWrapper';
import Comparison, { UID_PARAMS } from 'src/features/comparisons/Comparison';
import { useLoginState } from 'src/hooks';
import { alreadyComparedWith, selectRandomEntity } from 'src/utils/entity';
import { TRACKED_EVENTS, trackEvent } from 'src/utils/analytics';
import { EntityResult, OrderedDialogs } from 'src/utils/types';
import { getSkippedBy, setSkippedBy } from 'src/utils/comparisonSeries/skip';
import { isMobileDevice } from 'src/utils/extension';
import { scrollToTop } from 'src/utils/ui';

const UNMOUNT_SIGNAL = '__UNMOUNTING_PARENT__';

// This constant controls the render of the series, if the `length` prop of
// the `ComparisonSeries` component is strictly inferior to this value, a
// simple `Comparison` component with not extra features will be rendered
// instead.
const MIN_LENGTH = 2;

interface Props {
  // The current step of the series.
  step: number;
  // Called when a comparison is made. This function given by the parent
  // component should increment the `step`.
  onStepUp: (target: number) => void;
  length: number;
  // The parent can provide the list of user's comparisons, to avoid suggesting
  // comparisons the user already made.
  initComparisonsMade: string[];
  generateInitial?: boolean;
  dialogs?: OrderedDialogs;
  dialogAdditionalActions?: { [key: string]: { action: React.ReactNode } };
  getAlternatives?: () => Promise<Array<EntityResult>>;
  // A magic flag that will enable additional behaviours specific to
  // tutorials, like  the anonymous tracking by our web analytics.
  isTutorial?: boolean;
  // Display the user's progression through the series.
  displayStepper?: boolean;
  // Redirect to this URL when the series is over.
  redirectTo?: string;
  keepUIDsAfterRedirect?: boolean;
  resumable?: boolean;
  // Allows the users to skip the series. If this value is set, the series
  // becomes skip-able. This value should be a unique name identifying the
  // series in the poll (can be suffixed by `_${pollName}`). Used as a local
  // storage key.
  skipKey?: string;
  // Only used if `skipKey` is defined.
  skipButtonLabel?: string;
}

const generateSteps = (length: number) => {
  const content = [];
  for (let i = 0; i < length; i++) {
    content.push(
      <Step key={i}>
        <StepLabel />
      </Step>
    );
  }
  return content;
};

const ComparisonSeries = ({
  step,
  onStepUp,
  length,
  initComparisonsMade,
  generateInitial,
  dialogs,
  dialogAdditionalActions,
  getAlternatives,
  isTutorial = false,
  displayStepper = false,
  redirectTo,
  keepUIDsAfterRedirect,
  resumable,
  skipKey,
  skipButtonLabel,
}: Props) => {
  const location = useLocation();

  const { t } = useTranslation();
  const { loginState } = useLoginState();

  const username = loginState.username;

  // trigger the initialization on the first render only, to allow users to
  // freely clear entities without being redirected once the series has started
  const initialize = useRef(
    generateInitial != undefined ? generateInitial : false
  );
  // display a circular progress placeholder while async requests are made to
  // initialize the component
  const [isLoading, setIsLoading] = React.useState(true);
  // open/close state of the `Dialog` component
  const [dialogOpen, setDialogOpen] = useState(true);
  // tell the `Comparison` to refresh the left entity, or the right one
  const [refreshLeft, setRefreshLeft] = useState(false);
  // a limited list of entities that can be used to suggest new comparisons
  const [alternatives, setAlternatives] = useState<Array<EntityResult>>([]);
  // an array of already made comparisons, allowing to not suggest two times the
  // same comparison to a user, formatted like this ['uidA/uidB', 'uidA/uidC']
  const [comparisonsMade, setComparisonsMade] = useState(initComparisonsMade);
  // a string representing the URL parameters of the first comparison that may be suggested
  const [firstComparisonParams, setFirstComparisonParams] = useState('');
  // has the series been skipped by the user?
  const [skipped, setSkipped] = useState(
    skipKey && username ? getSkippedBy(skipKey, username) === true : false
  );

  const searchParams = new URLSearchParams(location.search);
  const uidA: string = searchParams.get(UID_PARAMS.vidA) || '';
  const uidB: string = searchParams.get(UID_PARAMS.vidB) || '';

  /**
   * Build the list of `alternatives`. After each comparison, an entity
   * from this list can be selected to replace one of the two compared
   * entities.
   *
   * If the component has been mounted with `generateInitial` = true, build the
   * URL parameters that will be used to suggest the first comparison of the
   * series.
   */
  useEffect(() => {
    if (skipped) return;

    async function getAlternativesAsync(
      getAlts: () => Promise<Array<EntityResult>>
    ) {
      const alts = await getAlts();
      if (alts.length > 0) {
        setAlternatives(alts);
        return alts;
      }
      return [];
    }

    if (length >= MIN_LENGTH) {
      const alternativesPromise = getAlternatives
        ? getAlternativesAsync(getAlternatives)
        : Promise.resolve();

      alternativesPromise
        .then((entities) => {
          if (resumable && comparisonsMade.length > 0) {
            onStepUp(comparisonsMade.length);
          }

          if (entities && initialize.current && (uidA === '' || uidB === '')) {
            setFirstComparisonParams(
              genInitialComparisonParams(entities, comparisonsMade, uidA, uidB)
            );
          }
        })
        .then(() => setIsLoading(false));
    } else {
      // stop loading if no series is going to be rendered
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const afterSubmitCallback = (
    uidA: string,
    uidB: string
  ): { uid: string; refreshLeft: boolean } => {
    const lastComparison = uidA + '/' + uidB;
    const lastComparisonR = uidB + '/' + uidA;

    // if the submitted comparison has already been made:
    //   - do not update the comparisonsMade list
    //   - do not increment the step
    //   - do not display the dialog previously displayed
    //   - simply suggest a new comparison
    const comparisonIsNew =
      !comparisonsMade.includes(lastComparison) &&
      !comparisonsMade.includes(lastComparisonR);

    const newStep = comparisonIsNew ? step + 1 : step;
    if (step < length && comparisonIsNew) {
      onStepUp(newStep);
      scrollToTop('smooth');
    }

    // Anonymously track the users' progression through the tutorial, to
    // evaluate the tutorial's quality. DO NOT SEND ANY PERSONAL DATA.
    if (comparisonIsNew && isTutorial) {
      trackEvent(TRACKED_EVENTS.tutorial, { props: { step: step + 1 } });
    }

    // Inform the child component `<Comparison>` to not trigger any additional
    // refresh of its states. When the last comparison of the series is made,
    // this component will be unmounted, so does the child component
    // `<Comparison>`.
    if (newStep === length) {
      return { uid: UNMOUNT_SIGNAL, refreshLeft: false };
    }

    const newComparisons = comparisonIsNew
      ? comparisonsMade.concat([lastComparison])
      : comparisonsMade;

    if (comparisonIsNew) {
      setComparisonsMade(newComparisons);
    }

    const keptUid = refreshLeft ? uidB : uidA;
    const alreadyCompared = alreadyComparedWith(keptUid, newComparisons);

    let uid = '';
    if (alternatives.length > 0) {
      uid = selectRandomEntity(alternatives, alreadyCompared.concat([keptUid]))
        .entity.uid;
    }

    const nextSuggestion = { uid: uid, refreshLeft: refreshLeft };
    setRefreshLeft(!refreshLeft);

    if (dialogs && newStep != step && newStep in dialogs) {
      if (!isMobileDevice() || dialogs[newStep].mobile) {
        setDialogOpen(true);
      }
    }

    return nextSuggestion;
  };

  const closeDialog = () => {
    setDialogOpen(false);
  };

  const skipTheSeries = () => {
    closeDialog();

    if (skipKey && username) {
      setSkipped(true);
      setSkippedBy(skipKey, username);

      // Only track skip events if the series is the tutorial. Skipping a
      // generic comparison series is not useful for now.
      if (isTutorial) {
        trackEvent(TRACKED_EVENTS.tutorialSkipped, { props: { step: step } });
      }
    }
  };

  /**
   * Build a string representing the URL parameters of a comparison.
   *
   * @param from An array of entities from which `uidA` and `uidB` params will be built.
   * @param comparisons An array of existing comparisons.
   * @param uidA The current value of the `uidA` URL parameter
   * @param uidB The current value of the `uidB` URL parameter
   */
  const genInitialComparisonParams = (
    from: Array<EntityResult>,
    comparisons: Array<string>,
    uidA: string,
    uidB: string
  ): string => {
    if (from.length === 0) {
      return '';
    }

    const newSearchParams = new URLSearchParams();
    let newUidA: string;
    let newUidB: string;

    if (uidA === '') {
      if (uidB === '') {
        newUidA = selectRandomEntity(from, []).entity.uid;
      } else {
        // if not `uidA` and `uidB`, select an uid A that hasn't been compared with B
        newUidA = selectRandomEntity(
          from,
          alreadyComparedWith(uidB, comparisons)
        ).entity.uid;
      }
    } else {
      newUidA = uidA;
    }
    newSearchParams.append(UID_PARAMS.vidA, newUidA);

    if (uidB === '') {
      const comparedWithA = alreadyComparedWith(newUidA, comparisons);
      newUidB = selectRandomEntity(from, comparedWithA.concat([newUidA])).entity
        .uid;
    } else {
      newUidB = uidB;
    }
    newSearchParams.append(UID_PARAMS.vidB, newUidB);

    return newSearchParams.toString();
  };

  if (initialize.current && uidA !== '' && uidB !== '') {
    initialize.current = false;
  }

  if (initialize.current && firstComparisonParams) {
    return (
      <Redirect
        to={{ pathname: location.pathname, search: firstComparisonParams }}
      />
    );
  }

  if (redirectTo && (step >= length || skipped)) {
    const futureSearchParams = new URLSearchParams();

    if (keepUIDsAfterRedirect) {
      if (uidA) {
        futureSearchParams.append('uidA', uidA);
      }
      if (uidB) {
        futureSearchParams.append('uidB', uidB);
      }
    }

    return (
      <Redirect
        to={{ pathname: redirectTo, search: futureSearchParams.toString() }}
      />
    );
  }

  return (
    <>
      {length >= MIN_LENGTH ? (
        <LoaderWrapper isLoading={isLoading}>
          {/*
            Do not display the dialog box while the alternatives array
            is being built, to avoid a blink effect.
          */}
          {!isLoading &&
            dialogs &&
            step in dialogs &&
            (!isMobileDevice() || dialogs[step].mobile) &&
            (!getAlternatives || alternatives.length > 0) && (
              <DialogBox
                title={dialogs[step].title}
                content={dialogs[step].messages.map((message, index) => {
                  return (
                    <Typography key={index} paragraph>
                      {message}
                    </Typography>
                  );
                })}
                open={dialogOpen}
                onClose={closeDialog}
                additionalActionButton={
                  skipKey ? (
                    <Button
                      color="secondary"
                      variant="text"
                      onClick={skipTheSeries}
                    >
                      {skipButtonLabel
                        ? skipButtonLabel
                        : t('comparisonSeries.skipTheSeries')}
                    </Button>
                  ) : (
                    dialogAdditionalActions &&
                    step in dialogAdditionalActions &&
                    dialogAdditionalActions[step].action
                  )
                }
              />
            )}
          {displayStepper && (
            <Container maxWidth="md" sx={{ my: 2 }}>
              <Stepper
                activeStep={step}
                alternativeLabel
                sx={{ marginBottom: 4 }}
              >
                {generateSteps(length)}
              </Stepper>
            </Container>
          )}
          <Comparison afterSubmitCallback={afterSubmitCallback} />
        </LoaderWrapper>
      ) : (
        <Comparison />
      )}
    </>
  );
};

export default ComparisonSeries;
