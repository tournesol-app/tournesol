import React, { useEffect, useState } from 'react';

import {
  Tabs,
  Tab,
  Paper,
  Alert,
  Box,
  Typography,
  IconButton,
} from '@mui/material';
import { InfoOutlined } from '@mui/icons-material';

import { Trans, useTranslation } from 'react-i18next';
import { EntityResult } from 'src/utils/types';
import { ExternalLink } from 'src/components';
import { RowEntityCard } from 'src/components/entity/EntityCard';
import { EntityMetadataVariant } from 'src/components/entity/EntityMetadata';
import LoaderWrapper from 'src/components/LoaderWrapper';
import EntitySearchInput from './EntitySearchInput';
import { getWebExtensionUrl } from 'src/utils/extension';

interface Props {
  tabs: EntitiesTab[];
  onSelectEntity?: (entityUid: string) => void;
  width?: string | number;
  elevation?: number;
  maxHeight?: string | number;
  withLink?: boolean;
  entitySearchInput?: boolean;
  displayDescription?: boolean;
  metadataVariant?: EntityMetadataVariant;
}

export interface EntitiesTab {
  name: string;
  label: string;
  fetch: () => Promise<EntityResult[]>;
  disabled?: boolean;
  displayIndividualScores?: boolean;
}

export enum TabStatus {
  Ok = 'ok',
  Loading = 'loading',
  Error = 'error',
}

const getIndividualScores = (res: EntityResult) => {
  if ('individual_rating' in res && res.individual_rating) {
    if ('criteria_scores' in res.individual_rating) {
      return res.individual_rating.criteria_scores;
    }
  }
};

const TabError = ({ message }: { message: string }) => (
  <Typography variant="subtitle1" paragraph m={2} color="neutral.main">
    {message}
  </Typography>
);

const TabInfo = ({
  messageKey,
  handleClose,
}: {
  messageKey: string;
  handleClose?: () => void;
}) => {
  const { t } = useTranslation();

  const descriptionMessages: { [key: string]: React.ReactNode } = {
    'sub-sample': t('tabsBox.subsample'),
    'recently-compared': t('tabsBox.compared'),
    recommendations: t('tabsBox.recommendations'),
    unconnected: t('tabsBox.toConnect'),
    'rate-later': (
      <Trans t={t} i18nKey="tabsBox.rateLater">
        Your rate-later videos appear here. You can add some to your list by
        clicking on the &apos;+&apos; sign on the video cards. You can also add
        them directly from{' '}
        <ExternalLink href={getWebExtensionUrl()} target="_blank">
          the extension
        </ExternalLink>
        .
      </Trans>
    ),
    'good-short-videos': t('tabsBox.goodShortVideos'),
  };

  if (!(messageKey in descriptionMessages)) {
    return null;
  }

  return (
    <Alert severity="info" onClose={handleClose} icon={false}>
      {descriptionMessages[messageKey]}
    </Alert>
  );
};

