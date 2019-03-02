import axios from "axios"

export default class ApiClient {
  ApiTokenLocalStorageKey = "api_token";

  constructor(hostname, port) {
    this.endpoint = `http://${hostname}:${port}`;
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.ApiTokenLocalStorageKey);
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
      localStorage.setItem(this.ApiTokenLocalStorageKey, token)
    })
  }

  setAuth(token) {
    this.isAuth = true;
    this.axios.defaults.headers['Authorization'] = 'Bearer ' + token;
  }

  hasAuth() {
    return this.isAuth;
  }

  upsertBoard(boardId, q, limit, sort, projections) {
    const data = {q, projections};
    if (limit) {
      data["limit"] = limit
    }
    if (sort) {
      data["sort"] = sort
    }
    return this.axios.post(`${this.endpoint}/board/${boardId}`, data)
  }

  getBoards() {
    return this.axios.get(`${this.endpoint}/boards`).then(response => response.data)
  }

  getBoard(boardId) {
    return this.axios.get(`${this.endpoint}/board/${boardId}`).then(response => response.data)
  }

  swapBoards(boardId, anotherBoardId) {
    return this.axios.post(`${this.endpoint}/boards/swap/${boardId}/${anotherBoardId}`)
  }

  removeBoard(boardId) {
    return this.axios.delete(`${this.endpoint}/board/${boardId}`)
  }
}
