import axios from "axios"

export default class ContentClient {
  constructor(hostname, port) {
    this.apiEndpoint = `http://${hostname}:${port}/api`
  }

  async call(verb, metadata, payload) {
    const response = await axios.post(this.apiEndpoint, {
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

  async query(q) {
    return this.call("query", {}, q)
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
