/* eslint-disable react/destructuring-assignment, react/jsx-props-no-spreading */
import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';

import Typography from '@material-ui/core/Typography';
import { Editor } from 'react-draft-wysiwyg';
import { EditorState, convertToRaw, ContentState } from 'draft-js';
import 'react-draft-wysiwyg/dist/react-draft-wysiwyg.css';
import draftToHtml from 'draftjs-to-html';
import htmlToDraft from 'html-to-draftjs';

import { SUBMIT_EDITED_COMMENT, GET_COMMENTS, TournesolAPI } from '../../api';
import CommentHeader from './CommentHeader';
import CommentFooter from './CommentFooter';
import CommentEditor from './CommentEditor';
import EmailAddVerifyAlert from '../EmailAddVerifyAlert';
import getUsernames from './getUsernames';

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
    margin: '5px',
  },
  mainContainer: {
    paddingRight: '0px',
    margin: '4px',
    marginRight: '0px',
    paddingLeft: '4px',
    border: 'solid 1px #7777',
  },
  replyRow: {
    width: 'calc(100% - 16px)',
    marginLeft: '16px',
  },
  commentElement: {
    width: '100%',
  },
  title: {
    fontSize: 14,
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'row',
    margin: '4px',
  },
  toolbarDisabled: {
    display: 'None',
  },
}));

const toolbarOptions = {
  options: ['link', 'history', 'blockType'],
  blockType: { options: ['Blockquote'] },
};

const getEditorState = (data) => {
  const storedState = htmlToDraft(data);
  const { contentBlocks, entityMap } = storedState;
  const contentState = ContentState.createFromBlockArray(
    contentBlocks,
    entityMap,
  );

  // const contentState = convertFromRaw(storedState);
  const editorState = EditorState.createWithContent(contentState);
  return editorState;
};

const Comment = ({ comment, alternateColor, isRoot, reload }) => {
  const [commentText, setCommentText] = useState(comment.comment);
  const [isEditing, setIsEditing] = useState(false);
  const [isReplying, setIsReplying] = useState(false);

  const [allUsernames, setAllUsernames] = React.useState([]);
  const [allUsernamesRequested, setAllUsernamesRequested] = React.useState(false);

  if (!allUsernamesRequested) {
    setAllUsernamesRequested(true);
    getUsernames('', setAllUsernames);
  }

  const classes = useStyles();

  const submitEditedComment = () => {
    setIsEditing(false);
    SUBMIT_EDITED_COMMENT(comment.id, commentText);
  };

  if (isRoot) {
    return (
      <div
        className={classes.mainContainer}
        style={{ background: alternateColor ? '#ddd' : '#fff' }}
      >
        <Editor
          readOnly
          mention={{ separator: ' ',
            trigger: '@',
            suggestions: allUsernames,
          }}

          editorState={getEditorState(commentText)}
          toolbarClassName={classes.toolbarDisabled}
        />
      </div>
    );
  }

  return (
    <div
      className={`${classes.mainContainer} comment_editor_cid_${comment.id}`}
      style={{ background: alternateColor ? '#ddd' : '#fff' }}
    >
      <CommentHeader comment={comment} reload={reload} />
      {isEditing ? (
        <div className={`comment_editor_cid_${comment.id}_editing`} />
      ) : (
        <div className={`comment_editor_cid_${comment.id}_not_editing`} />
      )}
      <Editor
        onEditorStateChange={(s) => {
          setCommentText(draftToHtml(convertToRaw(s.getCurrentContent())));
        }}
        readOnly={!isEditing}
        defaultEditorState={getEditorState(commentText)}
        toolbar={toolbarOptions}
        toolbarClassName={!isEditing && classes.toolbarDisabled}
        style={isEditing && { background: '#dfd7' }}
        mention={{ separator: ' ',
          trigger: '@',
          suggestions: allUsernames,
        }}
      />
      <CommentFooter
        comment={comment}
        isReplying={isReplying}
        isEditing={isEditing}
        toggleReply={() => setIsReplying(!isReplying)}
        toggleNeedEditing={() => setIsEditing(!isEditing)}
        saveEdits={() => submitEditedComment(comment)}
      />
      {isReplying && (
        <CommentEditor
          videoId={comment.video}
          parentComment={comment.id}
          anonymousInitial={comment.anonymous}
          placeholder="Write your comment here"
          close={() => {
            reload();
            setIsReplying(false);
          }}
        />
      )}
      <CommentList
        classes={classes}
        videoId={comment.video}
        parentComment={comment.id}
        alternateColor={!alternateColor}
      />
    </div>
  );
};

const CommentList = (props) => {
  const { videoId, reload } = props;

  const [commentList, setCommentList] = useState(null);
  const [previousVideoId, setPreviousVideoId] = useState(videoId);
  const [shouldReload, setShouldReload] = useState(reload);

  if (
    commentList === null ||
    previousVideoId !== videoId ||
    shouldReload !== reload
  ) {
    setCommentList([]);
    setPreviousVideoId(videoId);
    setShouldReload(reload);
    if (videoId !== null && videoId !== '...') {
      GET_COMMENTS(videoId, (x) => setCommentList(x), props.parentComment);
    }
  }

  return (
    <>
      {commentList &&
        commentList.map((c) => (
          <Comment
            key={c.id}
            comment={c}
            alternateColor={props.alternateColor}
            reload={() => setCommentList(null)}
          />
        ))}
    </>
  );
};

export default (props) => {
  const classes = useStyles();

  const [reload, setReload] = useState(null);
  const [commentAnonymously, setCommentAnonymously] = useState(null);
  const [informationRequested, setInformationRequested] = useState(false);

  if (!informationRequested) {
    setInformationRequested(true);
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationRetrieve(window.user_information_id,
      (err, resp) => {
        if (!err) {
          setCommentAnonymously(resp.comment_anonymously);
        }
      });
  }

  return (
    <>
      <EmailAddVerifyAlert />
      <Typography paragraph className={classes.title} color="textSecondary" gutterBottom>
        What do you think about this video? Please respect other users when
        writing comments.
      </Typography>
      {commentAnonymously !== null &&
        <CommentEditor
          videoId={props.videoId}
          close={setReload}
          anonymousInitial={commentAnonymously}
        />}
      <CommentList {...props} isRoot reload={reload} />
    </>
  );
};
