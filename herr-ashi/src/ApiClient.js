import axios from "axios"

export default class ApiClient {
  constructor(hostname, port, s3Hostname, s3Port, s3BucketName) {
    this.apiEndpoint = `http://${hostname}:${port}/api`;
    this.s3Endpoint = `http://${s3Hostname}:${s3Port}/${s3BucketName}`;

    this.handleListResponse = this.handleListResponse.bind(this)
  }

  nextPage(fromTimestamp) {
    let url = this.apiEndpoint;
    if (fromTimestamp) {
      url = url + `?from=${fromTimestamp}`
    }
    return axios.get(url)
      .then(this.handleListResponse)
  }

  prevPage(toTimestamp) {
    let url = this.apiEndpoint;
    if (toTimestamp) {
      url = url + `?to=${toTimestamp}`
    }
    return axios.get(url)
      .then(this.handleListResponse)
  }

  random() {
    return fetch(`${this.apiEndpoint}/random`)
      .then(response => response.json())
      .then(item => {
        return {
          ...item,
          "s3_image_link": `${this.s3Endpoint}/${item["s3_image_id"]}`
        }
      })
  }

  handleListResponse(response) {
    const data = response.data;
    if (data.length === 0) {
      return null
    }
    return data.map(item => {
      return {
        ...item,
        "s3_image_link": `${this.s3Endpoint}/${item["s3_image_id"]}`
      }
    })
  }
}
