import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch } from 'react-redux';
import { useLocation } from 'react-router-dom';

import { Grid2 } from '@mui/material';

import { ContentBox, ContentHeader, LoaderWrapper } from 'src/components';
import { useNotifications } from 'src/hooks';
import SettingsMenu from 'src/features/settings/SettingsMenu';
import TournesolUserSettingsForm from 'src/features/settings/preferences/TournesolUserSettingsForm';
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

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const isEmbedded = Boolean(searchParams.get('embed'));

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <ContentHeader
        title={`${t('settings.title')} > ${t('preferences.preferences')}`}
      />
      <ContentBox maxWidth="xl">
        <Grid2
          container
          spacing={4}
          sx={[
            isEmbedded
              ? {
                  justifyContent: 'center',
                }
              : {
                  justifyContent: 'normal',
                },
          ]}
        >
          {!isEmbedded && (
            <Grid2 size={settingsMenuBreakpoints}>
              <SettingsMenu />
            </Grid2>
          )}
          <Grid2 size={mainSectionBreakpoints}>
            <LoaderWrapper isLoading={loading}>
              <TournesolUserSettingsForm />
            </LoaderWrapper>
          </Grid2>
        </Grid2>
      </ContentBox>
    </>
  );
};

export default PreferencePage;
