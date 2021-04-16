import React from 'react';

import { useParams } from 'react-router-dom';
import ReportIcon from '@material-ui/icons/Report';
import EditIcon from '@material-ui/icons/Edit';
import IconButton from '@material-ui/core/IconButton';
import PersonIcon from '@material-ui/icons/Person';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import Grid from '@material-ui/core/Grid';
import { green, orange } from '@material-ui/core/colors';
import { makeStyles } from '@material-ui/core/styles';
import UserInterface from './UserInterface';
import { TournesolAPI } from '../api';
import PersonalInfo from './PersonalInfo';

const useStyles = makeStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.background.paper,
    width: 500,
    position: 'relative',
    minHeight: 200,
  },
  stats: {
    width: '150px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    fontSize: '150%',
  },
  fabEdit: {
    color: theme.palette.common.white,

    width: '80px',
    height: '80px',

    backgroundColor: green[500],
    '&:hover': {
      backgroundColor: green[600],
    },
  },
  fabDownload: {
    color: theme.palette.common.white,

    width: '80px',
    height: '80px',

    backgroundColor: orange[500],
    '&:hover': {
      backgroundColor: orange[600],
    },
  },
}));

const userProfileLinks = [
  { name: 'Twitter', key: 'twitter', icon: '/static/icons/twitter.png' },
  { name: 'LinkedIn', key: 'linkedin', icon: '/static/icons/linkedin.png' },
  { name: 'Website', key: 'website', icon: '/static/icons/website.png' },
  { name: 'YouTube', key: 'youtube', icon: '/static/icons/youtube.png' },
  {
    name: 'Google Scholar',
    key: 'google_scholar',
    icon: '/static/icons/scholar.png',
  },
  { name: 'ORCID', key: 'orcid', icon: '/static/icons/orcid.png' },
  {
    name: 'Researchgate',
    key: 'researchgate',
    icon: '/static/icons/researchgate.png',
  },
];

