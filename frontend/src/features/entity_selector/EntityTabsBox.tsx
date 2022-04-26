import React, { useEffect, useState } from 'react';
import { Tabs, Tab, Paper, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { RelatedEntityObject } from 'src/utils/types';
import { VideoCardFromId } from '../videos/VideoCard';

interface Props {
  tabs: EntitiesTab[];
  onSelectEntity: (entityUid: string) => void;
}

export interface EntitiesTab {
  name: string;
  label: string;
  fetch: () => Promise<RelatedEntityObject[]>;
  disabled?: boolean;
}

const EntityTabsBox = ({ tabs, onSelectEntity }: Props) => {
  const { t } = useTranslation();
  const [tabValue, setTabValue] = useState(tabs[0]?.name);
  const [options, setOptions] = useState<RelatedEntityObject[]>([]);

  useEffect(() => {
    const tab = tabs.find((t) => t.name === tabValue);
    if (!tab) {
      return;
    }
    tab.fetch().then(setOptions);
  }, [tabs, tabValue]);

  return (
    <Paper
      elevation={10}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        ul: {
          flexGrow: 1,
          listStyleType: 'none',
          p: 0,
          m: 0,
          overflowY: 'scroll',
          maxHeight: '40vh',
          '.MuiModal-root &': {
            maxHeight: 'none',
          },
        },
        li: {
          cursor: 'pointer',
          '&:hover': {
            bgcolor: 'grey.50',
          },
          '&:first-of-type': {
            marginTop: 1,
          },
        },
        width: 'min(700px, 100vw)',
        bgcolor: 'white',
        overflow: 'hidden',
        flexGrow: 1,
      }}
    >
      <Tabs
        textColor="secondary"
        indicatorColor="secondary"
        value={tabValue}
        onChange={(e, value) => setTabValue(value)}
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
      {options.length > 0 ? (
        <ul>
          {options.map((entity) => (
            <li
              key={entity.metadata.video_id}
              onClick={() => onSelectEntity(entity.uid)}
            >
              <VideoCardFromId
                videoId={entity.metadata.video_id}
                variant="row"
              />
            </li>
          ))}
        </ul>
      ) : (
        <Typography variant="subtitle1" paragraph m={2} color="neutral.main">
          {t('tabsBox.emptyList')}
        </Typography>
      )}
    </Paper>
  );
};

export default EntityTabsBox;
