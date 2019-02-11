import axios from "axios"

export default class ApiClient {
  constructor(hostname, port) {
    this.endpoint = `http://${hostname}:${port}`;
    this.apiConfigEndpoint = `${this.endpoint}/apiConfig`
  }

  getApiConfig() {
    return axios.get(this.apiConfigEndpoint)
  }

  setApiConfig(q, fields) {
    return axios.post(this.apiConfigEndpoint, {q, fields})
  }

  upsertBoard(boardId, q) {
    return axios.post(`${this.endpoint}/board/${boardId}`, q)
  }

  getBoards() {
    return axios.get(`${this.endpoint}/boards`)
  }

  swapBoards(boardId, anotherBoardId) {
    return axios.post(`${this.endpoint}/boards/swap/${boardId}/${anotherBoardId}`)
  }

  removeBoard(boardId) {
    return axios.delete(`${this.endpoint}/board/${boardId}`)
  }

  getBoard(boardId) {
    return axios.get(`${this.endpoint}/board/${boardId}`)
  }
}
