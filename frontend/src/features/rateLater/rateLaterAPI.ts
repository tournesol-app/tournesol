import { ensureVideoExistOrCreate } from 'src/utils/video';
import { UsersService } from 'src/services/openapi';
import { OpenAPI } from 'src/services/openapi/core/OpenAPI';
import { Video } from 'src/services/openapi';
import { LoginState } from '../login/LoginState.model';

const api_url = process.env.REACT_APP_API_URL;
OpenAPI.BASE = api_url ?? '';

export const fetchRateLaterList = async (
  login_state: LoginState,
  { limit = 20, offset = 0 }
) => {
  if (!login_state.username) {
    throw Error('username is missing');
  }
  OpenAPI.TOKEN = login_state.access_token;
  return UsersService.usersMeVideoRateLaterList(limit, offset);
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

  return UsersService.usersMeVideoRateLaterCreate({
    video: { video_id } as Video,
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

  return UsersService.usersMeVideoRateLaterDestroy(video_id);
};
