import axios, { AxiosInstance } from "axios";
import Board from "./Board";
import BoardProjection from "./BoardProjection";
import BoardRender from "./BoardRender";

export default class ApiClient {
  private TokenLocalStorageKey = "accessToken";
  private endpoint: string;
  private axios: AxiosInstance;
  private isAuth: boolean;

  constructor() {
    this.endpoint = "";
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.TokenLocalStorageKey);
    if (token) {
      this.setAuth(token);
    }
  }

  public async auth(username: string, password: string) {
    return this.axios.post(`${this.endpoint}/auth`, {
      username, password,
    }).then((response) => {
      const token = response.data.access_token;
      if (!token) {
        throw new Error(`No access_token in ${response.data}`);
      }
      this.setAuth(token);
    });
  }

  public setAuth(token: string) {
    localStorage.setItem(this.TokenLocalStorageKey, token);
    this.isAuth = true;
    this.axios = axios.create({
      headers: {
        Authorization: "Bearer " + token,
      },
    });
  }

  public unsetAuth() {
    localStorage.removeItem(this.TokenLocalStorageKey);
    this.isAuth = true;
    this.axios = axios.create();
  }

  public hasAuth(): boolean {
    return this.isAuth;
  }

  public async upsertBoard(
    boardId: string,
    q: object,
    limit: number | undefined,
    sort: object | undefined,
    projections: BoardProjection[],
  ): Promise<any> {
    const data: Board = {q, projections};
    if (limit) {
      data.limit = limit;
    }
    if (sort) {
      data.sort = sort;
    }
    return this.axios.post(`${this.endpoint}/apiInternal/board/${boardId}`, data);
  }

  public async getBoards(): Promise<Board[]> {
    return this.axios.get(`${this.endpoint}/apiInternal/boards`).then((response) => response.data);
  }

  public async getBoard(boardId: string): Promise<Board> {
    return this.axios.get(`${this.endpoint}/apiInternal/board/${boardId}`).then((response) => response.data);
  }

  public async swapBoards(boardId: string, anotherBoardId: string): Promise<any> {
    return this.axios.post(`${this.endpoint}/apiInternal/boards/swap/${boardId}/${anotherBoardId}`);
  }

  public async removeBoard(boardId: string): Promise<any> {
    return this.axios.delete(`${this.endpoint}/apiInternal/board/${boardId}`);
  }

  public async renderBoard(boardId: string): Promise<BoardRender> {
    return this.axios.get(`${this.endpoint}/apiInternal/renderBoard/${boardId}`).then((response) => response.data);
  }

  public async callbackBoard(callbackId: string, rawDocument: object): Promise<any> {
    return this.axios.post(`${this.endpoint}/apiInternal/callbackBoard/${callbackId}`, rawDocument);
  }

  public async getWorkers() {
    return this.axios.get(`${this.endpoint}/apiInternal/worker`).then(response => response.data)
  }

  public async addWorker(module, className, args, intervalSeconds) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker`, {
      module,
      class_name: className,
      args,
      interval_seconds: intervalSeconds,
    });
  }

  public async removeWorker(workerId) {
    return this.axios.delete(`${this.endpoint}/apiInternal/worker/${workerId}`);
  }

  public async updateWorkerIntervalSeconds(workerId, intervalSeconds) {
    return this.axios.put(`${this.endpoint}/apiInternal/worker/${workerId}/intervalSeconds/${intervalSeconds}`);
  }

  public async updateWorkerErrorResiliency(workerId: string, errorResiliency: number) {
    return this.axios.put(`${this.endpoint}/apiInternal/worker/${workerId}/errorResiliency/${errorResiliency}`);
  }

  public async updateWorkerExecutor(workerId: string, executor: string) {
    return this.axios.put(`${this.endpoint}/apiInternal/worker/${workerId}/executor/${executor}`);
  }

  public async getExecutors(): Promise<string[]>{
    return this.axios.get(`${this.endpoint}/apiInternal/executor`).then(response => response.data)
  }

  public async getWorkerMetadata(workerId) {
    return this.axios.get(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`);
  }

  public async setWorkerMetadata(workerId, metadata) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`, metadata);
  }
}
