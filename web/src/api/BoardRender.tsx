import {ButtonData} from "../components/modView/Button";
import {ImageListData} from "../components/modView/ImageList";
import {TextData} from "../components/modView/Text";
import {VideoData} from "../components/modView/Video";
import BoardProjection from "./BoardProjection";

export type RenderTypes = "button" | "image" | "image_list" | "text" | "video";

export const ActionableRenderTypes = new Set(["button"]);

export type RenderDataTypes = ButtonData | ImageData | ImageListData | TextData | VideoData;

export interface Row {
  raw_document: object;
  renders: {
    [key: string]: {
      type: RenderTypes,
      data: RenderDataTypes,
      callback_id?: string,
    },
  };
}

export default interface BoardRender {
  board_query: {
    projections: BoardProjection[],
    q: string,
    sort?: object,
    limit?: number,
  };
  count_without_limit: number;
  payload: Row[];
}
