import React from 'react';

import { makeStyles } from '@material-ui/core/styles';

import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import AccountBoxIcon from '@material-ui/icons/AccountBox';
import ThumbUpIcon from '@material-ui/icons/ThumbUp';
import ThumbDownIcon from '@material-ui/icons/ThumbDown';
import ReportProblemIcon from '@material-ui/icons/ReportProblem';
import AccessTimeIcon from '@material-ui/icons/AccessTime';
import Button from '@material-ui/core/Button';

import { useHistory } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { FLAG_COMMENT } from '../../api';
import FeatureSelector from './FeatureSelector';

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    flexDirection: 'row',
    overflowX: 'auto',
    overflowY: 'hidden',
    alignItems: 'center',
  },
  title: {
    fontSize: 14,
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'row',
    margin: '4px',
    flex: '0 0 auto',
  },
}));

const flagComment = (commentId, field, callback) => {
  FLAG_COMMENT(commentId, field, () => { callback(); });
};

export default (props) => {
  const classes = useStyles();
  const { comment, needEditing, updateCommentFeatures } = props;
  const history = useHistory();

  return (
    <div className={classes.root}>
      <Typography className={classes.title} color="textSecondary" gutterBottom>
        {comment.anonymous ? <FontAwesomeIcon icon={['fa', 'user-secret']} /> : <AccountBoxIcon />}
        {' '}
        {!comment.anonymous ? (
          <Button onClick={() => { history.push(`/user/${comment.username}`); }}>
            {comment.username}
          </Button>
        ) : (
          <span>
            {`anonymous ${comment.anonymized_username_id + 1}`}
            {comment.username === window.username ? ' (you)' : ''}
          </span>
        )}
        &nbsp;
        <AccessTimeIcon />
        &nbsp;
        {comment.datetime_add_ago}
        {comment.edited_m_added_s > 10 && ', edited'}
        &nbsp;&nbsp;
      </Typography>
      <IconButton
        aria-label="add"
        size="small"
        className={`vote_plus_comment_${comment.id}`}
        onClick={() => {
          flagComment(comment.id, 'votes_plus', props.reload);
        }}
      >
        <ThumbUpIcon />
      </IconButton>
      {comment.votes_plus}
      <IconButton
        aria-label="add"
        size="small"
        onClick={() => {
          flagComment(comment.id, 'votes_minus', props.reload);
        }}
      >
        <ThumbDownIcon />
      </IconButton>
      {comment.votes_minus}
      <IconButton
        aria-label="add"
        size="small"
        onClick={() => {
          flagComment(comment.id, 'red_flags', props.reload);
        }}
      >
        <ReportProblemIcon />
      </IconButton>
      {comment.red_flags}
      <FeatureSelector
        key={comment.id}
        show={comment}
        readOnly={!needEditing}
        onUpdate={updateCommentFeatures}
        minimalist
      />
    </div>
  );
};
