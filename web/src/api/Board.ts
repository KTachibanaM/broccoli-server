import BoardProjection from "./BoardProjection";

export default interface Board {
  q: object;
  limit?: number;
  sort?: object;
  projections: BoardProjection[];
}
