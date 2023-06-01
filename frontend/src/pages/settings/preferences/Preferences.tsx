import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';

import { Grid } from '@mui/material';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  SettingsSection,
} from 'src/components';
import { useNotifications } from 'src/hooks';
import VideosPollUserSettingsForm from 'src/features/settings/preferences/VideosPollUserSettingsForm';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import { replaceSettings } from 'src/features/settings/userSettingsSlice';
import {
  mainSectionBreakpoints,
  settingsMenuBreakpoints,
} from 'src/pages/settings/layout';
import { UsersService } from 'src/services/openapi';

const PreferencePage = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const { contactAdministrator } = useNotifications();

  const [loading, setLoading] = useState(true);

  /**
   * In order to display the up-to-date user's preferences in all child
   * components, we retrieve the user's settings from the API and refresh the
   * Redux store.
   */
  useEffect(() => {
    async function retrieveProfile() {
      const response = await UsersService.usersMeSettingsRetrieve().catch(
        () => {
          contactAdministrator(
            'error',
            t('preferences.errorOccurredWhileRetrievingPreferences')
          );
        }
      );

      if (response) {
        dispatch(replaceSettings(response));
      }

      setLoading(false);
    }

    retrieveProfile();
  }, [t, dispatch, contactAdministrator]);

  // subSectionBreakP can be changed independently of mainSectionBp
  const subSectionBreakpoints = mainSectionBreakpoints;
  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('preferences.preferences')}`}
      />
      <ContentBox maxWidth="xl">
        <Grid container spacing={4}>
          <Grid item {...settingsMenuBreakpoints}>
            <SettingsMenu />
          </Grid>
          <Grid
            container
            item
            direction="column"
            alignItems="stretch"
            {...mainSectionBreakpoints}
          >
            <SettingsSection
              title={`${t('preferences.preferencesRegarding')} ${t(
                'poll.videos'
              )}`}
              {...subSectionBreakpoints}
            >
              <LoaderWrapper isLoading={loading}>
                <VideosPollUserSettingsForm />
              </LoaderWrapper>
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
};

export default PreferencePage;
