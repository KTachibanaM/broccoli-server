import axios, { AxiosInstance } from "axios";
import Board from "./Board";
import BoardRender from "./BoardRender";
import JobRun from "./JobRun";

export default class ApiClient {
  private TokenLocalStorageKey = "accessToken";
  private readonly endpoint: string;
  private axios: AxiosInstance;
  private isAuth: boolean;

  constructor() {
    if (process.env.REACT_APP_ENDPOINT) {
      this.endpoint = process.env.REACT_APP_ENDPOINT;
    } else {
      this.endpoint = "";
    }
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.TokenLocalStorageKey);
    if (token) {
      this.setAuth(token);
    }
  }

  public async auth(username: string, password: string): Promise<boolean> {
    return this.axios.post(`${this.endpoint}/auth`, {
      username, password,
    }).then((response) => {
      const token = response.data.access_token;
      if (!token) {
        throw new Error(`No access_token in ${response.data}`);
      }
      this.setAuth(token);
      return true
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

  public async getBoards(): Promise<Board[]> {
    return this.axios.get(`${this.endpoint}/apiInternal/boards`).then((response) => response.data);
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

  public async getWorkerModules(): Promise<string[]> {
    return this.axios.get(`${this.endpoint}/apiInternal/worker/modules`).then(response => response.data)
  }

  public async addWorker(moduleName: string, args: object, intervalSeconds: number) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker`, {
      module_name: moduleName, args, interval_seconds: intervalSeconds,
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

  public async getWorkerMetadata(workerId): Promise<object> {
    return this.axios.get(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`).then(response => response.data)
  }

  public async setWorkerMetadata(workerId, metadata) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`, metadata);
  }

  public async getOneOffJobModules(): Promise<string[]>{
    return this.axios.get(`${this.endpoint}/apiInternal/oneOffJob/modules`).then(response => response.data)
  }

  public async runOneOffJob(moduleName: string, args: object): Promise<{status: string}> {
    return this.axios.post(`${this.endpoint}/apiInternal/oneOffJob/run`, {
      'module_name': moduleName,
      args
    }).then(response => response.data)
  }

  public async getOneOffJobRuns(): Promise<JobRun[]> {
    return this.axios.get(`${this.endpoint}/apiInternal/oneOffJob/run`).then(response => response.data)
  }

  public async getThreadCount(): Promise<number> {
    return this.axios.get(`${this.endpoint}/debug/threadCount`).then(response => response.data['thread_count'])
  }

  public async getInstanceTitle(): Promise<string> {
    return this.axios.get(`${this.endpoint}/apiInternal/instanceTitle`).then(response => response.data)
  }
}
