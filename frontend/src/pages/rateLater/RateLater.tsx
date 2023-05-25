import React, { useEffect, useCallback, useMemo, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Box, Grid, IconButton, Paper, Stack } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';
import InfoIcon from '@mui/icons-material/Info';

import {
  ContentBox,
  ContentHeader,
  LoaderWrapper,
  Pagination,
} from 'src/components';
import EntityList from 'src/features/entities/EntityList';
import RateLaterAddForm from 'src/features/rateLater/RateLaterAddForm';
import { useCurrentPoll, useNotifications } from 'src/hooks';
import { ApiError, RateLater, UsersService } from 'src/services/openapi';
import { CompareNowAction, RemoveFromRateLater } from 'src/utils/action';
import { addToRateLaterList } from 'src/utils/api/rateLaters';
import { UID_YT_NAMESPACE, YOUTUBE_POLL_NAME } from 'src/utils/constants';
import { getWebExtensionUrl } from 'src/utils/extension';
import { useSelector } from 'react-redux';
import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { DEFAULT_RATE_LATER_AUTO_REMOVAL } from 'src/utils/constants';
import PreferencesIconButtonLink from 'src/components/buttons/PreferencesIconButtonLink';
import DialogNodeBox from 'src/components/DialogBoxGeneric';

const useStyles = makeStyles({
  rateLaterContent: {
    flexDirection: 'column',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '20px',
  },
});

