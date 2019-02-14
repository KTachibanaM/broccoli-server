import axios from "axios"

export default class ApiClient {
  constructor(hostname, port) {
    this.endpoint = `http://${hostname}:${port}`;
    this.apiConfigEndpoint = `${this.endpoint}/apiConfig`
  }

  getApiConfig() {
    return axios.get(this.apiConfigEndpoint)
  }

  setApiConfig(q, projection) {
    return axios.post(this.apiConfigEndpoint, {q, projection})
  }

  upsertBoard(boardId, q, limit, sort, projections) {
    const data = {q, projections};
    if (limit) {
      data["limit"] = limit
    }
    if (sort) {
      data["sort"] = sort
    }
    return axios.post(`${this.endpoint}/board/${boardId}`, data)
  }

  getBoards() {
    return axios.get(`${this.endpoint}/boards`).then(response => response.data)
  }

  getBoard(boardId) {
    return axios.get(`${this.endpoint}/board/${boardId}`).then(response => response.data)
  }

  swapBoards(boardId, anotherBoardId) {
    return axios.post(`${this.endpoint}/boards/swap/${boardId}/${anotherBoardId}`)
  }

  removeBoard(boardId) {
    return axios.delete(`${this.endpoint}/board/${boardId}`)
  }
}
