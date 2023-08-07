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
import { RelatedEntityObject } from 'src/utils/types';
import { RowEntityCard } from 'src/components/entity/EntityCard';
import LoaderWrapper from 'src/components/LoaderWrapper';
import EntityTextInput from './EntityTextInput';
import { getWebExtensionUrl } from 'src/utils/extension';
import { InfoOutlined } from '@mui/icons-material';

interface Props {
  tabs: EntitiesTab[];
  onSelectEntity?: (entityUid: string) => void;
  width?: string | number;
  elevation?: number;
  maxHeight?: string | number;
  withLink?: boolean;
  entityTextInput?: { value: string; onChange: (value: string) => void };
  displayDescription?: boolean;
}

export interface EntitiesTab {
  name: string;
  label: string;
  fetch: () => Promise<RelatedEntityObject[]>;
  disabled?: boolean;
}

export enum TabStatus {
  Ok = 'ok',
  Loading = 'loading',
  Error = 'error',
}

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
  width = 'min(700px, 100vw)',
  elevation = 1,
  maxHeight = '40vh',
  withLink = false,
  entityTextInput,
  displayDescription = true,
}: Props) => {
  const { t } = useTranslation();

  const [tabValue, setTabValue] = useState(tabs[0]?.name);
  const [status, setStatus] = useState<TabStatus>(TabStatus.Ok);
  const [options, setOptions] = useState<RelatedEntityObject[]>([]);
  const [isDescriptionVisible, setIsDescriptionVisible] =
    useState(displayDescription);

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
      {entityTextInput && (
        <EntityTextInput
          value={entityTextInput.value}
          onChange={entityTextInput.onChange}
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
          bgcolor: 'grey.100',
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          '& .MuiTabs-scrollButtons.Mui-disabled': {
            opacity: 0.3,
          },
        }}
      >
        {tabs.map(({ label, name, disabled }) => (
          <Tab key={name} value={name} label={label} disabled={disabled} />
        ))}
      </Tabs>
      <LoaderWrapper
        isLoading={status === TabStatus.Loading}
        sx={{ overflowY: 'scroll' }}
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
          <TabError message={t('tabsBox.errorOnLoading')} />
        ) : options.length > 0 ? (
          <ul>
            {options.map((entity) => (
              <li
                key={entity.uid}
                onClick={onSelectEntity && (() => onSelectEntity(entity.uid))}
              >
                <RowEntityCard entity={entity} withLink={withLink} />
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
