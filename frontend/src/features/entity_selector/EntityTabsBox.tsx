import React, { useEffect, useState } from 'react';
import { Tabs, Tab, Paper, Alert, Button, Link, Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { RelatedEntityObject } from 'src/utils/types';
import { RowEntityCard } from 'src/components/entity/EntityCard';
import LoaderWrapper from 'src/components/LoaderWrapper';
import EntityTextInput from './EntityTextInput';
import { getWebExtensionUrl } from 'src/utils/extension';

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

const TabError = ({
  messageKey,
  handleClose,
}: {
  messageKey: string;
  handleClose?: () => void;
}) => {
  const { t } = useTranslation();

  const emptyListMessages: { [key: string]: string } = {
    error: 'tabsBox.errorOnLoading',
    'rate-later': 'tabsBox.rateLater',
    'recently-compared': 'tabsBox.compared',
    recommendations: 'tabsBox.recommendations',
    unconnected: 'tabsBox.toConnect',
  };

  return (
    <Box p={2}>
      <Alert severity="info" onClose={handleClose}>
        {t(emptyListMessages[messageKey])}
        {messageKey === 'rate-later' ? (
          <Box display="flex" justifyContent="flex-end">
            <Button
              color="info"
              size="small"
              variant="outlined"
              component={Link}
              href={getWebExtensionUrl()}
              target="_blank"
            >
              {t('videos.dialogs.tutorial.installTheExtension')}
            </Button>
          </Box>
        ) : undefined}
      </Alert>
    </Box>
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
  displayDescription = false,
}: Props) => {
  const [tabValue, setTabValue] = useState(tabs[0]?.name);
  const [status, setStatus] = useState<TabStatus>(TabStatus.Ok);
  const [options, setOptions] = useState<RelatedEntityObject[]>([]);
  const [toggleDescription, setToggleDescription] =
    useState(displayDescription);

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
          '&:first-of-type': {
            marginTop: 1,
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
          setToggleDescription(true);
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
        {toggleDescription && (
          <TabError
            messageKey={tabValue}
            handleClose={() => {
              setToggleDescription(false);
            }}
          />
        )}
        {status === TabStatus.Error ? (
          <TabError messageKey={'error'} />
        ) : (
          options.length > 0 && (
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
          )
        )}
      </LoaderWrapper>
    </Paper>
  );
};

export default EntityTabsBox;
