import axios from "axios"

export default class ApiClient {
  TokenLocalStorageKey = "accessToken";

  constructor() {
    this.endpoint = process.env.REACT_APP_SERVER_URL;
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.TokenLocalStorageKey);
    if (token) {
      this.setAuth(token)
    }
  }

  async auth(username, password) {
    return this.axios.post(`${this.endpoint}/auth`, {
      username, password
    }).then(response => {
      const token = response.data['access_token'];
      if (!token) {
        throw new Error(`No access_token in ${response.data}`)
      }
      this.setAuth(token);
      localStorage.setItem(this.TokenLocalStorageKey, token)
    })
  }

  setAuth(token) {
    this.isAuth = true;
    this.axios = axios.create({
      headers: {
        "Authorization": 'Bearer ' + token
      }
    })
  }

  hasAuth() {
    return this.isAuth;
  }

  async upsertBoard(boardId, q, limit, sort, projections) {
    const data = {q, projections};
    if (limit) {
      data["limit"] = limit
    }
    if (sort) {
      data["sort"] = sort
    }
    return this.axios.post(`${this.endpoint}/apiInternal/board/${boardId}`, data)
  }

  async getBoards() {
    return this.axios.get(`${this.endpoint}/apiInternal/boards`).then(response => response.data)
  }

  async getBoard(boardId) {
    return this.axios.get(`${this.endpoint}/apiInternal/board/${boardId}`).then(response => response.data)
  }

  async swapBoards(boardId, anotherBoardId) {
    return this.axios.post(`${this.endpoint}/apiInternal/boards/swap/${boardId}/${anotherBoardId}`)
  }

  async removeBoard(boardId) {
    return this.axios.delete(`${this.endpoint}/apiInternal/board/${boardId}`)
  }

  async rpcCall(verb, metadata, payload) {
    const response = await this.axios.post(`${this.endpoint}/apiInternal/rpc`, {
      verb: verb,
      metadata: metadata,
      payload: payload
    });
    if (!response.data) {
      throw new Error("No data")
    }
    if (!response.data["status"]) {
      throw new Error("No status in data")
    }
    if (response.data["status"] !== "ok") {
      throw new Error(`Status is ${response.data["status"]}`)
    }
    return response.data["payload"]
  }

  async rpcQuery(q, limit, sort) {
    const payload = {q};
    if (limit) {
      payload["limit"] = limit
    }
    if (sort) {
      payload["sort"] = sort
    }
    return this.rpcCall("query", {}, payload)
  }

  async rpcUpdateOne(filter_q, update_doc) {
    return this.rpcCall("update_one", {}, {filter_q, update_doc})
  }

  async rpcQueryNearestHammingNeighbors(q, binary_string_key, from_binary_string, max_distance) {
    return this.rpcCall("query_nearest_hamming_neighbors", {}, {
      q, binary_string_key, from_binary_string, max_distance
    })
  }

  async getWorkers() {
    return this.axios.get(`${this.endpoint}/apiInternal/worker`)
  }

  async addWorker(module, className, args, intervalSeconds) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker`, {
      "module": module,
      "class_name": className,
      "args": args,
      "interval_seconds": intervalSeconds
    })
  }

  async removeWorker(workerId) {
    return this.axios.delete(`${this.endpoint}/apiInternal/worker/${workerId}`)
  }

  async updateWorkerIntervalSeconds(workerId, intervalSeconds) {
    return this.axios.put(`${this.endpoint}/apiInternal/worker/${workerId}/intervalSeconds/${intervalSeconds}`)
  }

  async getWorkerMetadata(workerId) {
    return this.axios.get(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`)
  }

  async setWorkerMetadata(workerId, metadata) {
    return this.axios.post(`${this.endpoint}/apiInternal/worker/${workerId}/metadata`, metadata)
  }
}