const RateLaterPage = () => {
  const classes = useStyles();

  const { t } = useTranslation();
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();
  const { name: pollName } = useCurrentPoll();

  const [isLoading, setIsLoading] = React.useState(true);

  const [rateLaterList, setRateLaterList] = React.useState<RateLater[]>([]);
  const [entityCount, setEntityCount] = React.useState<number | null>(null);

  const videoListTopRef = React.useRef<HTMLDivElement>(null);
  const [offset, setOffset] = React.useState(0);
  const limit = 20;
  const settings = useSelector(selectSettings).settings?.[YOUTUBE_POLL_NAME];
  const rateLaterSetting = settings?.rate_later__auto_remove
    ? settings.rate_later__auto_remove
    : DEFAULT_RATE_LATER_AUTO_REMOVAL;

  const loadList = useCallback(async () => {
    setIsLoading(true);
    let rateLaterResponse;
    try {
      rateLaterResponse = await UsersService.usersMeRateLaterList({
        pollName,
        limit,
        offset,
      });
    } catch (err) {
      console.error('Fetch rater list failed.', err);
      setIsLoading(false);
      return;
    }
    if (rateLaterResponse.count != null) {
      setEntityCount(rateLaterResponse.count);
    }
    if (rateLaterResponse.results != null) {
      setRateLaterList(rateLaterResponse.results);
    }
    setIsLoading(false);
  }, [offset, pollName, setEntityCount, setRateLaterList]);

  const addToRateLater = async (id: string): Promise<boolean> => {
    let uidNamespace = '';
    // TODO: we should be able to get the UID namespace from the polls'
    // configuration to avoid writing these kind of if statement everywhere.
    if (pollName === YOUTUBE_POLL_NAME) {
      uidNamespace = UID_YT_NAMESPACE;
    }

    const response = await addToRateLaterList(
      pollName,
      uidNamespace + id
    ).catch((reason: ApiError) => {
      displayErrorsFrom(reason, t('ratelater.errorOccurredCannotAddVideo'), [
        {
          status: 409,
          variant: 'warning',
          msg: t('ratelater.videoAlreadyInList'),
        },
      ]);
    });
    if (response) {
      showSuccessAlert(t('ratelater.videoAdded'));
      await loadList();
      return true;
    }
    return false;
  };

  const onOffsetChange = (newOffset: number) => {
    setOffset(newOffset);
    videoListTopRef.current?.scrollIntoView();
  };

  useEffect(() => {
    loadList();
  }, [loadList]);

  const entities = rateLaterList.map((r) => r.entity);
  const rateLaterPageActions = [
    CompareNowAction,
    RemoveFromRateLater(loadList),
  ];

  const [descriptionDialogOpen, setDescriptionDialogOpen] = useState(false);

  const handleDescriptionInfoClick = useCallback(() => {
    setDescriptionDialogOpen(true);
  }, []);

  const handleDescriptionDialogClose = useCallback(() => {
    setDescriptionDialogOpen(false);
  }, []);

  const DescriptionDialog = ({
    open,
    onClose,
  }: {
    open: boolean;
    onClose: () => void;
  }) => {
    const { t } = useTranslation();
    const dialog = useMemo(
      () => ({
        title: t('ratelater.findVideosTitle'),
        content: (
          <>
            <Typography paragraph>
              <Trans t={t} i18nKey="ratelater.findVideosYoutube">
                You can search them in your{' '}
                <a href="https://www.youtube.com/feed/history">
                  YouTube history page
                </a>{' '}
                , or your{' '}
                <a href="https://www.youtube.com/playlist?list=LL">
                  liked video playlist
                </a>
                .
              </Trans>
            </Typography>
            <Typography paragraph>
              {t('ratelater.findVideosTournesol')}
            </Typography>
          </>
        ),
      }),
      [t]
    );
    return <DialogNodeBox open={open} onClose={onClose} dialog={dialog} />;
  };

  return (
    <>
      <ContentHeader title={t('myRateLaterListPage.title')} />
      <ContentBox noMinPaddingX maxWidth="lg">
        <Box display={'flex'} justifyContent={'end'} mb={2}>
          <PreferencesIconButtonLink hash="#rate_later" />
        </Box>
        <Grid
          container
          direction="row"
          spacing={2}
          justifyContent="space-between"
          alignItems="stretch"
        >
          <Grid item sm={6} display="flex" width="100%">
            <Paper sx={{ p: 2, width: '100%' }}>
              <Stack direction="row" alignItems="center" mb={2}>
                <Typography variant="h6">
                  {t('ratelater.addVideosToRateLaterList')}
                </Typography>
                <IconButton onClick={handleDescriptionInfoClick}>
                  <InfoIcon fontSize="small" />
                </IconButton>
                <DescriptionDialog
                  open={descriptionDialogOpen}
                  onClose={handleDescriptionDialogClose}
                />
              </Stack>
              <Box pt={2}>
                <RateLaterAddForm addVideo={addToRateLater} />
              </Box>
            </Paper>
          </Grid>
          <Grid item sm={6} display="flex" width="100%">
            <Paper sx={{ p: 2, width: '100%' }}>
              <Typography paragraph>
                {t('ratelater.addVideosToYourListToCompareThemLater')}
              </Typography>
              <Trans t={t} i18nKey="ratelater.useOurBrowserExtension">
                Use our{' '}
                <a href={getWebExtensionUrl() ?? getWebExtensionUrl('chrome')}>
                  browser extension
                </a>{' '}
                to effortlessly add videos directly from YouTube.
              </Trans>
              <Typography paragraph mt={2} mb={0}>
                {t('ratelater.orCopyPasteVideoUrlHere')}
              </Typography>
            </Paper>
            {/* <PreferencesIconButtonLink hash='#rate_later'/> */}
          </Grid>
        </Grid>

        <div className={classes.rateLaterContent} ref={videoListTopRef}>
          {entityCount !== null && (
            <Typography variant="subtitle1">
              <Trans
                t={t}
                i18nKey="ratelater.listHasNbVideos"
                count={entityCount}
              >
                Your rate-later list now has <strong>{{ entityCount }}</strong>{' '}
                video(s). They are automatically removed after{' '}
                <strong>{{ rateLaterSetting }}</strong> comparison(s).
              </Trans>{' '}
              {/* <PreferencesIconButtonLink hash='#rate_later'/> */}
            </Typography>
          )}

          <Box width="100%" textAlign="center">
            <LoaderWrapper isLoading={isLoading}>
              <EntityList
                entities={entities}
                actions={rateLaterPageActions}
                actionsIfUnavailable={[RemoveFromRateLater(loadList)]}
              />
            </LoaderWrapper>
          </Box>
          {!!entityCount && entityCount > limit && (
            <Pagination
              offset={offset}
              count={entityCount}
              onOffsetChange={onOffsetChange}
              limit={limit}
            />
          )}
        </div>
      </ContentBox>
    </>
  );
};

export default RateLaterPage;
