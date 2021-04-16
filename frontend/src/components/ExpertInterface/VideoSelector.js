import React from 'react';

import IconButton from '@material-ui/core/IconButton';
import ReplayIcon from '@material-ui/icons/Replay';
import TextField from '@material-ui/core/TextField';
import Tooltip from '@material-ui/core/Tooltip';
import CommentIcon from '@material-ui/icons/Comment';
import ReportIcon from '@material-ui/icons/Report';
import PublicIcon from '@material-ui/icons/Public';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { useHistory } from 'react-router-dom';
import HourglassEmptyIcon from '@material-ui/icons/HourglassEmpty';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Fade from '@material-ui/core/Fade';
import { withStyles } from '@material-ui/core/styles';
import { TutorialTooltip } from './TutorialTooltips';
import { getVideoIdFromURL, YoutubePlayer } from '../../utils';
import { TournesolAPI } from '../../api';

const StyledMenu = withStyles({
  paper: {
    border: '1px solid #d3d4d5',
  },
})((props) => (
  <Menu
    elevation={0}
    getContentAnchorEl={null}
    anchorOrigin={{
      vertical: 'bottom',
      horizontal: 'center',
    }}
    transformOrigin={{
      vertical: 'top',
      horizontal: 'center',
    }}
    TransitionComponent={Fade}
  /* eslint-disable react/jsx-props-no-spreading */

    {...props}
  /* eslint-enable react/jsx-props-no-spreading */

  />
));

const StyledMenuItem = withStyles((theme) => ({
  root: {
    '&:focus': {
      backgroundColor: theme.palette.primary.main,
      '& .MuiListItemIcon-root, & .MuiListItemText-primary': {
        color: theme.palette.common.white,
      },
    },
  },
}))(MenuItem);

const PrivacyStatusSelector = ({ id, onPrivacyInfo = null }) => {
  const [privacyStatus, setPrivacyStatus] = React.useState('INIT');
  const [privacyStatusVideo, setPrivacyStatusVideo] = React.useState(null);

  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClickListItem = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const setPublic = (status) => {
    const api = new TournesolAPI.VideosApi();
    setPrivacyStatus('REQUESTED');
    api.setRatingPrivacy(status, id, () => {
      setPrivacyStatus('INIT');
    });
  };

  const handleMenuItemClick = (event, status) => {
    // setSelectedIndex(index);
    if (status !== privacyStatus) {
      setPublic(!status);
    }
    setAnchorEl(null);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  if (privacyStatus === 'INIT') {
    setPrivacyStatus('REQUESTED');
    setPrivacyStatusVideo(id);
    const api = new TournesolAPI.VideosApi();
    api.myRatingsArePrivate(id, (err, data) => {
      if (!err) {
        setPrivacyStatus(data.my_ratings_are_private);
        if (onPrivacyInfo !== null) {
          onPrivacyInfo(data.my_ratings_are_private);
        }
      } else {
        setPrivacyStatus('ERROR');
      }
      setPrivacyStatusVideo(id);
    });
  }

  if (privacyStatusVideo !== id && privacyStatus !== 'REQUESTED') {
    setPrivacyStatus('INIT');
  }

  // note the STRING indices
  const nameByPrivacy = { true: 'Only me', false: 'Everyone' };
  const iconByPrivacy = { true: <FontAwesomeIcon icon={['fa', 'user-secret']} />,
    false: <PublicIcon /> };

  if (privacyStatus !== true && privacyStatus !== false) {
    return (
      <Tooltip
        title="Please wait..."
        aria-label="add"
      >
        <IconButton
          className="class_privacy_loading"
          aria-label="load"
        >
          <HourglassEmptyIcon />
        </IconButton>
      </Tooltip>
    );
  }

  return (
    <span>
      <Tooltip
        title={`Video visibility: ${nameByPrivacy[privacyStatus.toString()]}`}
        aria-label="add"
      >
        <IconButton
          id={`id_open_privacy_menu_${id}`}
          aria-label="load"
          onClick={handleClickListItem}
        >
          {privacyStatus === true && (
            <div id={`id_video_${id}_private`} />
          )}
          {privacyStatus === false && (
          <div id={`id_video_${id}_public`} />
          )}
          {iconByPrivacy[privacyStatus.toString()]}
        </IconButton>
      </Tooltip>
      <StyledMenu
        id="lock-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        {Object.keys(iconByPrivacy)
          .map((status) => status === 'true')
          .map((status) => (
            <StyledMenuItem
              key={status}
              disabled={false}
              selected={status === privacyStatus}
              onClick={(event) => handleMenuItemClick(event, status)}
              id={`menu_set_private_${status}_${id}`}
            >
              <ListItemIcon>
                {iconByPrivacy[status.toString()]}
              </ListItemIcon>
              <ListItemText primary={nameByPrivacy[status.toString()]} />

            </StyledMenuItem>
          ))}
      </StyledMenu>
    </span>
  );
};

export default ({
  id,
  setId,
  getNewId,
  showPlayer = true,
  showReport = true,
  showControls = true,
  showCommentButton = true,
  openComments,
  tourIndex,
}) => {
  const history = useHistory();

  const handleChange = (e) => {
    const videoId = getVideoIdFromURL(e.target.value);
    if (videoId) setId(videoId);
    else setId(e.target.value.replace(/[^A-Za-z0-9-_]/g, '').substring(0, 20));
  };

  return (
    <div>
      {showPlayer && (
        <div
          style={{
            height: '238px',
            width: '420px',
            background: '#000',
          }}
        >
          <YoutubePlayer videoId={id} light width={420} height={240} lightAutoplay={0} />
        </div>
      )}
      {showControls && (
      <div style={{ marginTop: '12px' }}>
        <TutorialTooltip
          i={tourIndex === 0 || tourIndex === 1 ? tourIndex : -2}
          tourIndex={tourIndex}
        >
          <TextField
            label="Video Id"
            variant="outlined"
            className="video_id_text_field"
            placeholder="Paste URL or Video ID"
            style={{ width: '13em' }}
            value={id}
            onChange={handleChange}
          />
        </TutorialTooltip>
        <TutorialTooltip i={7} tourIndex={tourIndex}>
          <Tooltip title="New Video" aria-label="add">
            <IconButton
              className="new_video_button"
              aria-label="load"
              onClick={() => getNewId()}
            >
              <ReplayIcon />
            </IconButton>
          </Tooltip>
        </TutorialTooltip>
        {showCommentButton && (
          <TutorialTooltip i={5} tourIndex={tourIndex}>
            <Tooltip title="Comments" aria-label="add">
              <IconButton aria-label="load" onClick={openComments}>
                <CommentIcon />
              </IconButton>
            </Tooltip>
          </TutorialTooltip>
        )}
        {showReport && (
          <TutorialTooltip i={6} tourIndex={tourIndex}>
            <Tooltip title="Report video" aria-label="add">
              <IconButton
                aria-label="load"
                onClick={() => history.push(`/report/${id}`)}
              >
                <ReportIcon />
              </IconButton>
            </Tooltip>
          </TutorialTooltip>
        )}
        <PrivacyStatusSelector id={id} />
      </div>
      )}
    </div>
  );
};