const EntityTabsBox = ({
  tabs,
  onSelectEntity,
  width = 'min(760px, 100vw)',
  elevation = 1,
  maxHeight = '40vh',
  withLink = false,
  entitySearchInput = false,
  displayDescription = true,
  metadataVariant = 'wrap',
}: Props) => {
  const { t } = useTranslation();

  const [tabValue, setTabValue] = useState(tabs[0]?.name);
  const [status, setStatus] = useState<TabStatus>(TabStatus.Ok);

  const [tabsHidden, setTabsHidden] = useState(false);
  const [tabsDisabled, setTabsDisabled] = useState(false);
  const [searchError, setSearchError] = useState(false);
  const [statusBeforeSearch, setStatusBeforeSearch] = useState<TabStatus>(
    TabStatus.Ok
  );

  const [options, setOptions] = useState<EntityResult[]>([]);
  const [isDescriptionVisible, setIsDescriptionVisible] =
    useState(displayDescription);
  const [displayIndividualScores, setDisplayIndividualScores] = useState(
    tabs[0]?.displayIndividualScores
  );

  const canCloseDescription = !displayDescription;

  const handleToggleDescription = () => {
    setIsDescriptionVisible(!isDescriptionVisible);
  };

  useEffect(() => {
    const tab = tabs.find((t) => t.name === tabValue);
    if (!tab) {
      return;
    }

    let aborted = false;
    const loadTab = async () => {
      setStatus(TabStatus.Loading);
      try {
        const results = await tab.fetch();
        if (!aborted) {
          setOptions(results);
          setStatus(TabStatus.Ok);
        }
      } catch {
        if (!aborted) {
          setOptions([]);
          setStatus(TabStatus.Error);
        }
      }

      setDisplayIndividualScores(tab?.displayIndividualScores ?? false);
    };

    loadTab();
    return () => {
      aborted = true;
    };
  }, [tabs, tabValue]);

  const onSearchStart = () => {
    if (!searchError) {
      setStatusBeforeSearch(status);
    }
    setTabsDisabled(true);
    setStatus(TabStatus.Loading);
  };

  const onSearchError = () => {
    setSearchError(true);
  };

  const onSearchClose = () => {
    setTabsHidden(false);
    setTabsDisabled(false);
    setSearchError(false);
    setStatus(statusBeforeSearch);
  };

  const onSearchResults = () => {
    setTabsHidden(true);
    setStatus(statusBeforeSearch);
  };

  return (
    <Paper
      elevation={elevation}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        ul: {
          listStyleType: 'none',
          p: 0,
          m: 0,
          maxHeight,
          '.MuiModal-root &': {
            maxHeight: 'none',
          },
        },
        li: {
          cursor: onSelectEntity && 'pointer',
          '&:hover': {
            bgcolor: 'grey.100',
          },
        },
        width: width,
        bgcolor: 'white',
        overflow: 'hidden',
        flexGrow: 1,
      }}
    >
      {entitySearchInput && (
        <EntitySearchInput
          onClose={onSearchClose}
          onSearch={onSearchStart}
          onError={onSearchError}
          onResults={onSearchResults}
          onResultSelect={onSelectEntity}
        />
      )}

      <Tabs
        textColor="secondary"
        indicatorColor="secondary"
        value={tabValue}
        onChange={(e, value) => {
          handleToggleDescription;
          setTabValue(value);
        }}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          display: tabsHidden ? 'none' : 'inital',
          bgcolor: 'grey.100',
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          '& .MuiTabs-scrollButtons.Mui-disabled': {
            opacity: 0.3,
          },
        }}
      >
        {tabs.map(({ label, name, disabled }) => (
          <Tab
            key={name}
            value={name}
            label={label}
            disabled={tabsDisabled || disabled}
          />
        ))}
      </Tabs>
      <LoaderWrapper
        circularProgress={!searchError && !tabsHidden}
        isLoading={status === TabStatus.Loading}
        sx={{ display: tabsHidden ? 'none' : 'initial', overflowY: 'auto' }}
      >
        {isDescriptionVisible ? (
          <TabInfo
            messageKey={tabValue}
            handleClose={
              canCloseDescription
                ? () => {
                    setIsDescriptionVisible(false);
                  }
                : undefined
            }
          />
        ) : (
          <Box display="flex" justifyContent="flex-end">
            <IconButton onClick={handleToggleDescription} color="info">
              <InfoOutlined />
            </IconButton>
          </Box>
        )}
        {status === TabStatus.Error ? (
          <TabError message={t('entitySelector.errorOnLoading')} />
        ) : options.length > 0 ? (
          <ul>
            {options.map((res) => (
              <li
                key={res.entity.uid}
                onClick={
                  onSelectEntity && (() => onSelectEntity(res.entity.uid))
                }
              >
                <RowEntityCard
                  result={res}
                  withLink={withLink}
                  metadataVariant={metadataVariant}
                  individualScores={
                    displayIndividualScores
                      ? getIndividualScores(res)
                      : undefined
                  }
                />
              </li>
            ))}
          </ul>
        ) : (
          <TabError message={t('tabsBox.emptyList')} />
        )}
      </LoaderWrapper>
    </Paper>
  );
};

export default EntityTabsBox;
