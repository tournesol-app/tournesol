import React from 'react';
import { SvgIconComponent } from '@mui/icons-material';
import {
  EntityNoExtraField,
  RelatedEntity,
  Video,
  VideoSerializerWithCriteria,
} from 'src/services/openapi';

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

export type RelatedEntityObject = EntityNoExtraField | RelatedEntity;
export type VideoObject = Video | VideoSerializerWithCriteria;

// a poll that can be displayed by <PollSelector>
export type SelectablePoll = {
  name: string;
  displayOrder: number;
  path: string;
  iconComponent: SvgIconComponent;
  withSearchBar: boolean;
  topBarBackground: string | null;
};
export type SelectablePolls = Array<SelectablePoll>;
