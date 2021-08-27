import { UsersService, VideoService } from 'src/services/openapi';
import { OpenAPI } from 'src/services/openapi/core/OpenAPI';
import { LoginState } from '../login/LoginState.model';

const api_url = process.env.REACT_APP_API_URL;
OpenAPI.BASE = api_url ?? '';

export const fetchRateLaterList = async (
  login_state: LoginState,
  { limit = 10, offset = 0 }
) => {
  if (!login_state.username) {
    throw Error('username is missing');
  }
  OpenAPI.TOKEN = login_state.access_token;
  return UsersService.usersVideoRateLaterList(
    login_state.username,
    limit,
    offset
  );
};

export const addToRateLaterList = async (
  login_state: LoginState,
  { video_id }: { video_id: string }
) => {
  if (!login_state.username) {
    throw Error('username is missing');
  }
  OpenAPI.TOKEN = login_state.access_token;

  // FIXME: should the video be created automatically?
  // And if so, shouldn't the backend be responsible for it?
  // It's currently impractical to check if the API error
  // is blocking or not.
  try {
    await VideoService.videoCreate({ video_id });
  } catch (err) {
    if (
      err.status === 400 &&
      err.body?.video_id?.[0]?.includes('already exists')
    ) {
      console.debug(
        'Video already exists in the database: API error can be ignored'
      );
    } else {
      throw err;
    }
  }

  return UsersService.usersVideoRateLaterCreate(login_state.username, {
    video: { video_id },
  });
};
