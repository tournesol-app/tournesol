import { ensureVideoExistOrCreate } from 'src/utils/video';
import { UsersService } from 'src/services/openapi';
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

  await ensureVideoExistOrCreate(video_id);

  return UsersService.usersVideoRateLaterCreate(login_state.username, {
    video: { video_id },
  });
};

export const deleteFromRateLaterList = async (
  login_state: LoginState,
  { video_id }: { video_id: string }
) => {
  if (!login_state.username) {
    throw Error('username is missing');
  }
  OpenAPI.TOKEN = login_state.access_token;

  return UsersService.usersVideoRateLaterDestroy(
    login_state.username,
    video_id
  );
};
