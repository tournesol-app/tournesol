import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { useTranslation } from 'react-i18next';

import { Grid } from '@mui/material';

import { ContentBox, ContentHeader, SettingsSection } from 'src/components';
import { useNotifications } from 'src/hooks';
import GenericPollUserSettingsForm from 'src/features/settings/preferences/GenericPollUserSettingsForm';
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
            t('pollUserSettingsForm.errorOccurredWhileRetrievingPreferences')
          );
        }
      );

      if (response) {
        dispatch(replaceSettings(response));
      }
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
              title={t('preferences.preferencesOfThePoll')}
              {...subSectionBreakpoints}
            >
              <GenericPollUserSettingsForm pollName="videos" />
            </SettingsSection>
          </Grid>
        </Grid>
      </ContentBox>
    </>
  );
};

export default PreferencePage;
