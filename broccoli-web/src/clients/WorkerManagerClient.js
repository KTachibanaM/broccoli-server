import axios from "axios"

export default class WorkerManagerClient {
  constructor(hostname, port) {
    this.apiEndpoint = `http://${hostname}:${port}/api`
  }

  async getWorkers() {
    return axios.get(`${this.apiEndpoint}/worker`)
  }

  async addWorker(module, className, args, globalArgs, intervalSeconds) {
    return axios.post(`${this.apiEndpoint}/worker`, {
      "module": module,
      "class_name": className,
      "args": args,
      "global_args": globalArgs,
      "interval_seconds": intervalSeconds
    })
  }

  async removeWorker(workerId) {
    return axios.delete(`${this.apiEndpoint}/worker/${workerId}`)
  }

  async updateWorkerIntervalSeconds(workerId, intervalSeconds) {
    return axios.put(`${this.apiEndpoint}/worker/${workerId}/intervalSeconds/${intervalSeconds}`)
  }

  async getWorkerEvents(workerId, fromMilliseconds, toMilliseconds, limit) {
    return axios.get(`${this.apiEndpoint}/worker/${workerId}/events`, {
      "params": {
        "from_ms": fromMilliseconds,
        "to_ms": toMilliseconds,
        "limit": limit
      }
    })
  }
}
