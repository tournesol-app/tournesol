import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';

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

export default ({
  comment,
  isEditing,
  toggleReply,
  toggleNeedEditing,
  saveEdits,
}) => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Button size="small" onClick={toggleReply} className={`comment_${comment.id}_reply`}>
        reply {comment.children ? `(${comment.children})` : ''}
      </Button>
      {window.username === comment.username && !isEditing && (
        <Button size="small" onClick={toggleNeedEditing} className={`comment_${comment.id}_edit`}>
          edit
        </Button>
      )}
      {isEditing && (
        <Button size="small" onClick={saveEdits} className={`comment_${comment.id}_save_edits`}>
          save
        </Button>
      )}
    </div>
  );
};
