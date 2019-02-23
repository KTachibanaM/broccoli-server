import axios from "axios"

export default class WorkerManagerClient {
  constructor(hostname, port) {
    this.apiEndpoint = `http://${hostname}:${port}/api`
  }

  async getWorkers() {
    return axios.get(`${this.apiEndpoint}/worker`)
  }

  async addWorker(module, className, args, intervalSeconds) {
    return axios.post(`${this.apiEndpoint}/worker`, {
      "module": module,
      "class_name": className,
      "args": args,
      "interval_seconds": intervalSeconds
    })
  }

  async removeWorker(workerId) {
    return axios.delete(`${this.apiEndpoint}/worker/${workerId}`)
  }

  async updateWorkerIntervalSeconds(workerId, intervalSeconds) {
    return axios.put(`${this.apiEndpoint}/worker/${workerId}/intervalSeconds/${intervalSeconds}`)
  }

  async getWorkerMetadata(workerId) {
    return axios.get(`${this.apiEndpoint}/worker/${workerId}/metadata`)
  }

  async setWorkerMetadata(workerId, metadata) {
    return axios.post(`${this.apiEndpoint}/worker/${workerId}/metadata`, metadata)
  }
}
