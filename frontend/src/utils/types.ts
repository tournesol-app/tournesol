import React from 'react';
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
  (({ uid }: { uid: string }) => JSX.Element) | React.ReactNode
>;

export type VideoObject = Video | VideoSerializerWithCriteria;
