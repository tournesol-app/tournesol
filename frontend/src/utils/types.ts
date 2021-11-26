import { Video, VideoSerializerWithCriteria } from 'src/services/openapi';

export type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

export interface JSONObject {
  [k: string]: JSONValue;
}

export type ActionList = Array<
  ({ videoId }: { videoId: string }) => JSX.Element | null
>;

export type VideoObject = Video | VideoSerializerWithCriteria;
