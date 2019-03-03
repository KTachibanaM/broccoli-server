import axios from "axios"

export default class ContentClient {
  ContentServerTokenLocalStorageKey = "content_server_token";

  constructor(hostname, port) {
    this.endpoint = `http://${hostname}:${port}`;
    this.apiEndpoint = `http://${hostname}:${port}/api`;
    this.axios = axios.create();
    this.isAuth = false;
    const token = localStorage.getItem(this.ContentServerTokenLocalStorageKey);
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
      localStorage.setItem(this.ContentServerTokenLocalStorageKey, token)
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

  async call(verb, metadata, payload) {
    const response = await this.axios.post(this.apiEndpoint, {
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

  async query(q, limit, sort) {
    const payload = {q};
    if (limit) {
      payload["limit"] = limit
    }
    if (sort) {
      payload["sort"] = sort
    }
    return this.call("query", {}, payload)
  }

  async schema() {
    return this.call("schema", {}, {})
  }

  async updateOne(filter_q, update_doc) {
    return this.call("update_one", {}, {filter_q, update_doc})
  }

  async queryNearestHammingNeighbors(q, binary_string_key, from_binary_string, max_distance) {
    return this.call("query_nearest_hamming_neighbors", {}, {
      q, binary_string_key, from_binary_string, max_distance
    })
  }
}
