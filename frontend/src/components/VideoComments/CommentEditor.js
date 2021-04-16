import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';

import Button from '@material-ui/core/Button';
import { Editor } from 'react-draft-wysiwyg';
import { convertToRaw, EditorState } from 'draft-js';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import draftToHtml from 'draftjs-to-html';

import Checkbox from '@material-ui/core/Checkbox';
import Tooltip from '@material-ui/core/Tooltip';
import { SUBMIT_COMMENT } from '../../api';
import getUsernames from './getUsernames';

const useStyles = makeStyles(() => ({
  main: {
    background: '#dfd4',
    paddingRight: '0px',
    margin: '4px',
    marginRight: '0px',
    border: 'solid 1px #7777',
  },

}));

const toolbarOptions = {
  options: ['link', 'history', 'blockType'],
  blockType: { options: ['Blockquote'] },
};

export default (props) => {
  const { videoId, parentComment, features, anonymousInitial } = props;
  const [anonymous, setAnonymous] = React.useState(anonymousInitial);
  const [allUsernames, setAllUsernames] = React.useState([]);
  const [allUsernamesRequested, setAllUsernamesRequested] = React.useState(false);

  if (!allUsernamesRequested) {
    setAllUsernamesRequested(true);
    getUsernames('', setAllUsernames);
  }

  const classes = useStyles();

  const [editorState, setEditorState] = useState(() => {
    EditorState.createEmpty();
  });

  const handleCheckbox = (e) => {
    setAnonymous(e.target.checked);
  };

  const submitComment = () => {
    const comment = draftToHtml(convertToRaw(editorState.getCurrentContent()));
    SUBMIT_COMMENT(
      {
        ...features,
        comment,
        video: videoId,
        anonymous,
        parent_comment: parentComment || null,
      },
      () => props.close(comment),
      () => {},
    );
  };

  return (
    <div className={`${classes.main} comment_editor_${videoId}_${parentComment}`}>
      <Editor
        editorState={editorState}
        editorStyle={{ height: '100px' }}
        onMenu
        mention={{ separator: ' ',
          trigger: '@',
          suggestions: allUsernames,
        }}
        onEditorStateChange={setEditorState}
        toolbar={toolbarOptions}
      />
      <Button
        color="secondary"
        size="small"
        className={`${classes.commentElement} comment_editor_submit_${videoId}_${parentComment}`}
        onClick={() => {
          submitComment();
          setEditorState(EditorState.createEmpty());
        }}
      >
        SUBMIT
      </Button>
      <Tooltip title="Anonymous comment" aria-label="add">
        <Checkbox
          className={`anonymous_comment_checkbox_class_${videoId}_${parentComment}`}
          checked={anonymous}
          onChange={handleCheckbox}
          inputProps={{ 'aria-label': 'primary checkbox' }}
        />
      </Tooltip>
    </div>
  );
};
