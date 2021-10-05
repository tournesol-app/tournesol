import { UsersService } from '../../services/openapi';
import { OpenAPI } from '../../services/openapi/core/OpenAPI';

const api_url = process.env.REACT_APP_API_URL;

export const fetchComparisons = (
  access_token: string,
  limit: number,
  offset: number
) => {
  OpenAPI.TOKEN = access_token;
  OpenAPI.BASE = api_url ?? '';
  return UsersService.usersMeComparisonsList(limit, offset);
};
