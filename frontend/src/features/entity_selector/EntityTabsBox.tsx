import React, { useEffect, useState } from 'react';
import {
  Tabs,
  Tab,
  Paper,
  Alert,
  Link,
  Box,
  Typography,
  IconButton,
} from '@mui/material';
import { Trans, useTranslation } from 'react-i18next';
import { EntityResult } from 'src/utils/types';
import { RowEntityCard } from 'src/components/entity/EntityCard';
import LoaderWrapper from 'src/components/LoaderWrapper';
import EntitySearchInput from './EntityTextInput';
import { getWebExtensionUrl } from 'src/utils/extension';
import { InfoOutlined } from '@mui/icons-material';

interface Props {
  tabs: EntitiesTab[];
  onSelectEntity?: (entityUid: string) => void;
  width?: string | number;
  elevation?: number;
  maxHeight?: string | number;
  withLink?: boolean;
  entitySearchInput?: boolean;
  displayDescription?: boolean;
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
        <Link
          href={getWebExtensionUrl()}
          target="_blank"
          rel="noopener"
          sx={{
            color: 'revert',
            textDecoration: 'revert',
          }}
        >
          the extension
        </Link>
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
}: Props) => {
  const { t } = useTranslation();

  const [tabValue, setTabValue] = useState(tabs[0]?.name);
  const [uiDisabled, setUiDisabled] = useState(false);
  const [status, setStatus] = useState<TabStatus>(TabStatus.Ok);
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

  return (
    <Paper
      elevation={elevation}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '160px',
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
          cursor: onSelectEntity && !uiDisabled ? 'pointer' : 'default',
          '&:hover': {
            bgcolor: uiDisabled ? 'inherit' : 'grey.100',
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
          onClear={() => setUiDisabled(false)}
          onResults={() => setUiDisabled(true)}
          onResultSelect={onSelectEntity}
        />
      )}
      <Box sx={{ filter: uiDisabled ? 'blur(3px)' : 'none' }}>
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
              disabled={uiDisabled ? true : disabled}
            />
          ))}
        </Tabs>
        <LoaderWrapper
          isLoading={status === TabStatus.Loading}
          sx={{ overflowY: uiDisabled ? 'hidden' : 'auto' }}
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
              <IconButton
                onClick={handleToggleDescription}
                color="info"
                disabled={uiDisabled}
              >
                <InfoOutlined />
              </IconButton>
            </Box>
          )}
          {status === TabStatus.Error ? (
            <TabError message={t('tabsBox.errorOnLoading')} />
          ) : options.length > 0 ? (
            <ul>
              {options.map((res) => (
                <li
                  key={res.entity.uid}
                  onClick={
                    uiDisabled
                      ? undefined
                      : onSelectEntity && (() => onSelectEntity(res.entity.uid))
                  }
                >
                  <RowEntityCard
                    result={res}
                    withLink={withLink}
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
      </Box>
    </Paper>
  );
};

export default EntityTabsBox;
