import React, { useEffect, useCallback, useState } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { useSelector } from 'react-redux';

import { Box, Divider, Grid, IconButton, Paper, Stack } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';
import InfoIcon from '@mui/icons-material/Info';

import {
  ContentBox,
  ContentHeader,
  ExternalLink,
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

import { selectSettings } from 'src/features/settings/userSettingsSlice';
import { DEFAULT_RATE_LATER_AUTO_REMOVAL } from 'src/utils/constants';
import PreferencesIconButtonLink from 'src/components/buttons/PreferencesIconButtonLink';
import DialogBox from 'src/components/DialogBox';
import { PollUserSettingsKeys } from 'src/utils/types';

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

const WhereToFindVideosDialog = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const { t } = useTranslation();

  const dialog = {
    title: t('ratelater.findVideosTitle'),
    content: (
      <>
        <Typography paragraph>
          <Trans t={t} i18nKey="ratelater.findVideosYoutube">
            You can search them in your{' '}
            <ExternalLink href="https://www.youtube.com/feed/history">
              YouTube history page
            </ExternalLink>{' '}
            , or your{' '}
            <ExternalLink href="https://www.youtube.com/playlist?list=LL">
              liked video playlist
            </ExternalLink>
            .
          </Trans>
        </Typography>
        <Typography paragraph>{t('ratelater.findVideosTournesol')}</Typography>
      </>
    ),
  };

  return (
    <DialogBox
      open={open}
      onClose={onClose}
      title={dialog.title}
      content={dialog.content}
    />
  );
};

const RateLaterPage = () => {
  const classes = useStyles();

  const { t } = useTranslation();
  const { displayErrorsFrom, showSuccessAlert } = useNotifications();

  const { name: pollName } = useCurrentPoll();
  const settings =
    useSelector(selectSettings).settings?.[pollName as PollUserSettingsKeys];

  const [isLoading, setIsLoading] = React.useState(true);

  const [rateLaterList, setRateLaterList] = React.useState<RateLater[]>([]);
  const [entityCount, setEntityCount] = React.useState<number | null>(null);

  const videoListTopRef = React.useRef<HTMLDivElement>(null);
  const [offset, setOffset] = React.useState(0);
  const limit = 20;

  const rateLaterSetting =
    settings?.rate_later__auto_remove ?? DEFAULT_RATE_LATER_AUTO_REMOVAL;

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

  const rateLaterPageActions = [
    CompareNowAction,
    RemoveFromRateLater(loadList),
  ];

  const [where2findVideosOpen, setWhere2findVideosOpen] = useState(false);

  const onInfoClick = useCallback(() => {
    setWhere2findVideosOpen(true);
  }, []);

  const onWhereToFindVideosDialogClose = useCallback(() => {
    setWhere2findVideosOpen(false);
  }, []);

  return (
    <>
      <ContentHeader title={t('myRateLaterListPage.title')} />
      <ContentBox maxWidth="lg">
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
            <Paper sx={{ p: 2, display: 'flex', width: '100%' }}>
              <Box
                display="flex"
                flexDirection="column"
                alignItems="stretch"
                justifyContent="space-around"
              >
                <Stack direction="row" alignItems="center" mb={2} spacing={1}>
                  <Typography variant="h6">
                    {t('ratelater.addVideosToRateLaterList')}
                  </Typography>
                  <IconButton onClick={onInfoClick}>
                    <InfoIcon fontSize="small" />
                  </IconButton>
                  <WhereToFindVideosDialog
                    open={where2findVideosOpen}
                    onClose={onWhereToFindVideosDialogClose}
                  />
                </Stack>
                <Box pt={2}>
                  <RateLaterAddForm addVideo={addToRateLater} />
                </Box>
              </Box>
            </Paper>
          </Grid>

          <Grid item sm={6} display="flex" width="100%">
            <Paper sx={{ p: 2, width: '100%' }}>
              <Typography paragraph>
                {t('ratelater.addVideosToYourListToCompareThemLater')}
              </Typography>
              <Divider />
              <ul>
                <li>
                  <Trans t={t} i18nKey="ratelater.useOurBrowserExtension">
                    Use our{' '}
                    <ExternalLink
                      href={
                        getWebExtensionUrl() ?? getWebExtensionUrl('chrome')
                      }
                    >
                      browser extension
                    </ExternalLink>{' '}
                    to effortlessly add videos directly from YouTube.
                  </Trans>
                </li>
                <li>
                  <Typography paragraph mt={2} mb={0}>
                    {t('ratelater.orCopyPasteVideoUrlHere')}
                  </Typography>
                </li>
              </ul>
            </Paper>
          </Grid>
        </Grid>

        <div className={classes.rateLaterContent} ref={videoListTopRef}>
          {entityCount !== null && (
            <Typography
              variant="subtitle1"
              m={2}
              textAlign="center"
              lineHeight="1.5em"
              sx={{
                '& strong': {
                  color: 'secondary.main',
                  fontSize: '1.4em',
                },
              }}
            >
              <Trans
                t={t}
                i18nKey="ratelater.listHasNbVideos"
                count={entityCount}
              >
                Your rate-later list contains <strong>{{ entityCount }}</strong>{' '}
                video(s). They will be automatically removed after{' '}
                <strong>{{ rateLaterSetting }}</strong> comparison(s).
              </Trans>{' '}
            </Typography>
          )}

          <Box width="100%">
            <LoaderWrapper isLoading={isLoading}>
              <EntityList
                entities={rateLaterList}
                actions={rateLaterPageActions}
                actionsIfUnavailable={[RemoveFromRateLater(loadList)]}
                cardProps={{ showRatingControl: true }}
                displayContextAlert={true}
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