export default () => {
  const classes = useStyles();
  const { userId } = useParams();
  const [data, setData] = React.useState(
    TournesolAPI.UserInformationPublicSerializerV2.constructFromObject({}),
  );
  const [requested, setRequested] = React.useState(false);
  const [error, setError] = React.useState(false);
  const [requestedUsername, setRequestedUsername] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [formOpen, setFormOpen] = React.useState(false);

  // user was loaded, but a new user is requested now...
  if (requestedUsername && requestedUsername !== userId) {
    setRequestedUsername(null);
    setRequested(false);
  }

  const openForm = () => {
    setFormOpen(true);
  };

  const closeForm = () => {
    setFormOpen(false);
    setRequested(false);
  };

  const descriptionElementRef = React.useRef(null);
  React.useEffect(() => {
    if (formOpen) {
      const { current: descriptionElement } = descriptionElementRef;
      if (descriptionElement !== null) {
        descriptionElement.focus();
      }
    }
  }, [formOpen]);

  const needUserInterface = data && (window.username === data.username || data.n_public_videos > 0);

  if (!requested) {
    setLoading(true);
    setRequestedUsername(userId);
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationList({ userUsername: userId }, (err, dataNew) => {
      if (err || dataNew.count !== 1) {
        setError(true);
        setData(null);
        setLoading(false);
      } else {
        setError(false);
        const [dataItem] = dataNew.results;
        setData(dataItem);
        setLoading(false);
        window.data = dataItem;
      }
      return null;
    });
    setRequested(true);
  }

  return (
    <div id="userPage">
      {loading ? <div id="id_user_page_loading" /> : <div id="id_user_page_loaded" />}
      {!loading && data === null && (
        <p>
          This person does not exist, or does not share their profile publicly
        </p>
      )}
      {!loading && data !== null && (
        <>
          {loading && <p>Loading</p>}

          {!loading && error && (
          <p>
            This person does not exist or prefers to keep their information
            private.
          </p>
          )}

          {!loading && !error && data && (
          <>
            <Grid
              container
              spacing={3}
              style={{ paddingBottom: '5px' }}
            >
              <Grid item xs={9}>

                <h1>
                  <span id="id_first_last_name_certified_user">
                    {data.first_name} {data.last_name}{' '}
                    {data.is_certified && (
                    <img
                      style={{ width: '1em', marginTop: '0.3em' }}
                      src="/static/ts_certified_person.png"
                      alt="tournesol"
                    />
                    )}
                  </span>
                  {data.is_certified && data.certified_email_domain !== null && (
                  <span id="id_certified_domain_name">
                    {data.certified_email_domain}
                  </span>
                  )}
                  <IconButton
                    aria-label="load"
                    onClick={() => {
                      // TODO: API call to allow reporting users
                      alert('Reporting is not yet implemented');
                    }}
                    style={{ float: 'right' }}
                  >
                    <ReportIcon />
                  </IconButton>
                </h1>

                <h3>
                  <span>
                    <PersonIcon />
                    {userId}
                  </span>
                </h3>
                <h2 id="id_title_user">{data.title}</h2>
                <p id="id_bio_user">{data.bio}</p>

                <Grid
                  container
                  direction="row"
                  spacing={3}
                  justify="flex-start"
                  alignItems="center"
                  style={{ paddingBottom: '10px', paddingTop: '5px' }}
                >
                  {userProfileLinks.map(({ key, name, icon }) => {
                    if (
                      data[key] !== undefined &&
                                          data[key] !== null &&
                                          data[key].length >= 1
                    ) {
                      return (
                        <Grid item>
                          <a
                            id={`id_${key}_user`}
                            href={data[key]}
                            target="_blank"
                            rel="noreferrer"
                          >
                            <img
                              src={icon}
                              alt={name}
                              style={{ maxHeight: '30px' }}
                            />
                          </a>
                        </Grid>
                      );
                    }
                    return null;
                  })}
                </Grid>

                {data.degrees && data.degrees.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'row' }}>
                  <b>Degrees: </b>
                  <ul style={{ margin: 0, listStyleType: 'none' }}>
                    {data.degrees &&
                                          data.degrees.map(({ level, domain, institution }) => (
                                            <li
                                              key={level + domain + institution}
                                              className="class_degree_user"
                                            >
                                              {level}, {domain}, {institution}
                                            </li>
                                          ))}
                  </ul>
                </div>
                )}

                {data.expertises && data.expertises.length > 0 && (
                <p>
                  <b>Expertise: </b>
                  {data.expertises &&
                                          data.expertises.map((e, i) => (
                                            <span key={e.name} className="class_expertise_user">
                                              {e.name}
                                              {i === data.expertises.length - 1 || ', '}
                                            </span>
                                          ))}
                </p>
                )}

                {data.expertise_keywords && data.expertise_keywords.length > 0 && (
                <p>
                  <b>Keywords: </b>
                  {data.expertise_keywords &&
                                          data.expertise_keywords.map((k, i) => (
                                            <span
                                              key={k.name}
                                              className="class_expertise_keyword_user"
                                            >
                                              {k.name}
                                              {i === data.expertise_keywords.length - 1 || ', '}
                                            </span>
                                          ))}
                </p>
                )}
              </Grid>

              <Grid item xs={3}>

                <Grid
                  container
                  direction="column"
                  justify="space-evenly"
                  alignItems="center"
                >

                  {data.avatar && (
                  <Grid item>
                    <a href={data.avatar}>
                      <img
                        id="id_profile_user"
                        src={data.avatar}
                        alt="user portrait"
                        style={{ margin: '8px', maxWidth: '90%' }}
                      />
                    </a>
                  </Grid>
                  )}

                  <Grid item>

                    {window.username === data.username && (
                    <IconButton
                      aria-label="download"
                      className={classes.fabDownload}
                      onClick={() => null}
                      href="/my_tournesol_data.zip"
                      id="id_my_data_download"
                    >
                      <Tooltip
                        style={{ width: '100%', height: '100%' }}
                        title="Download my Tournesol data"
                        aria-label="add"
                      >
                        <div style={{ width: '100%', height: '100%', textAlign: 'center' }}>
                          <FontAwesomeIcon icon={['fas', 'download']} />
                        </div>
                      </Tooltip>
                    </IconButton>
                    )}

                                &nbsp;&nbsp;

                    {window.username === data.username && (
                    <IconButton
                      aria-label="edit"
                      className={classes.fabEdit}
                      onClick={openForm}
                      id="edit_userprofile_button_id"
                    >
                      <Tooltip
                        title="Edit my data"
                        aria-label="add"
                      >
                        <EditIcon />
                      </Tooltip>
                    </IconButton>
                    )}

                  </Grid>
                </Grid>

              </Grid>

            </Grid>

            <div
              style={{
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'center',
              }}
            >
              <div className={classes.stats}>
                <h1>{data.n_ratings}</h1>
                <span>ratings</span>
              </div>
              <div className={classes.stats}>
                <h1>{data.n_videos}</h1>
                <span>videos</span>
              </div>
              <div className={classes.stats}>
                <h1>{data.n_comments}</h1>
                <span>comments</span>
              </div>
              <div className={classes.stats}>
                <h1>{data.n_likes}</h1>
                <span>likes</span>
              </div>
              <div className={classes.stats}>
                <h1>{data.n_thanks_received}</h1>
                <span>thank yous</span>
              </div>
              <div className={classes.stats}>
                <h1>{data.n_mentions}</h1>
                <span>
                  {window.username === data.username ? (
                    <a id="id_mentions" href="/comment_mentions">
                      mentions
                    </a>
                  ) : (
                    'mentions'
                  )}
                </span>
              </div>
            </div>

            {window.username === data.username && (
            <Dialog
              maxWidth="md"
              open={formOpen}
              onClose={closeForm}
              scroll="body"
              aria-describedby="scroll-dialog-description"
            >
              <DialogContent>
                <DialogContentText
                  id="scroll-dialog-description"
                  ref={descriptionElementRef}
                  tabIndex={-1}
                >
                  <PersonalInfo />
                </DialogContentText>
              </DialogContent>
              <DialogActions>
                <Button onClick={closeForm} color="primary">
                  Close
                </Button>
              </DialogActions>
            </Dialog>
            )}
          </>
          )}
        </>
      )}

      {needUserInterface === true && (
        <span>
          <div
            style={{
              display: 'flex',
              flexDirection: 'row',
              justifyContent: 'center',
            }}
          >
            <h2>Search with {data.username}'s public recommendations!</h2>
          </div>
          <UserInterface searchModelOverride={data.username} showAllMyVideosInitial="true" />
        </span>
      )}

      {needUserInterface === false && !loading && data !== null && (
        <p>This contributor did not rate any videos publicly.</p>
      )}

    </div>
  );
};
