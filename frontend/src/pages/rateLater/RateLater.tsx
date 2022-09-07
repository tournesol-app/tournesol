import React, { useEffect, useCallback } from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Card, Box, CardContent, CardActions } from '@mui/material';
import makeStyles from '@mui/styles/makeStyles';
import Typography from '@mui/material/Typography';

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

const useStyles = makeStyles({
  rateLaterContent: {
    flexDirection: 'column',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '20px',
  },
  stickyPagination: {
    position: 'sticky',
    top: 4,
    zIndex: 1,
    padding: '6px',
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

  return (
    <>
      <ContentHeader title={t('myRateLaterListPage.title')} />
      <ContentBox noMinPaddingX maxWidth="md">
        <Card
          elevation={4}
          sx={{
            textAlign: 'center',
            display: 'flex',
            alignItems: 'center',
            flexDirection: 'column',
            fontSize: '14px',
          }}
        >
          <CardContent>
            <Typography variant="h6">
              {t('ratelater.addVideosToRateLaterList')}
            </Typography>
            <Trans t={t} i18nKey="ratelater.rateLaterFormIntroduction">
              Copy-paste the id or the URL of a favorite video of yours.
              <br />
              You can search them in your{' '}
              <a href="https://www.youtube.com/feed/history">
                YouTube history page
              </a>
              , or your{' '}
              <a href="https://www.youtube.com/playlist?list=LL">
                liked video playlist
              </a>
              .<br />
              Our{' '}
              <a href={getWebExtensionUrl() ?? getWebExtensionUrl('chrome')}>
                browser extension
              </a>{' '}
              can also help you import videos effortlessly.
              <br />
              You will then be able to rate the videos you imported.
            </Trans>
          </CardContent>
          <CardActions>
            <RateLaterAddForm addVideo={addToRateLater} />
          </CardActions>
        </Card>

        <div className={classes.rateLaterContent} ref={videoListTopRef}>
          {entityCount !== null && (
            <Typography variant="subtitle1">
              <Trans
                t={t}
                i18nKey="ratelater.listHasNbVideos"
                count={entityCount}
              >
                Your rate-later list now has <strong>{{ entityCount }}</strong>{' '}
                video(s).
              </Trans>
            </Typography>
          )}

          <Box width="100%" textAlign="center">
            <LoaderWrapper isLoading={isLoading}>
              <EntityList entities={entities} actions={rateLaterPageActions} />
            </LoaderWrapper>
          </Box>
          {!!entityCount && (
            <div className={classes.stickyPagination}>
              <Pagination
                offset={offset}
                count={entityCount}
                onOffsetChange={onOffsetChange}
                limit={limit}
              />
            </div>
          )}
        </div>
      </ContentBox>
    </>
  );
};

export default RateLaterPage;
