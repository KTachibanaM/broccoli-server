import axios from "axios"

export default class ApiClient {
  constructor(hostname, port) {
    this.apiConfigEndpoint = `http://${hostname}:${port}/apiConfig`
  }

  getApiConfig() {
    return axios.get(this.apiConfigEndpoint)
  }

  setApiConfig(q, fields) {
    return axios.post(this.apiConfigEndpoint, {q, fields})
  }
}
