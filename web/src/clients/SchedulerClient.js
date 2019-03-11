import axios from "axios"

export default class SchedulerClient {
  WorkerManagerTokenLocalStorageKey = "worker_manager_token";

  constructor(hostname, port) {
    this.endpoint = `http://${hostname}:${port}`;
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.WorkerManagerTokenLocalStorageKey);
    if (token) {
      this.setAuth(token)
    }
  }

  auth(username, password) {
    return this.axios.post(`${this.endpoint}/auth`, {
      username, password
    }).then(response => {
      const token = response.data['access_token'];
      if (!token) {
        throw new Error(`No access_token in ${response.data}`)
      }
      this.setAuth(token);
      localStorage.setItem(this.WorkerManagerTokenLocalStorageKey, token)
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
